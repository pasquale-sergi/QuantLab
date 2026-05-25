from datetime import date

import pytest

from app.analytics.metrics import (
    annualized_return,
    annualized_volatility,
    drawdown_series,
    expected_shortfall_95,
    historical_var_95,
    max_drawdown,
    sharpe_ratio,
    total_return,
    volatility,
)


def _sample_returns() -> list[float | None]:
    return [None, 0.10, -0.05, 0.02, -0.03]


def test_total_return_calculation() -> None:
    result = total_return(_sample_returns())
    assert result == pytest.approx(0.033923, rel=1e-6)


def test_annualized_return_calculation() -> None:
    result = annualized_return(_sample_returns())
    assert result == pytest.approx(7.1800579045, rel=1e-6)


def test_volatility_calculation() -> None:
    result = volatility(_sample_returns())
    assert result == pytest.approx(0.0668331255, rel=1e-6)


def test_sharpe_ratio_calculation() -> None:
    result = sharpe_ratio(_sample_returns())
    assert result == pytest.approx(2.3752454704, rel=1e-6)


def test_max_drawdown_calculation() -> None:
    returns_with_dates = [
        (date(2024, 1, 2), None),
        (date(2024, 1, 3), 0.10),
        (date(2024, 1, 4), -0.05),
        (date(2024, 1, 5), 0.02),
        (date(2024, 1, 8), -0.03),
    ]

    result = max_drawdown(returns_with_dates)
    assert result == pytest.approx(-0.06007, rel=1e-6)


def test_historical_var_95_calculation() -> None:
    result = historical_var_95(_sample_returns())
    assert result == pytest.approx(-0.05, rel=1e-12)


def test_expected_shortfall_95_calculation() -> None:
    result = expected_shortfall_95(_sample_returns())
    assert result == pytest.approx(-0.05, rel=1e-12)


def test_annualized_volatility_calculation() -> None:
    result = annualized_volatility(_sample_returns())
    assert result == pytest.approx(1.0609429768, rel=1e-6)


def test_drawdown_series_shape() -> None:
    returns_with_dates = [
        (date(2024, 1, 2), None),
        (date(2024, 1, 3), -0.02),
    ]

    rows = drawdown_series(returns_with_dates)
    assert len(rows) == 2
    assert rows[0].equity == pytest.approx(1.0, rel=1e-12)
    assert rows[0].drawdown == pytest.approx(0.0, rel=1e-12)
    assert rows[1].equity == pytest.approx(0.98, rel=1e-12)
    assert rows[1].drawdown == pytest.approx(-0.02, rel=1e-12)
