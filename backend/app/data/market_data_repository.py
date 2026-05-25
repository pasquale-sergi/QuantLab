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
