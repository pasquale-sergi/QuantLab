from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Callable

import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session

from app.data.market_data_repository import MarketDataRepository, PriceInput


@dataclass(frozen=True)
class IngestionResult:
    symbol: str
    rows_inserted: int
    start_date: date
    end_date: date


def _download_data(symbol: str, start_date: date, end_date: date) -> pd.DataFrame:
    return yf.download(symbol, start=start_date.isoformat(), end=end_date.isoformat(), progress=False)


class MarketDataIngestionService:
    def __init__(
        self,
        session: Session,
        repository: MarketDataRepository | None = None,
        download_func: Callable[[str, date, date], pd.DataFrame] = _download_data,
    ) -> None:
        self.session = session
        self.repository = repository or MarketDataRepository(session)
        self.download_func = download_func

    def ingest(self, symbol: str, start_date: date, end_date: date) -> IngestionResult:
        normalized_symbol = symbol.upper().strip()
        frame = self.download_func(normalized_symbol, start_date, end_date)

        if frame.empty:
            asset = self.repository.get_or_create_asset(normalized_symbol)
            self.session.commit()
            return IngestionResult(
                symbol=asset.symbol,
                rows_inserted=0,
                start_date=start_date,
                end_date=end_date,
            )

        ticker = yf.Ticker(normalized_symbol)
        asset_name = ticker.info.get("shortName") if ticker.info else None
        asset = self.repository.get_or_create_asset(normalized_symbol, asset_name)

        rows: list[PriceInput] = []
        for index, row in frame.iterrows():
            rows.append(
                PriceInput(
                    date=index.date(),
                    open=Decimal(str(float(row["Open"]))),
                    high=Decimal(str(float(row["High"]))),
                    low=Decimal(str(float(row["Low"]))),
                    close=Decimal(str(float(row["Close"]))),
                    volume=int(row["Volume"]),
                )
            )

        inserted, _ = self.repository.upsert_prices(asset.id, rows)
        self.session.commit()

        return IngestionResult(
            symbol=asset.symbol,
            rows_inserted=inserted,
            start_date=start_date,
            end_date=end_date,
        )
