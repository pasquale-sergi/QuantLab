"""add backtest summary metrics columns

Revision ID: 20260526_02
Revises: 20260526_01
Create Date: 2026-05-26
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260526_02"
down_revision = "20260526_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("backtest_metrics", sa.Column("number_of_trades", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("backtest_metrics", sa.Column("buy_trades", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("backtest_metrics", sa.Column("sell_trades", sa.Integer(), nullable=False, server_default="0"))
    op.add_column(
        "backtest_metrics",
        sa.Column("time_in_market_pct", sa.Numeric(precision=18, scale=10), nullable=False, server_default="0"),
    )
    op.add_column("backtest_metrics", sa.Column("best_day", sa.Numeric(precision=18, scale=10), nullable=True))
    op.add_column("backtest_metrics", sa.Column("worst_day", sa.Numeric(precision=18, scale=10), nullable=True))
    op.add_column(
        "backtest_metrics",
        sa.Column("average_daily_return", sa.Numeric(precision=18, scale=10), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("backtest_metrics", "average_daily_return")
    op.drop_column("backtest_metrics", "worst_day")
    op.drop_column("backtest_metrics", "best_day")
    op.drop_column("backtest_metrics", "time_in_market_pct")
    op.drop_column("backtest_metrics", "sell_trades")
    op.drop_column("backtest_metrics", "buy_trades")
    op.drop_column("backtest_metrics", "number_of_trades")
