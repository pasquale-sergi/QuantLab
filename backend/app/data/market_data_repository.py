from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Asset, Price


@dataclass(frozen=True)
class PriceInput:
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


class SymbolNotFoundError(ValueError):
    def __init__(self, symbol: str) -> None:
        super().__init__(f"Symbol '{symbol}' does not exist")
        self.symbol = symbol


class PriceDataNotFoundError(ValueError):
    def __init__(self, symbol: str, start_date: date, end_date: date) -> None:
        super().__init__(f"No price data for symbol '{symbol}' between {start_date} and {end_date}")
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date


class MarketDataRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_create_asset(self, symbol: str, name: str | None = None) -> Asset:
        normalized_symbol = symbol.upper().strip()
        asset = self.session.scalar(select(Asset).where(Asset.symbol == normalized_symbol))
        if asset:
            if name and not asset.name:
                asset.name = name
                self.session.flush()
            return asset

        asset = Asset(symbol=normalized_symbol, name=name)
        self.session.add(asset)
        self.session.flush()
        return asset

    def upsert_prices(self, asset_id: int, rows: list[PriceInput]) -> tuple[int, int]:
        if not rows:
            return 0, 0

        dates = [row.date for row in rows]
        existing_prices = self.session.scalars(
            select(Price).where(Price.asset_id == asset_id, Price.date.in_(dates))
        ).all()
        existing_by_date = {entry.date: entry for entry in existing_prices}

        inserted = 0
        updated = 0
        for row in rows:
            existing = existing_by_date.get(row.date)
            if existing is None:
                self.session.add(
                    Price(
                        asset_id=asset_id,
                        date=row.date,
                        open=row.open,
                        high=row.high,
                        low=row.low,
                        close=row.close,
                        volume=row.volume,
                    )
                )
                inserted += 1
                continue

            existing.open = row.open
            existing.high = row.high
            existing.low = row.low
            existing.close = row.close
            existing.volume = row.volume
            updated += 1

        self.session.flush()
        return inserted, updated

    def fetch_prices_for_symbol(self, symbol: str, start_date: date, end_date: date) -> list[Price]:
        normalized_symbol = symbol.upper().strip()
        asset = self.session.scalar(select(Asset).where(Asset.symbol == normalized_symbol))
        if asset is None:
            raise SymbolNotFoundError(normalized_symbol)

        prices = self.session.scalars(
            select(Price)
            .where(
                Price.asset_id == asset.id,
                Price.date >= start_date,
                Price.date <= end_date,
            )
            .order_by(Price.date.asc())
        ).all()

        if not prices:
            raise PriceDataNotFoundError(normalized_symbol, start_date, end_date)

        return prices

    def fetch_prices_for_symbols(
        self,
        symbols: list[str],
        start_date: date,
        end_date: date,
    ) -> dict[str, list[Price]]:
        data_by_symbol: dict[str, list[Price]] = {}
        for symbol in symbols:
            normalized_symbol = symbol.upper().strip()
            data_by_symbol[normalized_symbol] = self.fetch_prices_for_symbol(
                normalized_symbol,
                start_date,
                end_date,
            )
        return data_by_symbol
