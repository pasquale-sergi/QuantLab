from __future__ import annotations

from dataclasses import dataclass

from app.engine.portfolio import EquityPoint, Trade


@dataclass(frozen=True)
class BacktestSummary:
    number_of_trades: int
    buy_trades: int
    sell_trades: int
    time_in_market_pct: float
    best_day: float | None
    worst_day: float | None
    average_daily_return: float | None


def calculate_backtest_summary(trades: list[Trade], equity_curve: list[EquityPoint]) -> BacktestSummary:
    number_of_trades = len(trades)
    buy_trades = sum(1 for trade in trades if trade.side == "BUY")
    sell_trades = sum(1 for trade in trades if trade.side == "SELL")

    if equity_curve:
        in_market_days = sum(1 for point in equity_curve if point.shares > 0)
        time_in_market_pct = in_market_days / len(equity_curve)
    else:
        time_in_market_pct = 0.0

    daily_returns = [point.daily_return for point in equity_curve if point.daily_return is not None]
    best_day = max(daily_returns) if daily_returns else None
    worst_day = min(daily_returns) if daily_returns else None
    average_daily_return = (sum(daily_returns) / len(daily_returns)) if daily_returns else None

    return BacktestSummary(
        number_of_trades=number_of_trades,
        buy_trades=buy_trades,
        sell_trades=sell_trades,
        time_in_market_pct=time_in_market_pct,
        best_day=best_day,
        worst_day=worst_day,
        average_daily_return=average_daily_return,
    )
