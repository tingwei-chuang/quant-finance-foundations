"""Tests for statistical inference and regression (Weeks 3-5)."""

from __future__ import annotations

import numpy as np
import pytest

from quant_math_roadmap.math.probability import (
    empirical_moments,
    running_mean,
    sampling_distribution_of_mean,
    simulate_normal,
)
from quant_math_roadmap.math.statistics import (
    bootstrap_mean_ci,
    confidence_interval_mean,
    false_discovery_demo,
    ols_fit,
    one_sample_ttest,
    standard_error_of_mean,
)

pytest.importorskip("statsmodels")
import statsmodels.api as sm  # noqa: E402


def test_running_mean_converges_to_truth() -> None:
    samples = simulate_normal(mean=2.0, std=1.0, size=50_000, seed=0)
    path = running_mean(samples)
    assert len(path) == len(samples)
    # Law of Large Numbers: the final running mean is close to the true mean.
    assert path[-1] == pytest.approx(2.0, abs=0.05)


def test_simulate_normal_is_reproducible() -> None:
    a = simulate_normal(0.0, 1.0, 1000, seed=42)
    b = simulate_normal(0.0, 1.0, 1000, seed=42)
    np.testing.assert_array_equal(a, b)
    c = simulate_normal(0.0, 1.0, 1000, seed=43)
    assert not np.array_equal(a, c)


def test_empirical_moments_recover_parameters() -> None:
    samples = simulate_normal(mean=5.0, std=2.0, size=100_000, seed=1)
    moments = empirical_moments(samples)
    assert moments["mean"] == pytest.approx(5.0, abs=0.05)
    assert moments["std"] == pytest.approx(2.0, abs=0.05)


def test_clt_sampling_distribution_concentrates() -> None:
    small = sampling_distribution_of_mean(sample_size=5, n_experiments=4000, seed=0)
    large = sampling_distribution_of_mean(sample_size=200, n_experiments=4000, seed=0)
    # Standard error shrinks as sample size grows.
    assert np.std(large) < np.std(small)


def test_standard_error_shrinks_with_sample_size() -> None:
    small = simulate_normal(0.0, 1.0, 100, seed=2)
    large = simulate_normal(0.0, 1.0, 10_000, seed=2)
    assert standard_error_of_mean(large) < standard_error_of_mean(small)


def test_confidence_interval_brackets_mean() -> None:
    samples = simulate_normal(mean=1.0, std=1.0, size=5000, seed=3)
    lower, upper = confidence_interval_mean(samples, confidence=0.95)
    assert lower < np.mean(samples) < upper
    assert lower < 1.0 < upper


def test_bootstrap_ci_is_reproducible_and_sensible() -> None:
    samples = simulate_normal(mean=0.5, std=1.0, size=2000, seed=4)
    ci_a = bootstrap_mean_ci(samples, n_resamples=2000, seed=0)
    ci_b = bootstrap_mean_ci(samples, n_resamples=2000, seed=0)
    assert ci_a == ci_b  # same seed -> identical interval
    assert ci_a[0] < np.mean(samples) < ci_a[1]


def test_one_sample_ttest_detects_nonzero_mean() -> None:
    samples = simulate_normal(mean=0.5, std=1.0, size=2000, seed=5)
    result = one_sample_ttest(samples, popmean=0.0)
    assert result.p_value < 0.01  # clearly different from zero


def test_one_sample_ttest_accepts_zero_mean() -> None:
    samples = simulate_normal(mean=0.0, std=1.0, size=2000, seed=6)
    result = one_sample_ttest(samples, popmean=0.0)
    assert result.p_value > 0.05  # no evidence against the null


def test_ols_matches_statsmodels() -> None:
    rng = np.random.default_rng(10)
    n = 500
    x1 = rng.standard_normal(n)
    x2 = rng.standard_normal(n)
    y = 1.5 + 2.0 * x1 - 0.7 * x2 + rng.normal(0.0, 0.3, n)
    X = np.column_stack([x1, x2])

    ours = ols_fit(X, y, add_const=True)
    sm_model = sm.OLS(y, sm.add_constant(X)).fit()

    np.testing.assert_allclose(ours.params, sm_model.params, rtol=1e-8)
    np.testing.assert_allclose(ours.std_errors, sm_model.bse, rtol=1e-6)
    assert ours.r_squared == pytest.approx(sm_model.rsquared, rel=1e-8)


def test_ols_recovers_known_coefficients() -> None:
    rng = np.random.default_rng(11)
    n = 5000
    x = rng.standard_normal(n)
    y = 3.0 + 0.8 * x + rng.normal(0.0, 0.1, n)
    fit = ols_fit(x, y, add_const=True)
    assert fit.params[0] == pytest.approx(3.0, abs=0.02)
    assert fit.params[1] == pytest.approx(0.8, abs=0.02)


def test_ols_requires_more_observations_than_parameters() -> None:
    with pytest.raises(ValueError):
        ols_fit(np.ones((2, 3)), np.ones(2))


def test_false_discovery_demo_matches_expected_rate() -> None:
    result = false_discovery_demo(n_strategies=500, n_periods=252, alpha=0.05, seed=0)
    # All strategies are pure noise, so every rejection is a false positive.
    # The count should sit near the theoretical expectation alpha * n.
    assert result["n_false_positives"] == pytest.approx(
        result["expected_false_positives"], abs=20
    )
    assert result["n_false_positives"] > 0
