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


def _seed_prices(db_session) -> None:
    repository = MarketDataRepository(db_session)
    asset = repository.get_or_create_asset("AAPL")
    repository.upsert_prices(
        asset.id,
        [
            PriceInput(date=date(2024, 1, 1), open=Decimal("1"), high=Decimal("1"), low=Decimal("1"), close=Decimal("1"), volume=1000),
            PriceInput(date=date(2024, 1, 2), open=Decimal("1"), high=Decimal("1"), low=Decimal("1"), close=Decimal("1"), volume=1000),
            PriceInput(date=date(2024, 1, 3), open=Decimal("1"), high=Decimal("1"), low=Decimal("1"), close=Decimal("1"), volume=1000),
            PriceInput(date=date(2024, 1, 4), open=Decimal("2"), high=Decimal("2"), low=Decimal("2"), close=Decimal("2"), volume=1000),
            PriceInput(date=date(2024, 1, 5), open=Decimal("1"), high=Decimal("1"), low=Decimal("1"), close=Decimal("1"), volume=1000),
            PriceInput(date=date(2024, 1, 6), open=Decimal("0.5"), high=Decimal("0.5"), low=Decimal("0.5"), close=Decimal("0.5"), volume=1000),
            PriceInput(date=date(2024, 1, 7), open=Decimal("1"), high=Decimal("1"), low=Decimal("1"), close=Decimal("1"), volume=1000),
        ],
    )
    db_session.commit()


def test_backtest_endpoint_response(client, db_session) -> None:
    _seed_prices(db_session)
    payload = {
        "symbol": "AAPL",
        "start_date": "2024-01-01",
        "end_date": "2024-01-07",
        "strategy": "moving_average_crossover",
        "parameters": {"short_window": 2, "long_window": 3},
        "initial_cash": 10000,
        "transaction_cost_bps": 10,
    }

    response = client.post("/backtests/run", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["strategy"] == "moving_average_crossover"
    assert body["parameters"]["short_window"] == 2
    assert body["parameters"]["long_window"] == 3
    assert isinstance(body["final_equity"], float)
    assert "total_return" in body["metrics"]
    assert "sharpe_ratio" in body["metrics"]
    assert len(body["equity_curve"]) == 7
    assert len(body["trades"]) >= 1


def test_backtest_endpoint_invalid_symbol(client) -> None:
    payload = {
        "symbol": "INVALID",
        "start_date": "2024-01-01",
        "end_date": "2024-01-06",
        "strategy": "moving_average_crossover",
        "parameters": {"short_window": 2, "long_window": 3},
        "initial_cash": 10000,
        "transaction_cost_bps": 10,
    }

    response = client.post("/backtests/run", json=payload)
    assert response.status_code == 404


def test_backtest_endpoint_invalid_window_parameters(client, db_session) -> None:
    _seed_prices(db_session)
    payload = {
        "symbol": "AAPL",
        "start_date": "2024-01-01",
        "end_date": "2024-01-06",
        "strategy": "moving_average_crossover",
        "parameters": {"short_window": 5, "long_window": 5},
        "initial_cash": 10000,
        "transaction_cost_bps": 10,
    }

    response = client.post("/backtests/run", json=payload)
    assert response.status_code == 400
