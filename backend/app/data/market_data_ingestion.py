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


def _extract_value(row: pd.Series, field: str, symbol: str) -> Any:
    if field in row.index:
        value = row[field]
    elif (field, symbol) in row.index:
        value = row[(field, symbol)]
    elif (symbol, field) in row.index:
        value = row[(symbol, field)]
    else:
        matches: list[Any] = []
        for key in row.index:
            if not isinstance(key, tuple):
                continue
            if field not in key:
                continue
            if symbol in key:
                matches.append(row[key])
        if not matches:
            for key in row.index:
                if isinstance(key, tuple) and field in key:
                    matches.append(row[key])
        if not matches:
            raise KeyError(f"Field '{field}' was not found in downloaded market data")
        value = matches[0]

    if isinstance(value, pd.Series):
        if len(value) == 0:
            raise ValueError(f"Field '{field}' for symbol '{symbol}' is empty")
        value = value.iloc[0]

    return value


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
            open_value = _extract_value(row, "Open", normalized_symbol)
            high_value = _extract_value(row, "High", normalized_symbol)
            low_value = _extract_value(row, "Low", normalized_symbol)
            close_value = _extract_value(row, "Close", normalized_symbol)
            volume_value = _extract_value(row, "Volume", normalized_symbol)

            rows.append(
                PriceInput(
                    date=index.date(),
                    open=Decimal(str(float(open_value))),
                    high=Decimal(str(float(high_value))),
                    low=Decimal(str(float(low_value))),
                    close=Decimal(str(float(close_value))),
                    volume=int(volume_value),
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
