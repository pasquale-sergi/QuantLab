from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from app.db.models import Price
from app.engine.portfolio import simulate_portfolio
from app.engine.strategies import moving_average_crossover_signals


def _prices(closes: list[float], start: date = date(2024, 1, 1)) -> list[Price]:
    rows: list[Price] = []
    for index, close in enumerate(closes):
        price_date = start + timedelta(days=index)
        rows.append(
            Price(
                asset_id=1,
                date=price_date,
                open=Decimal(str(close)),
                high=Decimal(str(close)),
                low=Decimal(str(close)),
                close=Decimal(str(close)),
                volume=1000,
                created_at=datetime.now(UTC),
            )
        )
    return rows


def test_moving_average_signal_generation() -> None:
    prices = _prices([1.0, 1.0, 1.0, 2.0, 3.0, 2.0, 1.0])
    signals = moving_average_crossover_signals(prices, short_window=2, long_window=3)

    buy_dates = [point.date for point in signals if point.signal == "BUY"]
    sell_dates = [point.date for point in signals if point.signal == "SELL"]

    assert buy_dates == [prices[3].date]
    assert sell_dates == [prices[6].date]


def test_no_lookahead_execution() -> None:
    prices = _prices([1.0, 1.0, 1.0, 2.0, 1.0, 0.5, 1.0])
    signal_points = moving_average_crossover_signals(prices, short_window=2, long_window=3)
    result = simulate_portfolio(
        symbol="AAPL",
        prices=prices,
        signals=[point.signal for point in signal_points],
        initial_cash=100.0,
        transaction_cost_bps=0.0,
    )

    assert result.trades[0].side == "BUY"
    assert result.trades[0].date == prices[4].date


def test_buy_trade_creation() -> None:
    prices = _prices([10.0, 10.0, 10.0])
    result = simulate_portfolio(
        symbol="AAPL",
        prices=prices,
        signals=[None, "BUY", None],
        initial_cash=1000.0,
        transaction_cost_bps=0.0,
    )

    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.side == "BUY"
    assert trade.shares == 100
    assert trade.cash_after_trade == pytest.approx(0.0, rel=1e-12)


def test_sell_trade_creation() -> None:
    prices = _prices([10.0, 10.0, 10.0, 10.0])
    result = simulate_portfolio(
        symbol="AAPL",
        prices=prices,
        signals=[None, "BUY", "SELL", None],
        initial_cash=1000.0,
        transaction_cost_bps=0.0,
    )

    assert len(result.trades) == 2
    assert result.trades[0].side == "BUY"
    assert result.trades[1].side == "SELL"


def test_transaction_cost_calculation() -> None:
    prices = _prices([10.0, 10.0, 10.0, 10.0])
    result = simulate_portfolio(
        symbol="AAPL",
        prices=prices,
        signals=[None, "BUY", "SELL", None],
        initial_cash=1000.0,
        transaction_cost_bps=10.0,
    )

    buy_trade, sell_trade = result.trades
    assert buy_trade.transaction_cost == pytest.approx(0.99, rel=1e-9)
    assert sell_trade.transaction_cost == pytest.approx(0.99, rel=1e-9)
    assert sell_trade.cash_after_trade == pytest.approx(998.02, rel=1e-9)


def test_portfolio_equity_calculation() -> None:
    prices = _prices([10.0, 11.0])
    result = simulate_portfolio(
        symbol="AAPL",
        prices=prices,
        signals=[None, None],
        initial_cash=100.0,
        transaction_cost_bps=0.0,
    )

    assert result.equity_curve[0].total_equity == pytest.approx(100.0, rel=1e-12)
    assert result.equity_curve[1].total_equity == pytest.approx(100.0, rel=1e-12)
    assert result.equity_curve[1].daily_return == pytest.approx(0.0, rel=1e-12)
