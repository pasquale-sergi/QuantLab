from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.data.backtest_experiment_repository import BacktestExperimentRepository, BacktestExperimentsNotFoundError
from app.db.models import BacktestEquityPoint, BacktestExperiment, BacktestMetric, BacktestTrade
from app.engine.backtester import BacktestResult


@dataclass(frozen=True)
class BacktestSaveRequest:
    symbol: str
    strategy: str
    parameters: dict[str, int]
    start_date: date
    end_date: date
    initial_cash: float
    transaction_cost_bps: float
    result: BacktestResult


def _decimal_or_none(value: float | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _decimal(value: float) -> Decimal:
    return Decimal(str(value))


class BacktestExperimentService:
    def __init__(self, repository: BacktestExperimentRepository) -> None:
        self.repository = repository

    def save_experiment(self, request: BacktestSaveRequest) -> BacktestExperiment:
        experiment = BacktestExperiment(
            symbol=request.symbol,
            strategy=request.strategy,
            parameters=request.parameters,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_cash=_decimal(request.initial_cash),
            transaction_cost_bps=_decimal(request.transaction_cost_bps),
            final_equity=_decimal(request.result.final_equity),
        )

        experiment.metrics = BacktestMetric(
            total_return=_decimal_or_none(request.result.metrics.total_return),
            annualized_return=_decimal_or_none(request.result.metrics.annualized_return),
            volatility=_decimal_or_none(request.result.metrics.volatility),
            annualized_volatility=_decimal_or_none(request.result.metrics.annualized_volatility),
            sharpe_ratio=_decimal_or_none(request.result.metrics.sharpe_ratio),
            max_drawdown=_decimal_or_none(request.result.metrics.max_drawdown),
            historical_var_95=_decimal_or_none(request.result.metrics.historical_var_95),
            expected_shortfall_95=_decimal_or_none(request.result.metrics.expected_shortfall_95),
            number_of_trades=request.result.metrics.number_of_trades,
            buy_trades=request.result.metrics.buy_trades,
            sell_trades=request.result.metrics.sell_trades,
            time_in_market_pct=_decimal(request.result.metrics.time_in_market_pct),
            best_day=_decimal_or_none(request.result.metrics.best_day),
            worst_day=_decimal_or_none(request.result.metrics.worst_day),
            average_daily_return=_decimal_or_none(request.result.metrics.average_daily_return),
        )

        experiment.trades = [
            BacktestTrade(
                date=trade.date,
                symbol=trade.symbol,
                side=trade.side,
                price=_decimal(trade.price),
                shares=trade.shares,
                gross_value=_decimal(trade.gross_value),
                transaction_cost=_decimal(trade.transaction_cost),
                cash_after_trade=_decimal(trade.cash_after_trade),
            )
            for trade in request.result.trades
        ]

        experiment.equity_curve = [
            BacktestEquityPoint(
                date=point.date,
                cash=_decimal(point.cash),
                shares=point.shares,
                close_price=_decimal(point.close_price),
                position_value=_decimal(point.position_value),
                total_equity=_decimal(point.total_equity),
                daily_return=_decimal_or_none(point.daily_return),
            )
            for point in request.result.equity_curve
        ]

        saved = self.repository.add(experiment)
        self.repository.session.commit()
        self.repository.session.refresh(saved)
        return saved

    def list_experiments(self) -> list[BacktestExperiment]:
        return self.repository.list_all()

    def get_experiment(self, experiment_id: int) -> BacktestExperiment:
        return self.repository.get_by_id(experiment_id)

    def compare_experiments(self, experiment_ids: list[int]) -> list[BacktestExperiment]:
        experiments = self.repository.get_by_ids_with_metrics(experiment_ids)
        found_ids = {experiment.id for experiment in experiments}
        missing_ids = [experiment_id for experiment_id in experiment_ids if experiment_id not in found_ids]
        if missing_ids:
            raise BacktestExperimentsNotFoundError(missing_ids)
        return experiments
