from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.data.market_data_repository import MarketDataRepository, PriceInput
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


def _seed_symbol(db_session, symbol: str = "AAPL") -> None:
    repo = MarketDataRepository(db_session)
    asset = repo.get_or_create_asset(symbol)

    repo.upsert_prices(
        asset.id,
        [
            PriceInput(date=date(2024, 1, 2), open=Decimal("100"), high=Decimal("101"), low=Decimal("99"), close=Decimal("100"), volume=1000),
            PriceInput(date=date(2024, 1, 3), open=Decimal("110"), high=Decimal("111"), low=Decimal("109"), close=Decimal("110"), volume=1000),
            PriceInput(date=date(2024, 1, 4), open=Decimal("104"), high=Decimal("105"), low=Decimal("103"), close=Decimal("104.5"), volume=1000),
            PriceInput(date=date(2024, 1, 5), open=Decimal("106"), high=Decimal("107"), low=Decimal("105"), close=Decimal("106.59"), volume=1000),
        ],
    )
    db_session.commit()


def test_metrics_endpoint(client, db_session) -> None:
    _seed_symbol(db_session)

    response = client.get(
        "/analytics/AAPL/metrics",
        params={"start_date": "2024-01-01", "end_date": "2024-01-10"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "AAPL"
    metrics = payload["metrics"]
    assert metrics["total_return"] == pytest.approx(0.0659, rel=1e-6)
    assert metrics["historical_var_95"] == pytest.approx(-0.05, rel=1e-9)
    assert metrics["expected_shortfall_95"] == pytest.approx(-0.05, rel=1e-9)
    assert metrics["max_drawdown"] < 0.0


def test_drawdown_endpoint(client, db_session) -> None:
    _seed_symbol(db_session)

    response = client.get(
        "/analytics/AAPL/drawdown",
        params={"start_date": "2024-01-01", "end_date": "2024-01-10"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "AAPL"
    rows = payload["rows"]
    assert len(rows) == 4
    assert rows[0]["equity"] == pytest.approx(1.0, rel=1e-12)
    assert rows[0]["drawdown"] == pytest.approx(0.0, rel=1e-12)
    assert rows[2]["drawdown"] == pytest.approx(-0.05, rel=1e-6)
