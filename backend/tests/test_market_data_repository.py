from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.data.market_data_repository import MarketDataRepository, PriceInput
from app.db.models import Asset, Price


def test_asset_creation(db_session) -> None:
    repo = MarketDataRepository(db_session)

    asset = repo.get_or_create_asset("AAPL", "Apple Inc.")
    db_session.commit()

    fetched = db_session.scalar(select(Asset).where(Asset.symbol == "AAPL"))
    assert fetched is not None
    assert fetched.id == asset.id
    assert fetched.name == "Apple Inc."


def test_price_insertion(db_session) -> None:
    repo = MarketDataRepository(db_session)
    asset = repo.get_or_create_asset("AAPL")

    inserted, updated = repo.upsert_prices(
        asset.id,
        [
            PriceInput(
                date=date(2024, 1, 2),
                open=Decimal("100.0"),
                high=Decimal("101.0"),
                low=Decimal("99.0"),
                close=Decimal("100.5"),
                volume=1000,
            )
        ],
    )
    db_session.commit()

    count = len(db_session.scalars(select(Price).where(Price.asset_id == asset.id)).all())
    assert inserted == 1
    assert updated == 0
    assert count == 1


def test_duplicate_prevention_updates_existing_row(db_session) -> None:
    repo = MarketDataRepository(db_session)
    asset = repo.get_or_create_asset("AAPL")

    first_payload = [
        PriceInput(
            date=date(2024, 1, 2),
            open=Decimal("100.0"),
            high=Decimal("101.0"),
            low=Decimal("99.0"),
            close=Decimal("100.5"),
            volume=1000,
        )
    ]
    repo.upsert_prices(asset.id, first_payload)

    second_payload = [
        PriceInput(
            date=date(2024, 1, 2),
            open=Decimal("110.0"),
            high=Decimal("111.0"),
            low=Decimal("109.0"),
            close=Decimal("110.5"),
            volume=2000,
        )
    ]
    inserted, updated = repo.upsert_prices(asset.id, second_payload)
    db_session.commit()

    rows = db_session.scalars(select(Price).where(Price.asset_id == asset.id)).all()
    assert inserted == 0
    assert updated == 1
    assert len(rows) == 1
    assert rows[0].close == Decimal("110.500000")
    assert rows[0].volume == 2000
