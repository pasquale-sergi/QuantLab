from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import prod, sqrt


TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class DrawdownPoint:
    date: date
    equity: float
    drawdown: float


def _clean_returns(returns: list[float | None]) -> list[float]:
    return [value for value in returns if value is not None]


def total_return(returns: list[float | None]) -> float | None:
    clean_returns = _clean_returns(returns)
    if not clean_returns:
        return None
    return prod((1.0 + value) for value in clean_returns) - 1.0


def annualized_return(returns: list[float | None], trading_days_per_year: int = TRADING_DAYS_PER_YEAR) -> float | None:
    clean_returns = _clean_returns(returns)
    if not clean_returns:
        return None

    cumulative_return = prod((1.0 + value) for value in clean_returns)
    periods = len(clean_returns)
    return cumulative_return ** (trading_days_per_year / periods) - 1.0


def volatility(returns: list[float | None]) -> float | None:
    clean_returns = _clean_returns(returns)
    periods = len(clean_returns)
    if periods < 2:
        return None

    mean_return = sum(clean_returns) / periods
    variance = sum((value - mean_return) ** 2 for value in clean_returns) / (periods - 1)
    return sqrt(variance)


def annualized_volatility(returns: list[float | None], trading_days_per_year: int = TRADING_DAYS_PER_YEAR) -> float | None:
    daily_volatility = volatility(returns)
    if daily_volatility is None:
        return None
    return daily_volatility * sqrt(trading_days_per_year)


def sharpe_ratio(
    returns: list[float | None],
    risk_free_rate: float = 0.0,
    trading_days_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float | None:
    clean_returns = _clean_returns(returns)
    if len(clean_returns) < 2:
        return None

    daily_volatility = volatility(clean_returns)
    if daily_volatility is None or daily_volatility == 0.0:
        return None

    daily_risk_free_rate = risk_free_rate / trading_days_per_year
    excess_returns = [value - daily_risk_free_rate for value in clean_returns]
    mean_excess_return = sum(excess_returns) / len(excess_returns)
    return (mean_excess_return / daily_volatility) * sqrt(trading_days_per_year)


def historical_var_95(returns: list[float | None]) -> float | None:
    clean_returns = sorted(_clean_returns(returns))
    if not clean_returns:
        return None

    index = max(int(len(clean_returns) * 0.05) - 1, 0)
    return clean_returns[index]


def expected_shortfall_95(returns: list[float | None]) -> float | None:
    clean_returns = _clean_returns(returns)
    if not clean_returns:
        return None

    var_95 = historical_var_95(clean_returns)
    if var_95 is None:
        return None

    tail = [value for value in clean_returns if value <= var_95]
    if not tail:
        return None
    return sum(tail) / len(tail)


def drawdown_series(returns_with_dates: list[tuple[date, float | None]]) -> list[DrawdownPoint]:
    points: list[DrawdownPoint] = []
    equity = 1.0
    peak = 1.0

    for point_date, daily_return in returns_with_dates:
        if daily_return is not None:
            equity *= 1.0 + daily_return

        peak = max(peak, equity)
        drawdown = (equity / peak) - 1.0 if peak != 0 else 0.0
        points.append(DrawdownPoint(date=point_date, equity=equity, drawdown=drawdown))

    return points


def max_drawdown(returns_with_dates: list[tuple[date, float | None]]) -> float | None:
    points = drawdown_series(returns_with_dates)
    if not points:
        return None
    return min(point.drawdown for point in points)
