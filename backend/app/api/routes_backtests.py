from datetime import date
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.data.backtest_experiment_repository import (
    BacktestExperimentNotFoundError,
    BacktestExperimentRepository,
    BacktestExperimentsNotFoundError,
)
from app.data.market_data_repository import MarketDataRepository, PriceDataNotFoundError, SymbolNotFoundError
from app.db.session import get_db
from app.engine.backtester import InvalidBacktestParameterError, run_moving_average_crossover_backtest
from app.services.backtest_experiment_service import BacktestExperimentService, BacktestSaveRequest


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
    experiment_id: int
    symbol: str
    strategy: str
    parameters: dict[str, int]
    start_date: date
    end_date: date
    transaction_cost_bps: float
    initial_cash: float
    final_equity: float
    metrics: BacktestMetricsResponse
    trades: list[TradeResponse]
    equity_curve: list[EquityPointResponse]


class BacktestExperimentListItemResponse(BaseModel):
    experiment_id: int
    symbol: str
    strategy: str
    parameters: dict[str, int]
    start_date: date
    end_date: date
    initial_cash: float
    transaction_cost_bps: float
    final_equity: float
    created_at: datetime


class BacktestExperimentDetailResponse(BaseModel):
    experiment_id: int
    symbol: str
    strategy: str
    parameters: dict[str, int]
    start_date: date
    end_date: date
    initial_cash: float
    transaction_cost_bps: float
    final_equity: float
    created_at: datetime
    metrics: BacktestMetricsResponse
    trades: list[TradeResponse]
    equity_curve: list[EquityPointResponse]


class BacktestExperimentComparisonItemResponse(BaseModel):
    experiment_id: int
    symbol: str
    strategy: str
    parameters: dict[str, int]
    start_date: date
    end_date: date
    initial_cash: float
    final_equity: float
    total_return: float | None
    annualized_return: float | None
    annualized_volatility: float | None
    sharpe_ratio: float | None
    max_drawdown: float | None
    historical_var_95: float | None
    expected_shortfall_95: float | None


class BacktestExperimentComparisonResponse(BaseModel):
    experiments: list[BacktestExperimentComparisonItemResponse]


def _metrics_response(metrics) -> BacktestMetricsResponse:
    return BacktestMetricsResponse(
        total_return=metrics.total_return,
        annualized_return=metrics.annualized_return,
        volatility=metrics.volatility,
        annualized_volatility=metrics.annualized_volatility,
        sharpe_ratio=metrics.sharpe_ratio,
        max_drawdown=metrics.max_drawdown,
        historical_var_95=metrics.historical_var_95,
        expected_shortfall_95=metrics.expected_shortfall_95,
    )


def _trade_response_list(trades) -> list[TradeResponse]:
    return [
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
        for trade in trades
    ]


def _equity_response_list(equity_points) -> list[EquityPointResponse]:
    return [
        EquityPointResponse(
            date=point.date,
            cash=point.cash,
            shares=point.shares,
            close_price=point.close_price,
            position_value=point.position_value,
            total_equity=point.total_equity,
            daily_return=point.daily_return,
        )
        for point in equity_points
    ]


def _experiment_service(db: Session) -> BacktestExperimentService:
    return BacktestExperimentService(BacktestExperimentRepository(db))


def _parse_experiment_ids(ids: str) -> list[int]:
    raw_items = [item.strip() for item in ids.split(",") if item.strip()]
    if not raw_items:
        raise HTTPException(status_code=400, detail="ids query parameter must contain at least one ID")

    parsed_ids: list[int] = []
    for raw_item in raw_items:
        try:
            parsed_id = int(raw_item)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=f"Invalid experiment ID '{raw_item}'") from error

        if parsed_id <= 0:
            raise HTTPException(status_code=400, detail="Experiment IDs must be positive integers")

        if parsed_id not in parsed_ids:
            parsed_ids.append(parsed_id)

    return parsed_ids


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

    service = _experiment_service(db)
    saved_experiment = service.save_experiment(
        BacktestSaveRequest(
            symbol=normalized_symbol,
            strategy=result.strategy,
            parameters=result.parameters,
            start_date=payload.start_date,
            end_date=payload.end_date,
            initial_cash=payload.initial_cash,
            transaction_cost_bps=payload.transaction_cost_bps,
            result=result,
        )
    )

    return BacktestRunResponse(
        experiment_id=saved_experiment.id,
        symbol=result.symbol,
        strategy=result.strategy,
        parameters=result.parameters,
        start_date=payload.start_date,
        end_date=payload.end_date,
        transaction_cost_bps=payload.transaction_cost_bps,
        initial_cash=result.initial_cash,
        final_equity=result.final_equity,
        metrics=_metrics_response(result.metrics),
        trades=_trade_response_list(result.trades),
        equity_curve=_equity_response_list(result.equity_curve),
    )


@router.get("/experiments", response_model=list[BacktestExperimentListItemResponse])
def list_backtest_experiments(db: Session = Depends(get_db)) -> list[BacktestExperimentListItemResponse]:
    service = _experiment_service(db)
    experiments = service.list_experiments()

    return [
        BacktestExperimentListItemResponse(
            experiment_id=experiment.id,
            symbol=experiment.symbol,
            strategy=experiment.strategy,
            parameters=experiment.parameters,
            start_date=experiment.start_date,
            end_date=experiment.end_date,
            initial_cash=float(experiment.initial_cash),
            transaction_cost_bps=float(experiment.transaction_cost_bps),
            final_equity=float(experiment.final_equity),
            created_at=experiment.created_at,
        )
        for experiment in experiments
    ]


@router.get("/experiments/compare", response_model=BacktestExperimentComparisonResponse)
def compare_backtest_experiments(ids: str, db: Session = Depends(get_db)) -> BacktestExperimentComparisonResponse:
    experiment_ids = _parse_experiment_ids(ids)
    service = _experiment_service(db)

    try:
        experiments = service.compare_experiments(experiment_ids)
    except BacktestExperimentsNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return BacktestExperimentComparisonResponse(
        experiments=[
            BacktestExperimentComparisonItemResponse(
                experiment_id=experiment.id,
                symbol=experiment.symbol,
                strategy=experiment.strategy,
                parameters=experiment.parameters,
                start_date=experiment.start_date,
                end_date=experiment.end_date,
                initial_cash=float(experiment.initial_cash),
                final_equity=float(experiment.final_equity),
                total_return=float(experiment.metrics.total_return) if experiment.metrics and experiment.metrics.total_return is not None else None,
                annualized_return=float(experiment.metrics.annualized_return)
                if experiment.metrics and experiment.metrics.annualized_return is not None
                else None,
                annualized_volatility=float(experiment.metrics.annualized_volatility)
                if experiment.metrics and experiment.metrics.annualized_volatility is not None
                else None,
                sharpe_ratio=float(experiment.metrics.sharpe_ratio)
                if experiment.metrics and experiment.metrics.sharpe_ratio is not None
                else None,
                max_drawdown=float(experiment.metrics.max_drawdown)
                if experiment.metrics and experiment.metrics.max_drawdown is not None
                else None,
                historical_var_95=float(experiment.metrics.historical_var_95)
                if experiment.metrics and experiment.metrics.historical_var_95 is not None
                else None,
                expected_shortfall_95=float(experiment.metrics.expected_shortfall_95)
                if experiment.metrics and experiment.metrics.expected_shortfall_95 is not None
                else None,
            )
            for experiment in experiments
        ]
    )


@router.get("/experiments/{experiment_id}", response_model=BacktestExperimentDetailResponse)
def get_backtest_experiment(experiment_id: int, db: Session = Depends(get_db)) -> BacktestExperimentDetailResponse:
    service = _experiment_service(db)
    try:
        experiment = service.get_experiment(experiment_id)
    except BacktestExperimentNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    if experiment.metrics is None:
        raise HTTPException(status_code=500, detail="Experiment metrics are missing")

    return BacktestExperimentDetailResponse(
        experiment_id=experiment.id,
        symbol=experiment.symbol,
        strategy=experiment.strategy,
        parameters=experiment.parameters,
        start_date=experiment.start_date,
        end_date=experiment.end_date,
        initial_cash=float(experiment.initial_cash),
        transaction_cost_bps=float(experiment.transaction_cost_bps),
        final_equity=float(experiment.final_equity),
        created_at=experiment.created_at,
        metrics=_metrics_response(experiment.metrics),
        trades=_trade_response_list(experiment.trades),
        equity_curve=_equity_response_list(experiment.equity_curve),
    )
