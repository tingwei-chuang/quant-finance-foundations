"""Tests for return calculations and risk metrics (Week 1)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quant_math_roadmap.finance.metrics import (
    PERIODS_PER_YEAR,
    annualized_volatility,
    correlation_matrix,
    covariance_matrix,
    max_drawdown,
    periods_per_year,
)
from quant_math_roadmap.finance.returns import (
    cumulative_returns,
    log_returns,
    log_to_simple,
    simple_returns,
    simple_to_log,
    total_return,
)


@pytest.fixture
def prices() -> pd.Series:
    """A short, hand-checkable price series."""
    idx = pd.bdate_range("2020-01-01", periods=4)
    return pd.Series([100.0, 110.0, 99.0, 108.9], index=idx, name="P")


def test_simple_returns_known_values(prices: pd.Series) -> None:
    result = simple_returns(prices)
    expected = pd.Series([0.10, -0.10, 0.10], index=prices.index[1:], name="P")
    pd.testing.assert_series_equal(result, expected)


def test_log_returns_known_values(prices: pd.Series) -> None:
    result = log_returns(prices)
    expected = np.log(prices / prices.shift(1)).dropna()
    pd.testing.assert_series_equal(result, expected)


def test_log_returns_are_additive(prices: pd.Series) -> None:
    # Sum of daily log returns equals the log of the total price ratio.
    lr = log_returns(prices)
    assert lr.sum() == pytest.approx(np.log(prices.iloc[-1] / prices.iloc[0]))


def test_simple_log_round_trip(prices: pd.Series) -> None:
    simple = simple_returns(prices)
    round_tripped = log_to_simple(simple_to_log(simple))
    pd.testing.assert_series_equal(round_tripped, simple)


def test_returns_drop_leading_nan(prices: pd.Series) -> None:
    assert len(simple_returns(prices)) == len(prices) - 1
    assert simple_returns(prices, dropna=False).iloc[0] != simple_returns(
        prices, dropna=False
    ).iloc[0]  # leading value is NaN


def test_returns_reject_non_positive_prices() -> None:
    bad = pd.Series([100.0, 0.0, 50.0])
    with pytest.raises(ValueError, match="strictly positive"):
        simple_returns(bad)


def test_cumulative_return_matches_total(prices: pd.Series) -> None:
    r = simple_returns(prices)
    growth = cumulative_returns(r)
    assert growth.iloc[-1] - 1.0 == pytest.approx(total_return(r))
    assert total_return(r) == pytest.approx(prices.iloc[-1] / prices.iloc[0] - 1.0)


def test_covariance_matrix_shape_and_symmetry() -> None:
    rng = np.random.default_rng(0)
    returns = pd.DataFrame(rng.standard_normal((200, 4)), columns=list("ABCD"))
    cov = covariance_matrix(returns)
    assert cov.shape == (4, 4)
    np.testing.assert_allclose(cov.to_numpy(), cov.to_numpy().T)


def test_correlation_matrix_unit_diagonal() -> None:
    rng = np.random.default_rng(1)
    returns = pd.DataFrame(rng.standard_normal((200, 3)), columns=list("XYZ"))
    corr = correlation_matrix(returns)
    np.testing.assert_allclose(np.diag(corr.to_numpy()), np.ones(3))
    assert (corr.to_numpy() <= 1.0 + 1e-9).all()


def test_annualization_uses_explicit_frequency() -> None:
    rng = np.random.default_rng(2)
    returns = pd.Series(rng.normal(0.0, 0.01, size=1000))
    daily = annualized_volatility(returns, frequency="daily")
    weekly = annualized_volatility(returns, frequency="weekly")
    # Same numbers, different annualisation factor -> different results.
    ratio = daily / weekly
    assert ratio == pytest.approx(np.sqrt(252 / 52), rel=1e-9)


def test_periods_per_year_lookup() -> None:
    assert periods_per_year("daily") == 252
    assert periods_per_year("WEEKLY") == 52
    assert PERIODS_PER_YEAR["monthly"] == 12
    with pytest.raises(ValueError, match="unknown frequency"):
        periods_per_year("hourly")


def test_max_drawdown_known_curve() -> None:
    equity = pd.Series([1.0, 1.2, 0.9, 1.1, 0.6, 1.0])
    # Worst peak-to-trough: 1.2 -> 0.6 == -50%.
    assert max_drawdown(equity) == pytest.approx(-0.5)


def test_max_drawdown_monotone_curve_is_zero() -> None:
    equity = pd.Series([1.0, 1.1, 1.2, 1.3])
    assert max_drawdown(equity) == pytest.approx(0.0)
