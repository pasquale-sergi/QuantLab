from datetime import date

from app.analytics.backtest_summary import calculate_backtest_summary
from app.engine.portfolio import EquityPoint, Trade


def test_calculate_backtest_summary_metrics() -> None:
    trades = [
        Trade(
            date=date(2024, 1, 2),
            symbol="AAPL",
            side="BUY",
            price=100.0,
            shares=10,
            gross_value=1000.0,
            transaction_cost=1.0,
            cash_after_trade=8999.0,
        ),
        Trade(
            date=date(2024, 1, 4),
            symbol="AAPL",
            side="SELL",
            price=110.0,
            shares=10,
            gross_value=1100.0,
            transaction_cost=1.1,
            cash_after_trade=10097.9,
        ),
        Trade(
            date=date(2024, 1, 5),
            symbol="AAPL",
            side="BUY",
            price=105.0,
            shares=9,
            gross_value=945.0,
            transaction_cost=0.945,
            cash_after_trade=9151.955,
        ),
    ]

    equity_curve = [
        EquityPoint(
            date=date(2024, 1, 1),
            cash=10000.0,
            shares=0,
            close_price=100.0,
            position_value=0.0,
            total_equity=10000.0,
            daily_return=None,
        ),
        EquityPoint(
            date=date(2024, 1, 2),
            cash=8999.0,
            shares=10,
            close_price=101.0,
            position_value=1010.0,
            total_equity=10009.0,
            daily_return=0.0009,
        ),
        EquityPoint(
            date=date(2024, 1, 3),
            cash=8999.0,
            shares=10,
            close_price=98.0,
            position_value=980.0,
            total_equity=9979.0,
            daily_return=-0.002997302427814,
        ),
        EquityPoint(
            date=date(2024, 1, 4),
            cash=10097.9,
            shares=0,
            close_price=110.0,
            position_value=0.0,
            total_equity=10097.9,
            daily_return=0.011914019440825734,
        ),
        EquityPoint(
            date=date(2024, 1, 5),
            cash=9151.955,
            shares=9,
            close_price=105.0,
            position_value=945.0,
            total_equity=10096.955,
            daily_return=-9.853535884890395e-05,
        ),
    ]

    summary = calculate_backtest_summary(trades, equity_curve)

    assert summary.number_of_trades == 3
    assert summary.buy_trades == 2
    assert summary.sell_trades == 1
    assert summary.time_in_market_pct == 3 / 5
    assert summary.best_day == 0.011914019440825734
    assert summary.worst_day == -0.002997302427814
    assert summary.average_daily_return == (
        0.0009
        + (-0.002997302427814)
        + 0.011914019440825734
        + (-9.853535884890395e-05)
    ) / 4
