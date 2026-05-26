from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.data.market_data_repository import MarketDataRepository, PriceDataNotFoundError, SymbolNotFoundError
from app.db.session import get_db
from app.engine.backtester import InvalidBacktestParameterError, run_moving_average_crossover_backtest


router = APIRouter(prefix="/backtests", tags=["backtests"])


class MovingAverageParametersRequest(BaseModel):
    short_window: int = Field(gt=0)
    long_window: int = Field(gt=0)


class BacktestRunRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    start_date: date
    end_date: date
    strategy: str
    parameters: MovingAverageParametersRequest
    initial_cash: float = Field(gt=0)
    transaction_cost_bps: float = Field(ge=0)


class BacktestMetricsResponse(BaseModel):
    total_return: float | None
    annualized_return: float | None
    volatility: float | None
    annualized_volatility: float | None
    sharpe_ratio: float | None
    max_drawdown: float | None
    historical_var_95: float | None
    expected_shortfall_95: float | None


class TradeResponse(BaseModel):
    date: date
    symbol: str
    side: str
    price: float
    shares: int
    gross_value: float
    transaction_cost: float
    cash_after_trade: float


class EquityPointResponse(BaseModel):
    date: date
    cash: float
    shares: int
    close_price: float
    position_value: float
    total_equity: float
    daily_return: float | None


class BacktestRunResponse(BaseModel):
    symbol: str
    strategy: str
    parameters: dict[str, int]
    initial_cash: float
    final_equity: float
    metrics: BacktestMetricsResponse
    trades: list[TradeResponse]
    equity_curve: list[EquityPointResponse]


@router.post("/run", response_model=BacktestRunResponse)
def run_backtest(payload: BacktestRunRequest, db: Session = Depends(get_db)) -> BacktestRunResponse:
    if payload.start_date > payload.end_date:
        raise HTTPException(status_code=400, detail="start_date must be <= end_date")
    if payload.strategy != "moving_average_crossover":
        raise HTTPException(status_code=400, detail="Only 'moving_average_crossover' strategy is supported")

    repository = MarketDataRepository(db)
    normalized_symbol = payload.symbol.upper().strip()

    try:
        prices = repository.fetch_prices_for_symbol(normalized_symbol, payload.start_date, payload.end_date)
    except SymbolNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PriceDataNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    try:
        result = run_moving_average_crossover_backtest(
            symbol=normalized_symbol,
            prices=prices,
            short_window=payload.parameters.short_window,
            long_window=payload.parameters.long_window,
            initial_cash=payload.initial_cash,
            transaction_cost_bps=payload.transaction_cost_bps,
        )
    except InvalidBacktestParameterError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return BacktestRunResponse(
        symbol=result.symbol,
        strategy=result.strategy,
        parameters=result.parameters,
        initial_cash=result.initial_cash,
        final_equity=result.final_equity,
        metrics=BacktestMetricsResponse(
            total_return=result.metrics.total_return,
            annualized_return=result.metrics.annualized_return,
            volatility=result.metrics.volatility,
            annualized_volatility=result.metrics.annualized_volatility,
            sharpe_ratio=result.metrics.sharpe_ratio,
            max_drawdown=result.metrics.max_drawdown,
            historical_var_95=result.metrics.historical_var_95,
            expected_shortfall_95=result.metrics.expected_shortfall_95,
        ),
        trades=[
            TradeResponse(
                date=trade.date,
                symbol=trade.symbol,
                side=trade.side,
                price=trade.price,
                shares=trade.shares,
                gross_value=trade.gross_value,
                transaction_cost=trade.transaction_cost,
                cash_after_trade=trade.cash_after_trade,
            )
            for trade in result.trades
        ],
        equity_curve=[
            EquityPointResponse(
                date=point.date,
                cash=point.cash,
                shares=point.shares,
                close_price=point.close_price,
                position_value=point.position_value,
                total_equity=point.total_equity,
                daily_return=point.daily_return,
            )
            for point in result.equity_curve
        ],
    )
