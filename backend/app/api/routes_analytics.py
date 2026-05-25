from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.analytics.metrics import (
    annualized_return,
    annualized_volatility,
    drawdown_series,
    expected_shortfall_95,
    historical_var_95,
    max_drawdown,
    sharpe_ratio,
    total_return,
    volatility,
)
from app.analytics.returns import compute_daily_simple_returns
from app.data.market_data_repository import MarketDataRepository, PriceDataNotFoundError, SymbolNotFoundError
from app.db.session import get_db


router = APIRouter(prefix="/analytics", tags=["analytics"])


class MetricsPayload(BaseModel):
    total_return: float | None
    annualized_return: float | None
    volatility: float | None
    annualized_volatility: float | None
    sharpe_ratio: float | None
    max_drawdown: float | None
    historical_var_95: float | None
    expected_shortfall_95: float | None


class SymbolMetricsResponse(BaseModel):
    symbol: str
    start_date: date
    end_date: date
    metrics: MetricsPayload


class DrawdownRowResponse(BaseModel):
    date: date
    equity: float
    drawdown: float


class SymbolDrawdownResponse(BaseModel):
    symbol: str
    start_date: date
    end_date: date
    rows: list[DrawdownRowResponse]


@router.get("/{symbol}/metrics", response_model=SymbolMetricsResponse)
def get_symbol_metrics(symbol: str, start_date: date, end_date: date, db: Session = Depends(get_db)) -> SymbolMetricsResponse:
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be <= end_date")

    normalized_symbol = symbol.upper().strip()
    repository = MarketDataRepository(db)
    try:
        prices = repository.fetch_prices_for_symbol(normalized_symbol, start_date, end_date)
    except SymbolNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PriceDataNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return_rows = compute_daily_simple_returns(normalized_symbol, prices)
    returns = [row.daily_return for row in return_rows]
    returns_with_dates = [(row.date, row.daily_return) for row in return_rows]

    payload = MetricsPayload(
        total_return=total_return(returns),
        annualized_return=annualized_return(returns),
        volatility=volatility(returns),
        annualized_volatility=annualized_volatility(returns),
        sharpe_ratio=sharpe_ratio(returns),
        max_drawdown=max_drawdown(returns_with_dates),
        historical_var_95=historical_var_95(returns),
        expected_shortfall_95=expected_shortfall_95(returns),
    )

    return SymbolMetricsResponse(
        symbol=normalized_symbol,
        start_date=start_date,
        end_date=end_date,
        metrics=payload,
    )


@router.get("/{symbol}/drawdown", response_model=SymbolDrawdownResponse)
def get_symbol_drawdown(symbol: str, start_date: date, end_date: date, db: Session = Depends(get_db)) -> SymbolDrawdownResponse:
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be <= end_date")

    normalized_symbol = symbol.upper().strip()
    repository = MarketDataRepository(db)
    try:
        prices = repository.fetch_prices_for_symbol(normalized_symbol, start_date, end_date)
    except SymbolNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PriceDataNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return_rows = compute_daily_simple_returns(normalized_symbol, prices)
    rows = drawdown_series([(row.date, row.daily_return) for row in return_rows])

    return SymbolDrawdownResponse(
        symbol=normalized_symbol,
        start_date=start_date,
        end_date=end_date,
        rows=[
            DrawdownRowResponse(date=row.date, equity=row.equity, drawdown=row.drawdown)
            for row in rows
        ],
    )
