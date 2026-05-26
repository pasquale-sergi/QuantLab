"""add backtest experiment tracking tables

Revision ID: 20260526_01
Revises:
Create Date: 2026-05-26
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260526_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "backtest_experiments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("strategy", sa.String(length=64), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("initial_cash", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("transaction_cost_bps", sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column("final_equity", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_backtest_experiments_symbol"), "backtest_experiments", ["symbol"], unique=False)

    op.create_table(
        "backtest_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.Column("total_return", sa.Numeric(precision=18, scale=10), nullable=True),
        sa.Column("annualized_return", sa.Numeric(precision=18, scale=10), nullable=True),
        sa.Column("volatility", sa.Numeric(precision=18, scale=10), nullable=True),
        sa.Column("annualized_volatility", sa.Numeric(precision=18, scale=10), nullable=True),
        sa.Column("sharpe_ratio", sa.Numeric(precision=18, scale=10), nullable=True),
        sa.Column("max_drawdown", sa.Numeric(precision=18, scale=10), nullable=True),
        sa.Column("historical_var_95", sa.Numeric(precision=18, scale=10), nullable=True),
        sa.Column("expected_shortfall_95", sa.Numeric(precision=18, scale=10), nullable=True),
        sa.ForeignKeyConstraint(["experiment_id"], ["backtest_experiments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("experiment_id"),
    )
    op.create_index(op.f("ix_backtest_metrics_experiment_id"), "backtest_metrics", ["experiment_id"], unique=False)

    op.create_table(
        "backtest_trades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("side", sa.String(length=8), nullable=False),
        sa.Column("price", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("shares", sa.Integer(), nullable=False),
        sa.Column("gross_value", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("transaction_cost", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("cash_after_trade", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.ForeignKeyConstraint(["experiment_id"], ["backtest_experiments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_backtest_trades_date"), "backtest_trades", ["date"], unique=False)
    op.create_index(op.f("ix_backtest_trades_experiment_id"), "backtest_trades", ["experiment_id"], unique=False)

    op.create_table(
        "backtest_equity_points",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("cash", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("shares", sa.Integer(), nullable=False),
        sa.Column("close_price", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("position_value", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("total_equity", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("daily_return", sa.Numeric(precision=18, scale=10), nullable=True),
        sa.ForeignKeyConstraint(["experiment_id"], ["backtest_experiments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_backtest_equity_points_date"), "backtest_equity_points", ["date"], unique=False)
    op.create_index(op.f("ix_backtest_equity_points_experiment_id"), "backtest_equity_points", ["experiment_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_backtest_equity_points_experiment_id"), table_name="backtest_equity_points")
    op.drop_index(op.f("ix_backtest_equity_points_date"), table_name="backtest_equity_points")
    op.drop_table("backtest_equity_points")

    op.drop_index(op.f("ix_backtest_trades_experiment_id"), table_name="backtest_trades")
    op.drop_index(op.f("ix_backtest_trades_date"), table_name="backtest_trades")
    op.drop_table("backtest_trades")

    op.drop_index(op.f("ix_backtest_metrics_experiment_id"), table_name="backtest_metrics")
    op.drop_table("backtest_metrics")

    op.drop_index(op.f("ix_backtest_experiments_symbol"), table_name="backtest_experiments")
    op.drop_table("backtest_experiments")
