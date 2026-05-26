from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import BacktestExperiment


class BacktestExperimentNotFoundError(ValueError):
    def __init__(self, experiment_id: int) -> None:
        super().__init__(f"Backtest experiment '{experiment_id}' was not found")
        self.experiment_id = experiment_id


class BacktestExperimentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, experiment: BacktestExperiment) -> BacktestExperiment:
        self.session.add(experiment)
        self.session.flush()
        return experiment

    def list_all(self) -> list[BacktestExperiment]:
        return self.session.scalars(
            select(BacktestExperiment)
            .order_by(BacktestExperiment.created_at.desc(), BacktestExperiment.id.desc())
        ).all()

    def get_by_id(self, experiment_id: int) -> BacktestExperiment:
        experiment = self.session.scalar(
            select(BacktestExperiment)
            .options(
                selectinload(BacktestExperiment.metrics),
                selectinload(BacktestExperiment.trades),
                selectinload(BacktestExperiment.equity_curve),
            )
            .where(BacktestExperiment.id == experiment_id)
        )
        if experiment is None:
            raise BacktestExperimentNotFoundError(experiment_id)
        return experiment
