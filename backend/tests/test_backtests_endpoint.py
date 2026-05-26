from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.data.market_data_repository import MarketDataRepository, PriceInput
from app.db.models import BacktestEquityPoint, BacktestExperiment, BacktestMetric, BacktestTrade
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
    assert isinstance(body["experiment_id"], int)
    assert body["symbol"] == "AAPL"
    assert body["strategy"] == "moving_average_crossover"
    assert body["parameters"]["short_window"] == 2
    assert body["parameters"]["long_window"] == 3
    assert body["start_date"] == "2024-01-01"
    assert body["end_date"] == "2024-01-07"
    assert body["transaction_cost_bps"] == 10
    assert isinstance(body["final_equity"], float)
    assert "total_return" in body["metrics"]
    assert "sharpe_ratio" in body["metrics"]
    assert "number_of_trades" in body["metrics"]
    assert "buy_trades" in body["metrics"]
    assert "sell_trades" in body["metrics"]
    assert "time_in_market_pct" in body["metrics"]
    assert "best_day" in body["metrics"]
    assert "worst_day" in body["metrics"]
    assert "average_daily_return" in body["metrics"]
    assert body["metrics"]["number_of_trades"] >= 0
    assert body["metrics"]["buy_trades"] >= 0
    assert body["metrics"]["sell_trades"] >= 0
    assert 0.0 <= body["metrics"]["time_in_market_pct"] <= 1.0
    assert len(body["equity_curve"]) == 7
    assert len(body["trades"]) >= 1

    experiment_id = body["experiment_id"]

    experiment = db_session.scalar(select(BacktestExperiment).where(BacktestExperiment.id == experiment_id))
    assert experiment is not None
    assert experiment.symbol == "AAPL"
    assert experiment.strategy == "moving_average_crossover"

    metric = db_session.scalar(select(BacktestMetric).where(BacktestMetric.experiment_id == experiment_id))
    assert metric is not None

    trades = db_session.scalars(select(BacktestTrade).where(BacktestTrade.experiment_id == experiment_id)).all()
    assert len(trades) >= 1

    equity_points = db_session.scalars(
        select(BacktestEquityPoint).where(BacktestEquityPoint.experiment_id == experiment_id)
    ).all()
    assert len(equity_points) == 7


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


def test_backtest_experiments_list_and_detail(client, db_session) -> None:
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

    run_response = client.post("/backtests/run", json=payload)
    assert run_response.status_code == 200
    experiment_id = run_response.json()["experiment_id"]

    list_response = client.get("/backtests/experiments")
    assert list_response.status_code == 200
    list_body = list_response.json()
    assert len(list_body) >= 1
    assert any(item["experiment_id"] == experiment_id for item in list_body)

    detail_response = client.get(f"/backtests/experiments/{experiment_id}")
    assert detail_response.status_code == 200
    detail_body = detail_response.json()
    assert detail_body["experiment_id"] == experiment_id
    assert detail_body["symbol"] == "AAPL"
    assert detail_body["strategy"] == "moving_average_crossover"
    assert detail_body["parameters"]["short_window"] == 2
    assert detail_body["parameters"]["long_window"] == 3
    assert "total_return" in detail_body["metrics"]
    assert "number_of_trades" in detail_body["metrics"]
    assert "time_in_market_pct" in detail_body["metrics"]
    assert "best_day" in detail_body["metrics"]
    assert "worst_day" in detail_body["metrics"]
    assert "average_daily_return" in detail_body["metrics"]
    assert len(detail_body["equity_curve"]) == 7
    assert len(detail_body["trades"]) >= 1


def test_backtest_experiment_detail_not_found(client) -> None:
    response = client.get("/backtests/experiments/999999")
    assert response.status_code == 404


def test_backtest_experiments_compare_success(client, db_session) -> None:
    _seed_prices(db_session)

    payload_one = {
        "symbol": "AAPL",
        "start_date": "2024-01-01",
        "end_date": "2024-01-07",
        "strategy": "moving_average_crossover",
        "parameters": {"short_window": 2, "long_window": 3},
        "initial_cash": 10000,
        "transaction_cost_bps": 10,
    }
    payload_two = {
        "symbol": "AAPL",
        "start_date": "2024-01-01",
        "end_date": "2024-01-07",
        "strategy": "moving_average_crossover",
        "parameters": {"short_window": 1, "long_window": 4},
        "initial_cash": 12000,
        "transaction_cost_bps": 5,
    }

    response_one = client.post("/backtests/run", json=payload_one)
    response_two = client.post("/backtests/run", json=payload_two)
    assert response_one.status_code == 200
    assert response_two.status_code == 200

    experiment_id_one = response_one.json()["experiment_id"]
    experiment_id_two = response_two.json()["experiment_id"]

    compare_response = client.get(f"/backtests/experiments/compare?ids={experiment_id_one},{experiment_id_two}")
    assert compare_response.status_code == 200

    body = compare_response.json()
    assert "experiments" in body
    assert len(body["experiments"]) == 2

    first = body["experiments"][0]
    assert first["experiment_id"] == experiment_id_one
    assert first["symbol"] == "AAPL"
    assert first["strategy"] == "moving_average_crossover"
    assert "total_return" in first
    assert "annualized_return" in first
    assert "annualized_volatility" in first
    assert "sharpe_ratio" in first
    assert "max_drawdown" in first
    assert "historical_var_95" in first
    assert "expected_shortfall_95" in first
    assert "number_of_trades" in first
    assert "buy_trades" in first
    assert "sell_trades" in first
    assert "time_in_market_pct" in first
    assert "best_day" in first
    assert "worst_day" in first
    assert "average_daily_return" in first
    assert "trades" not in first
    assert "equity_curve" not in first


def test_backtest_experiments_compare_missing_id_returns_404(client, db_session) -> None:
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

    run_response = client.post("/backtests/run", json=payload)
    assert run_response.status_code == 200
    existing_id = run_response.json()["experiment_id"]

    compare_response = client.get(f"/backtests/experiments/compare?ids={existing_id},999999")
    assert compare_response.status_code == 404
    assert "not found" in compare_response.json()["detail"].lower()


def test_backtest_experiments_compare_empty_ids_returns_400(client) -> None:
    response = client.get("/backtests/experiments/compare?ids=")
    assert response.status_code == 400
