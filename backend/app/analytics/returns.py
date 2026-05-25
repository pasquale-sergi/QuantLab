from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.db.models import Price


@dataclass(frozen=True)
class DailyReturnRow:
    date: date
    symbol: str
    close: Decimal
    daily_return: float | None


def compute_daily_simple_returns(symbol: str, prices: list[Price]) -> list[DailyReturnRow]:
    rows: list[DailyReturnRow] = []
    previous_close: Decimal | None = None

    for price in prices:
        daily_return: float | None = None
        if previous_close is not None and previous_close != Decimal("0"):
            daily_return = float((price.close / previous_close) - Decimal("1"))

        rows.append(
            DailyReturnRow(
                date=price.date,
                symbol=symbol,
                close=price.close,
                daily_return=daily_return,
            )
        )
        previous_close = price.close

    return rows
