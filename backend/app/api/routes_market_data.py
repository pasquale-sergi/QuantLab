from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.analytics.returns import compute_daily_simple_returns
from app.data.market_data_ingestion import MarketDataIngestionService
from app.data.market_data_repository import MarketDataRepository, PriceDataNotFoundError, SymbolNotFoundError
from app.db.session import get_db


router = APIRouter(prefix="/market-data", tags=["market-data"])


class MarketDataIngestionRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    start_date: date
    end_date: date


class MarketDataIngestionResponse(BaseModel):
    symbol: str
    rows_inserted: int
    start_date: date
    end_date: date


class ReturnRowResponse(BaseModel):
    date: date
    close: float
    daily_return: float | None


class SymbolReturnsResponse(BaseModel):
    symbol: str
    start_date: date
    end_date: date
    rows: list[ReturnRowResponse]


class MultiSymbolReturnsResponse(BaseModel):
    symbols: list[str]
    start_date: date
    end_date: date
    results: dict[str, list[ReturnRowResponse]]


class IngestedSymbolsResponse(BaseModel):
    symbols: list[str]


@router.post("/ingest", response_model=MarketDataIngestionResponse)
def ingest_market_data(payload: MarketDataIngestionRequest, db: Session = Depends(get_db)) -> MarketDataIngestionResponse:
    if payload.start_date > payload.end_date:
        raise HTTPException(status_code=400, detail="start_date must be <= end_date")

    service = MarketDataIngestionService(db)
    result = service.ingest(
        symbol=payload.symbol,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    return MarketDataIngestionResponse(
        symbol=result.symbol,
        rows_inserted=result.rows_inserted,
        start_date=result.start_date,
        end_date=result.end_date,
    )


@router.get("/symbols", response_model=IngestedSymbolsResponse)
def get_ingested_symbols(db: Session = Depends(get_db)) -> IngestedSymbolsResponse:
    repository = MarketDataRepository(db)
    symbols = repository.list_ingested_symbols()
    return IngestedSymbolsResponse(symbols=symbols)


@router.get("/{symbol}/returns", response_model=SymbolReturnsResponse)
def get_symbol_returns(symbol: str, start_date: date, end_date: date, db: Session = Depends(get_db)) -> SymbolReturnsResponse:
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be <= end_date")

    repository = MarketDataRepository(db)
    normalized_symbol = symbol.upper().strip()

    try:
        prices = repository.fetch_prices_for_symbol(normalized_symbol, start_date, end_date)
    except SymbolNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PriceDataNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    rows = compute_daily_simple_returns(normalized_symbol, prices)
    return SymbolReturnsResponse(
        symbol=normalized_symbol,
        start_date=start_date,
        end_date=end_date,
        rows=[
            ReturnRowResponse(
                date=row.date,
                close=float(row.close),
                daily_return=row.daily_return,
            )
            for row in rows
        ],
    )


@router.get("/returns", response_model=MultiSymbolReturnsResponse)
def get_multi_symbol_returns(
    symbols: str,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
) -> MultiSymbolReturnsResponse:
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be <= end_date")

    parsed_symbols = [symbol.strip().upper() for symbol in symbols.split(",") if symbol.strip()]
    if not parsed_symbols:
        raise HTTPException(status_code=400, detail="symbols query parameter is required")

    repository = MarketDataRepository(db)
    try:
        prices_by_symbol = repository.fetch_prices_for_symbols(parsed_symbols, start_date, end_date)
    except SymbolNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PriceDataNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    results: dict[str, list[ReturnRowResponse]] = {}
    for symbol_key, prices in prices_by_symbol.items():
        rows = compute_daily_simple_returns(symbol_key, prices)
        results[symbol_key] = [
            ReturnRowResponse(
                date=row.date,
                close=float(row.close),
                daily_return=row.daily_return,
            )
            for row in rows
        ]

    return MultiSymbolReturnsResponse(
        symbols=parsed_symbols,
        start_date=start_date,
        end_date=end_date,
        results=results,
    )
