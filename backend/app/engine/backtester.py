from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.analytics.backtest_summary import calculate_backtest_summary
from app.analytics.metrics import (
    annualized_return,
    annualized_volatility,
    expected_shortfall_95,
    historical_var_95,
    max_drawdown,
    sharpe_ratio,
    total_return,
    volatility,
)
from app.db.models import Price
from app.engine.portfolio import EquityPoint, Trade, simulate_portfolio
from app.engine.strategies import moving_average_crossover_signals


class InvalidBacktestParameterError(ValueError):
    pass


@dataclass(frozen=True)
class BacktestMetrics:
    total_return: float | None
    annualized_return: float | None
    volatility: float | None
    annualized_volatility: float | None
    sharpe_ratio: float | None
    max_drawdown: float | None
    historical_var_95: float | None
    expected_shortfall_95: float | None
    number_of_trades: int
    buy_trades: int
    sell_trades: int
    time_in_market_pct: float
    best_day: float | None
    worst_day: float | None
    average_daily_return: float | None


@dataclass(frozen=True)
class BacktestResult:
    symbol: str
    strategy: str
    parameters: dict[str, int]
    initial_cash: float
    final_equity: float
    metrics: BacktestMetrics
    trades: list[Trade]
    equity_curve: list[EquityPoint]


def run_moving_average_crossover_backtest(
    symbol: str,
    prices: list[Price],
    short_window: int,
    long_window: int,
    initial_cash: float,
    transaction_cost_bps: float,
) -> BacktestResult:
    if short_window <= 0 or long_window <= 0:
        raise InvalidBacktestParameterError("short_window and long_window must be > 0")
    if short_window >= long_window:
        raise InvalidBacktestParameterError("short_window must be < long_window")

    signal_points = moving_average_crossover_signals(prices, short_window=short_window, long_window=long_window)
    signals = [point.signal for point in signal_points]
    simulation_result = simulate_portfolio(
        symbol=symbol,
        prices=prices,
        signals=signals,
        initial_cash=initial_cash,
        transaction_cost_bps=transaction_cost_bps,
    )

    returns = [point.daily_return for point in simulation_result.equity_curve]
    returns_with_dates: list[tuple[date, float | None]] = [
        (point.date, point.daily_return) for point in simulation_result.equity_curve
    ]
    summary = calculate_backtest_summary(simulation_result.trades, simulation_result.equity_curve)

    metrics = BacktestMetrics(
        total_return=total_return(returns),
        annualized_return=annualized_return(returns),
        volatility=volatility(returns),
        annualized_volatility=annualized_volatility(returns),
        sharpe_ratio=sharpe_ratio(returns),
        max_drawdown=max_drawdown(returns_with_dates),
        historical_var_95=historical_var_95(returns),
        expected_shortfall_95=expected_shortfall_95(returns),
        number_of_trades=summary.number_of_trades,
        buy_trades=summary.buy_trades,
        sell_trades=summary.sell_trades,
        time_in_market_pct=summary.time_in_market_pct,
        best_day=summary.best_day,
        worst_day=summary.worst_day,
        average_daily_return=summary.average_daily_return,
    )

    final_equity = simulation_result.equity_curve[-1].total_equity if simulation_result.equity_curve else initial_cash

    return BacktestResult(
        symbol=symbol,
        strategy="moving_average_crossover",
        parameters={"short_window": short_window, "long_window": long_window},
        initial_cash=initial_cash,
        final_equity=final_equity,
        metrics=metrics,
        trades=simulation_result.trades,
        equity_curve=simulation_result.equity_curve,
    )
