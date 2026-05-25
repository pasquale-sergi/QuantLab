from datetime import UTC, date, datetime
from decimal import Decimal

from app.analytics.returns import compute_daily_simple_returns
from app.db.models import Price


def _price(price_date: date, close: str) -> Price:
    return Price(
        asset_id=1,
        date=price_date,
        open=Decimal(close),
        high=Decimal(close),
        low=Decimal(close),
        close=Decimal(close),
        volume=100,
        created_at=datetime.now(UTC),
    )


def test_return_calculation_correctness() -> None:
    prices = [
        _price(date(2024, 1, 2), "100"),
        _price(date(2024, 1, 3), "110"),
        _price(date(2024, 1, 4), "99"),
    ]

    rows = compute_daily_simple_returns("AAPL", prices)

    assert rows[1].daily_return == 0.1
    assert rows[2].daily_return == -0.1


def test_first_return_is_null() -> None:
    prices = [
        _price(date(2024, 1, 2), "100"),
        _price(date(2024, 1, 3), "101"),
    ]

    rows = compute_daily_simple_returns("AAPL", prices)

    assert rows[0].daily_return is None
