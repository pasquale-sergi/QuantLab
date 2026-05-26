from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    prices: Mapped[list[Price]] = relationship(back_populates="asset", cascade="all, delete-orphan")


class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (
        UniqueConstraint("asset_id", "date", name="uq_prices_asset_id_date"),
        Index("ix_prices_date", "date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    open: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    volume: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    asset: Mapped[Asset] = relationship(back_populates="prices")


class BacktestExperiment(Base):
    __tablename__ = "backtest_experiments"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    strategy: Mapped[str] = mapped_column(String(64), nullable=False)
    parameters: Mapped[dict[str, int]] = mapped_column(JSON, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    initial_cash: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    transaction_cost_bps: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    final_equity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    metrics: Mapped[BacktestMetric | None] = relationship(
        back_populates="experiment",
        cascade="all, delete-orphan",
        uselist=False,
    )
    trades: Mapped[list[BacktestTrade]] = relationship(back_populates="experiment", cascade="all, delete-orphan")
    equity_curve: Mapped[list[BacktestEquityPoint]] = relationship(back_populates="experiment", cascade="all, delete-orphan")


class BacktestMetric(Base):
    __tablename__ = "backtest_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    experiment_id: Mapped[int] = mapped_column(
        ForeignKey("backtest_experiments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    total_return: Mapped[Decimal | None] = mapped_column(Numeric(18, 10), nullable=True)
    annualized_return: Mapped[Decimal | None] = mapped_column(Numeric(18, 10), nullable=True)
    volatility: Mapped[Decimal | None] = mapped_column(Numeric(18, 10), nullable=True)
    annualized_volatility: Mapped[Decimal | None] = mapped_column(Numeric(18, 10), nullable=True)
    sharpe_ratio: Mapped[Decimal | None] = mapped_column(Numeric(18, 10), nullable=True)
    max_drawdown: Mapped[Decimal | None] = mapped_column(Numeric(18, 10), nullable=True)
    historical_var_95: Mapped[Decimal | None] = mapped_column(Numeric(18, 10), nullable=True)
    expected_shortfall_95: Mapped[Decimal | None] = mapped_column(Numeric(18, 10), nullable=True)
    number_of_trades: Mapped[int] = mapped_column(nullable=False, default=0)
    buy_trades: Mapped[int] = mapped_column(nullable=False, default=0)
    sell_trades: Mapped[int] = mapped_column(nullable=False, default=0)
    time_in_market_pct: Mapped[Decimal] = mapped_column(Numeric(18, 10), nullable=False, default=0)
    best_day: Mapped[Decimal | None] = mapped_column(Numeric(18, 10), nullable=True)
    worst_day: Mapped[Decimal | None] = mapped_column(Numeric(18, 10), nullable=True)
    average_daily_return: Mapped[Decimal | None] = mapped_column(Numeric(18, 10), nullable=True)

    experiment: Mapped[BacktestExperiment] = relationship(back_populates="metrics")


class BacktestTrade(Base):
    __tablename__ = "backtest_trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    experiment_id: Mapped[int] = mapped_column(
        ForeignKey("backtest_experiments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    shares: Mapped[int] = mapped_column(nullable=False)
    gross_value: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    transaction_cost: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    cash_after_trade: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)

    experiment: Mapped[BacktestExperiment] = relationship(back_populates="trades")


class BacktestEquityPoint(Base):
    __tablename__ = "backtest_equity_points"

    id: Mapped[int] = mapped_column(primary_key=True)
    experiment_id: Mapped[int] = mapped_column(
        ForeignKey("backtest_experiments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    cash: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    shares: Mapped[int] = mapped_column(nullable=False)
    close_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    position_value: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    total_equity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    daily_return: Mapped[Decimal | None] = mapped_column(Numeric(18, 10), nullable=True)

    experiment: Mapped[BacktestExperiment] = relationship(back_populates="equity_curve")
