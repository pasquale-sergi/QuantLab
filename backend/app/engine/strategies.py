from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import date
from typing import Literal

from app.db.models import Price


SignalSide = Literal["BUY", "SELL"]


@dataclass(frozen=True)
class SignalPoint:
    date: date
    short_ma: float | None
    long_ma: float | None
    signal: SignalSide | None


def simple_moving_average(values: list[float], window: int) -> list[float | None]:
    if window <= 0:
        raise ValueError("window must be > 0")

    result: list[float | None] = []
    running_sum = 0.0
    window_values: deque[float] = deque()

    for value in values:
        running_sum += value
        window_values.append(value)
        if len(window_values) > window:
            running_sum -= window_values.popleft()

        if len(window_values) == window:
            result.append(running_sum / window)
        else:
            result.append(None)

    return result


def moving_average_crossover_signals(
    prices: list[Price],
    short_window: int,
    long_window: int,
) -> list[SignalPoint]:
    if short_window <= 0 or long_window <= 0:
        raise ValueError("short_window and long_window must be > 0")
    if short_window >= long_window:
        raise ValueError("short_window must be < long_window")

    closes = [float(price.close) for price in prices]
    short_ma = simple_moving_average(closes, short_window)
    long_ma = simple_moving_average(closes, long_window)

    points: list[SignalPoint] = []
    previous_short: float | None = None
    previous_long: float | None = None

    for index, price in enumerate(prices):
        signal: SignalSide | None = None
        current_short = short_ma[index]
        current_long = long_ma[index]

        if (
            previous_short is not None
            and previous_long is not None
            and current_short is not None
            and current_long is not None
        ):
            if previous_short <= previous_long and current_short > current_long:
                signal = "BUY"
            elif previous_short >= previous_long and current_short < current_long:
                signal = "SELL"

        points.append(
            SignalPoint(
                date=price.date,
                short_ma=current_short,
                long_ma=current_long,
                signal=signal,
            )
        )

        previous_short = current_short
        previous_long = current_long

    return points
