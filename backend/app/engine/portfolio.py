from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.db.models import Price
from app.engine.strategies import SignalSide


@dataclass(frozen=True)
class Trade:
    date: date
    symbol: str
    side: SignalSide
    price: float
    shares: int
    gross_value: float
    transaction_cost: float
    cash_after_trade: float


@dataclass(frozen=True)
class EquityPoint:
    date: date
    cash: float
    shares: int
    close_price: float
    position_value: float
    total_equity: float
    daily_return: float | None


@dataclass(frozen=True)
class PortfolioSimulationResult:
    trades: list[Trade]
    equity_curve: list[EquityPoint]


def simulate_portfolio(
    symbol: str,
    prices: list[Price],
    signals: list[SignalSide | None],
    initial_cash: float,
    transaction_cost_bps: float,
) -> PortfolioSimulationResult:
    if initial_cash <= 0:
        raise ValueError("initial_cash must be > 0")
    if transaction_cost_bps < 0:
        raise ValueError("transaction_cost_bps must be >= 0")
    if len(prices) != len(signals):
        raise ValueError("prices and signals must have the same length")

    cost_rate = transaction_cost_bps / 10000.0
    cash = initial_cash
    shares = 0
    previous_equity: float | None = None
    pending_signal: SignalSide | None = None

    trades: list[Trade] = []
    equity_curve: list[EquityPoint] = []

    for index, price_row in enumerate(prices):
        close_price = float(price_row.close)

        if pending_signal == "BUY" and shares == 0:
            max_shares = int(cash / (close_price * (1.0 + cost_rate)))
            if max_shares > 0:
                gross_value = max_shares * close_price
                transaction_cost = gross_value * cost_rate
                cash -= gross_value + transaction_cost
                shares = max_shares
                trades.append(
                    Trade(
                        date=price_row.date,
                        symbol=symbol,
                        side="BUY",
                        price=close_price,
                        shares=max_shares,
                        gross_value=gross_value,
                        transaction_cost=transaction_cost,
                        cash_after_trade=cash,
                    )
                )

        elif pending_signal == "SELL" and shares > 0:
            gross_value = shares * close_price
            transaction_cost = gross_value * cost_rate
            cash += gross_value - transaction_cost
            sold_shares = shares
            shares = 0
            trades.append(
                Trade(
                    date=price_row.date,
                    symbol=symbol,
                    side="SELL",
                    price=close_price,
                    shares=sold_shares,
                    gross_value=gross_value,
                    transaction_cost=transaction_cost,
                    cash_after_trade=cash,
                )
            )

        position_value = shares * close_price
        total_equity = cash + position_value
        daily_return: float | None = None
        if previous_equity is not None and previous_equity != 0.0:
            daily_return = (total_equity / previous_equity) - 1.0

        equity_curve.append(
            EquityPoint(
                date=price_row.date,
                cash=cash,
                shares=shares,
                close_price=close_price,
                position_value=position_value,
                total_equity=total_equity,
                daily_return=daily_return,
            )
        )

        previous_equity = total_equity
        pending_signal = signals[index]

    return PortfolioSimulationResult(trades=trades, equity_curve=equity_curve)
