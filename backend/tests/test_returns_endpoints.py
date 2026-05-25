from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.data.market_data_repository import MarketDataRepository, PriceDataNotFoundError, PriceInput, SymbolNotFoundError
from app.db.session import get_db
from app.main import app


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.router.on_startup.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _seed_prices(db_session) -> None:
    repo = MarketDataRepository(db_session)

    aapl = repo.get_or_create_asset("AAPL")
    msft = repo.get_or_create_asset("MSFT")

    repo.upsert_prices(
        aapl.id,
        [
            PriceInput(date=date(2024, 1, 2), open=Decimal("100"), high=Decimal("101"), low=Decimal("99"), close=Decimal("100"), volume=1000),
            PriceInput(date=date(2024, 1, 3), open=Decimal("110"), high=Decimal("111"), low=Decimal("109"), close=Decimal("110"), volume=1200),
        ],
    )

    repo.upsert_prices(
        msft.id,
        [
            PriceInput(date=date(2024, 1, 2), open=Decimal("200"), high=Decimal("201"), low=Decimal("199"), close=Decimal("200"), volume=1500),
            PriceInput(date=date(2024, 1, 3), open=Decimal("210"), high=Decimal("211"), low=Decimal("209"), close=Decimal("210"), volume=1600),
        ],
    )
    db_session.commit()


def test_missing_symbol_error(db_session) -> None:
    repo = MarketDataRepository(db_session)

    with pytest.raises(SymbolNotFoundError):
        repo.fetch_prices_for_symbol("DOESNOTEXIST", date(2024, 1, 1), date(2024, 1, 10))


def test_no_data_in_date_range_error(db_session) -> None:
    repo = MarketDataRepository(db_session)
    asset = repo.get_or_create_asset("AAPL")
    repo.upsert_prices(
        asset.id,
        [
            PriceInput(date=date(2024, 1, 2), open=Decimal("100"), high=Decimal("101"), low=Decimal("99"), close=Decimal("100"), volume=1000),
        ],
    )
    db_session.commit()

    with pytest.raises(PriceDataNotFoundError):
        repo.fetch_prices_for_symbol("AAPL", date(2024, 2, 1), date(2024, 2, 10))


def test_single_symbol_returns_endpoint(client, db_session) -> None:
    _seed_prices(db_session)

    response = client.get(
        "/market-data/AAPL/returns",
        params={"start_date": "2024-01-01", "end_date": "2024-01-10"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "AAPL"
    assert len(payload["rows"]) == 2
    assert payload["rows"][0]["daily_return"] is None
    assert payload["rows"][1]["daily_return"] == 0.1


def test_multi_symbol_returns_endpoint(client, db_session) -> None:
    _seed_prices(db_session)

    response = client.get(
        "/market-data/returns",
        params={
            "symbols": "AAPL,MSFT",
            "start_date": "2024-01-01",
            "end_date": "2024-01-10",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbols"] == ["AAPL", "MSFT"]
    assert set(payload["results"].keys()) == {"AAPL", "MSFT"}
    assert payload["results"]["AAPL"][0]["daily_return"] is None
    assert payload["results"]["AAPL"][1]["daily_return"] == 0.1
    assert payload["results"]["MSFT"][1]["daily_return"] == 0.05
