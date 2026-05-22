"""Tests for portfolio construction and optimisation (Weeks 1-2)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quant_math_roadmap.finance.portfolio import (
    buy_and_hold_weights,
    equal_weights,
    minimum_variance_portfolio,
    portfolio_variance,
    shrinkage_covariance,
)
from quant_math_roadmap.math.linear_algebra import (
    is_positive_semidefinite,
    quadratic_form,
)
from quant_math_roadmap.math.optimization import (
    min_variance_weights,
    min_variance_weights_long_only,
)


@pytest.fixture
def covariance() -> np.ndarray:
    """A small, well-conditioned PSD covariance matrix."""
    rng = np.random.default_rng(7)
    factor = rng.standard_normal((5, 3))
    cov = factor @ factor.T + np.eye(5) * 0.5
    return cov


def test_equal_weights_sum_to_one() -> None:
    w = equal_weights(8)
    assert w.sum() == pytest.approx(1.0)
    assert np.allclose(w, 0.125)


def test_equal_weights_rejects_bad_count() -> None:
    with pytest.raises(ValueError):
        equal_weights(0)


def test_min_variance_weights_sum_to_one(covariance: np.ndarray) -> None:
    w = min_variance_weights(covariance)
    assert w.sum() == pytest.approx(1.0)


def test_min_variance_beats_equal_weight_in_sample(covariance: np.ndarray) -> None:
    mvp = min_variance_weights(covariance)
    eq = equal_weights(covariance.shape[0])
    # By construction the minimum-variance portfolio has the lowest variance.
    assert portfolio_variance(mvp, covariance) <= portfolio_variance(eq, covariance)


def test_min_variance_diagonal_covariance_is_inverse_variance_weighted() -> None:
    # For a diagonal covariance, MVP weight_i is proportional to 1/variance_i.
    variances = np.array([1.0, 4.0, 9.0])
    cov = np.diag(variances)
    w = min_variance_weights(cov)
    expected = (1.0 / variances) / np.sum(1.0 / variances)
    np.testing.assert_allclose(w, expected, rtol=1e-9)


def test_min_variance_long_only_has_no_negative_weights() -> None:
    # Construct a covariance that pushes the unconstrained solution short.
    rng = np.random.default_rng(11)
    factor = rng.standard_normal((6, 2))
    cov = factor @ factor.T + np.eye(6) * 0.1
    w = min_variance_weights_long_only(cov)
    assert w.sum() == pytest.approx(1.0, abs=1e-6)
    assert (w >= -1e-9).all()


def test_min_variance_rejects_singular_covariance() -> None:
    singular = np.ones((3, 3))  # rank 1, not invertible
    with pytest.raises(ValueError):
        min_variance_weights(singular)


def test_min_variance_singular_covariance_with_ridge_succeeds() -> None:
    singular = np.ones((3, 3))
    w = min_variance_weights(singular, ridge=1e-3)
    assert w.sum() == pytest.approx(1.0)


def test_portfolio_variance_matches_quadratic_form(covariance: np.ndarray) -> None:
    w = equal_weights(covariance.shape[0])
    assert portfolio_variance(w, covariance) == pytest.approx(quadratic_form(w, covariance))


def test_minimum_variance_portfolio_wrapper(covariance: np.ndarray) -> None:
    cov_df = pd.DataFrame(covariance)
    w_uncon = minimum_variance_portfolio(cov_df)
    w_long = minimum_variance_portfolio(cov_df, long_only=True)
    assert w_uncon.sum() == pytest.approx(1.0)
    assert (w_long >= -1e-9).all()


def test_shrinkage_covariance_is_psd_and_blends() -> None:
    rng = np.random.default_rng(3)
    returns = pd.DataFrame(rng.standard_normal((120, 5)), columns=list("ABCDE"))
    shrunk = shrinkage_covariance(returns, shrinkage=0.3)
    assert is_positive_semidefinite(shrunk.to_numpy())
    # Shrinkage 0 returns the raw sample covariance.
    raw = shrinkage_covariance(returns, shrinkage=0.0)
    np.testing.assert_allclose(raw.to_numpy(), returns.cov(ddof=1).to_numpy())


def test_buy_and_hold_weights_drift_without_rebalancing() -> None:
    idx = pd.bdate_range("2021-01-01", periods=3)
    # Asset A always rises, asset B always falls.
    returns = pd.DataFrame({"A": [0.10, 0.10, 0.10], "B": [-0.10, -0.10, -0.10]}, index=idx)
    weights = buy_and_hold_weights(np.array([0.5, 0.5]), returns)
    # Winner's weight should strictly increase, loser's should decrease.
    assert weights["A"].is_monotonic_increasing
    assert weights["B"].is_monotonic_decreasing
    # Weights still form a valid allocation each period.
    np.testing.assert_allclose(weights.sum(axis=1).to_numpy(), 1.0)
