from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.data.market_data_ingestion import MarketDataIngestionService
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
