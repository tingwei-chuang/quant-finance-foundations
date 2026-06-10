"""Coverage for previously-untested public APIs (P1-2, P1-3) and regressions
for several P0/P1 fixes that don't fit neatly into the existing test files.

This file targets the named gaps in the engineering roadmap:
- `sharpe_ratio` (the most glaring miss for a quant-education repo)
- `annualized_mean`, `turnover` (finance.metrics)
- `buy_and_hold_benchmark`, `information_coefficient` (backtesting.engine)
- `quadratic_gradient`, `quadratic_hessian`, `taylor_quadratic_approximation`
- `nearest_psd`
- `forecast_error_metrics`, `fit_linear_lag_model`
- `simulate_bernoulli`
- The previously-untested validation branches of `binomial_european_option`,
  `bond_price`, `yield_to_maturity` and the `adf_stationarity_test` API.
- The `discount_factor` negative-rate guard (P0-3 regression).
- The `assert_no_lookahead` future-shift detection (P0-6 regression).
- The new buy-and-hold turnover semantics (P0-7 regression).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quant_math_roadmap.backtesting.baselines import (
    baseline_turnover_comparison,
    buy_and_hold_equity,
)
from quant_math_roadmap.backtesting.costs import (
    annualized_turnover,
    apply_transaction_costs,
)
from quant_math_roadmap.backtesting.engine import (
    buy_and_hold_benchmark,
    information_coefficient,
)
from quant_math_roadmap.backtesting.leakage_checks import assert_no_lookahead
from quant_math_roadmap.finance.derivatives import (
    binomial_european_option,
    put_call_parity_gap,
)
from quant_math_roadmap.finance.fixed_income import (
    bond_price,
    discount_factor,
    yield_to_maturity,
)
from quant_math_roadmap.finance.metrics import (
    annualized_mean,
    sharpe_ratio,
    turnover,
)
from quant_math_roadmap.math.linear_algebra import (
    is_positive_semidefinite,
    nearest_psd,
)
from quant_math_roadmap.math.optimization import (
    min_variance_weights_long_only,
    quadratic_gradient,
    quadratic_hessian,
    taylor_quadratic_approximation,
)
from quant_math_roadmap.math.probability import simulate_bernoulli
from quant_math_roadmap.time_series.diagnostics import (
    adf_stationarity_test,
    autocorrelation,
)
from quant_math_roadmap.time_series.forecasting import (
    fit_linear_lag_model,
    forecast_error_metrics,
)


# ---------- finance.metrics ----------
def test_sharpe_ratio_known_value() -> None:
    # Constant 0.001 daily return, zero std -> defined return path with 0 vol.
    constant = pd.Series([0.001] * 252)
    assert sharpe_ratio(constant) == 0.0  # zero-vol guard


def test_sharpe_ratio_matches_manual_calculation() -> None:
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(0.001, 0.01, 252))
    expected = (r.mean() / r.std(ddof=1)) * np.sqrt(252)
    assert sharpe_ratio(r) == pytest.approx(expected)


def test_sharpe_ratio_uses_explicit_frequency() -> None:
    r = pd.Series([0.001] * 52 + [0.002] * 52)
    daily = sharpe_ratio(r, frequency="daily")
    weekly = sharpe_ratio(r, frequency="weekly")
    # Sharpe scales with sqrt of annualisation factor.
    assert daily / weekly == pytest.approx(np.sqrt(252 / 52))


def test_sharpe_ratio_subtracts_risk_free_rate() -> None:
    rng = np.random.default_rng(1)
    r = pd.Series(rng.normal(0.0005, 0.01, 1000))
    without_rf = sharpe_ratio(r, risk_free_rate=0.0)
    with_rf = sharpe_ratio(r, risk_free_rate=0.05)
    # A positive risk-free rate must lower the Sharpe ratio.
    assert with_rf < without_rf


def test_annualized_mean_scales_with_frequency() -> None:
    r = pd.Series([0.001] * 100)
    assert annualized_mean(r, frequency="daily") == pytest.approx(0.001 * 252)
    assert annualized_mean(r, frequency="monthly") == pytest.approx(0.001 * 12)


def test_turnover_first_period_is_zero() -> None:
    w = pd.DataFrame(
        {"A": [0.5, 0.5, 0.6], "B": [0.5, 0.5, 0.4]},
        index=pd.bdate_range("2021-01-01", periods=3),
    )
    t = turnover(w)
    assert t.iloc[0] == 0.0  # first period anchored to zero by convention
    assert t.iloc[1] == 0.0  # no change
    assert t.iloc[2] == pytest.approx(0.2)  # |0.6-0.5| + |0.4-0.5|


# ---------- backtesting.costs / engine ----------
def test_annualized_turnover_actually_scales() -> None:
    # P1-4 strengthening: 'scales' test now actually verifies scaling.
    positions = pd.Series([1.0, -1.0] * 50)
    t252 = annualized_turnover(positions, periods_per_year=252)
    t126 = annualized_turnover(positions, periods_per_year=126)
    assert t252 == pytest.approx(2.0 * t126)


def test_buy_and_hold_benchmark_matches_cumulative_returns() -> None:
    idx = pd.bdate_range("2021-01-01", periods=10)
    r = pd.Series([0.01] * 10, index=idx)
    eq = buy_and_hold_benchmark(r, initial_capital=100.0)
    assert eq.iloc[-1] == pytest.approx(100.0 * (1.01**10))
    assert (eq.diff().dropna() > 0).all()  # monotone for positive returns


def test_information_coefficient_perfect_signal_is_one() -> None:
    idx = pd.bdate_range("2021-01-01", periods=50)
    rng = np.random.default_rng(7)
    forward = pd.Series(rng.standard_normal(50), index=idx)
    ic = information_coefficient(forward, forward)
    assert ic == pytest.approx(1.0)


def test_information_coefficient_is_zero_for_constant_signal() -> None:
    idx = pd.bdate_range("2021-01-01", periods=50)
    rng = np.random.default_rng(8)
    forward = pd.Series(rng.standard_normal(50), index=idx)
    flat = pd.Series([1.0] * 50, index=idx)
    assert information_coefficient(flat, forward) == 0.0


def test_cost_drag_is_strictly_positive_when_trading() -> None:
    # P1-4 strengthening: was `>= 0`, which would pass for identity functions.
    idx = pd.bdate_range("2021-01-01", periods=20)
    gross = pd.Series([0.0] * 20, index=idx)
    positions = pd.Series([1.0, -1.0] * 10, index=idx)  # flips every period
    net = apply_transaction_costs(gross, positions, cost_per_unit_turnover=0.001)
    assert (gross - net).sum() > 0


# ---------- backtesting.baselines (P0-7 regression) ----------
def test_buy_and_hold_turnover_is_one_not_drift() -> None:
    """A true buy-and-hold portfolio trades **once** and never again."""
    idx = pd.bdate_range("2021-01-01", periods=200)
    rng = np.random.default_rng(0)
    rets = pd.DataFrame(rng.normal(0.0, 0.02, (200, 3)), index=idx, columns=list("ABC"))
    summary = baseline_turnover_comparison(rets)
    assert summary["buy_and_hold_turnover"] == pytest.approx(1.0)
    # The (correctly labelled) drift figure is still exposed for teaching.
    assert summary["buy_and_hold_drift"] > 0
    # Rebalancing trades opening + ongoing -> strictly larger than buy-and-hold.
    assert summary["equal_weight_rebalanced_turnover"] > summary["buy_and_hold_turnover"]


def test_buy_and_hold_equity_uses_initial_capital() -> None:
    idx = pd.bdate_range("2021-01-01", periods=4)
    rets = pd.DataFrame({"A": [0.0, 0.0, 0.0, 0.0], "B": [0.0, 0.0, 0.0, 0.0]}, index=idx)
    eq = buy_and_hold_equity(rets, initial_capital=1000.0)
    assert eq.iloc[0] == pytest.approx(1000.0)
    assert (eq == 1000.0).all()


# ---------- backtesting.leakage_checks (P0-6 regression) ----------
def test_assert_no_lookahead_catches_future_shifted_feature() -> None:
    rng = np.random.default_rng(0)
    target = pd.Series(rng.normal(0, 0.01, 300))
    future_feat = target.shift(-1)
    with pytest.raises(ValueError, match="future"):
        assert_no_lookahead(future_feat, target, name="future_shift")


# ---------- finance.fixed_income ----------
def test_discount_factor_rejects_pathologically_negative_rate() -> None:
    # Regression for P0-3.
    with pytest.raises(ValueError, match="non-positive"):
        discount_factor(-2.0, 2.0)
    with pytest.raises(ValueError, match="non-positive"):
        discount_factor(-1.5, 2.5)


def test_discount_factor_accepts_mild_negative_rate() -> None:
    # Negative rates < 100% are legitimate (think central-bank policy rates).
    df = discount_factor(-0.01, 1.0)
    assert df > 1.0
    assert df == pytest.approx(1.0 / (1.0 + (-0.01)))


def test_bond_price_rejects_non_integer_period_count() -> None:
    with pytest.raises(ValueError, match="whole number"):
        bond_price(1000.0, 0.05, 4.25, 0.04, coupons_per_year=2)


def test_yield_to_maturity_bracket_failure_raises() -> None:
    # An impossibly high price (>> face + all coupons) cannot be matched by any
    # yield in the bisection bracket.
    with pytest.raises(ValueError, match="bracket"):
        yield_to_maturity(
            price=1e9,
            face_value=1000.0,
            coupon_rate=0.05,
            years_to_maturity=5.0,
            coupons_per_year=2,
        )


# ---------- finance.derivatives (P1-5: tighter parity check + direct gap test) ----------
def test_put_call_parity_holds_to_machine_precision() -> None:
    spot, strike, rate, vol, T = 100.0, 105.0, 0.04, 0.25, 1.0
    call = binomial_european_option(spot, strike, rate, vol, T, n_steps=500, option_type="call")
    put = binomial_european_option(spot, strike, rate, vol, T, n_steps=500, option_type="put")
    gap = put_call_parity_gap(call, put, spot, strike, rate, T)
    # Was abs=1e-2 in the original test; CRR parity holds to ~1e-9 here.
    assert gap == pytest.approx(0.0, abs=1e-8)


def test_put_call_parity_gap_known_value() -> None:
    # Construct a deliberate parity violation and confirm the gap.
    spot, strike, rate, T = 100.0, 100.0, 0.05, 1.0
    discounted_strike = strike * np.exp(-rate * T)
    expected = (5.0 - 1.0) - (spot - discounted_strike)
    assert put_call_parity_gap(5.0, 1.0, spot, strike, rate, T) == pytest.approx(expected)


def test_binomial_rejects_extreme_volatility_or_rate() -> None:
    # Risk-neutral probability falls outside [0, 1] when the up/down moves
    # become too small to bracket the gross risk-free move.
    with pytest.raises(ValueError, match="risk-neutral"):
        binomial_european_option(100.0, 100.0, rate=1.5, volatility=0.01, maturity=1.0, n_steps=10)


# ---------- math.linear_algebra ----------
def test_nearest_psd_repairs_almost_psd_matrix() -> None:
    base = np.array([[2.0, -1.0], [-1.0, 2.0]])
    noisy = base + np.array([[0.0, 0.0], [0.0, -1e-10]])
    repaired = nearest_psd(noisy)
    assert is_positive_semidefinite(repaired)


def test_nearest_psd_clips_to_epsilon() -> None:
    bad = np.array([[1.0, 0.0], [0.0, -0.5]])
    repaired = nearest_psd(bad, epsilon=0.01)
    eigs = np.linalg.eigvalsh(repaired)
    assert eigs.min() >= 0.01 - 1e-12


# ---------- math.optimization ----------
def test_quadratic_gradient_known_value() -> None:
    M = np.array([[2.0, 0.5], [0.5, 3.0]])
    w = np.array([1.0, -2.0])
    # 2 * M @ w = 2 * [2 - 1, 0.5 - 6] = [2, -11]
    np.testing.assert_allclose(quadratic_gradient(M, w), [2.0, -11.0])


def test_quadratic_hessian_is_constant_2M() -> None:
    M = np.array([[1.0, 0.5], [0.5, 4.0]])
    np.testing.assert_allclose(quadratic_hessian(M), 2.0 * M)


def test_taylor_quadratic_approximation_at_base_point_returns_f() -> None:
    f0 = 7.0
    g = np.array([1.0, -2.0])
    H = np.array([[3.0, 0.0], [0.0, 1.0]])
    x0 = np.array([2.0, 3.0])
    # At eval = base, the linear and quadratic terms vanish.
    assert taylor_quadratic_approximation(f0, g, H, x0, x0) == pytest.approx(f0)


def test_taylor_quadratic_approximation_known_step() -> None:
    f0, g, H = 0.0, np.array([1.0]), np.array([[2.0]])
    x0, x = np.array([0.0]), np.array([1.0])
    # f(x) ≈ 0 + 1*1 + 0.5 * 1 * 2 * 1 = 2.0
    assert taylor_quadratic_approximation(f0, g, H, x0, x) == pytest.approx(2.0)


def test_min_variance_long_only_handles_zero_matrix() -> None:
    # Regression for P0-4: ZeroDivisionError previously.
    w = min_variance_weights_long_only(np.zeros((4, 4)), ridge=0.0)
    np.testing.assert_allclose(w, np.full(4, 0.25))


# ---------- math.probability ----------
def test_simulate_bernoulli_proportion_matches_p() -> None:
    draws = simulate_bernoulli(p=0.3, size=20_000, seed=0)
    assert draws.mean() == pytest.approx(0.3, abs=0.02)


def test_simulate_bernoulli_validates_probability() -> None:
    with pytest.raises(ValueError, match="lie in"):
        simulate_bernoulli(p=1.5, size=10)


# ---------- time_series ----------
def test_adf_stationarity_test_keys_and_types() -> None:
    rng = np.random.default_rng(0)
    stationary = pd.Series(rng.normal(0, 1, 500))
    result = adf_stationarity_test(stationary)
    for key in ("adf_statistic", "p_value", "used_lag", "n_obs"):
        assert key in result
        assert isinstance(result[key], float)
    # Pure white noise should look stationary.
    assert result["p_value"] < 0.05


def test_adf_stationarity_test_rejects_nan() -> None:
    s = pd.Series([1.0, np.nan, 3.0, 4.0, 5.0])
    with pytest.raises(ValueError, match="NaN"):
        adf_stationarity_test(s)


def test_autocorrelation_rejects_nan_regression_for_p1_8() -> None:
    s = pd.Series([1.0, np.nan, 3.0, 4.0, 5.0])
    with pytest.raises(ValueError, match="NaN"):
        autocorrelation(s, 1)


def test_fit_linear_lag_model_recovers_signal() -> None:
    rng = np.random.default_rng(0)
    n = 2000
    x = np.zeros(n)
    for t in range(2, n):
        x[t] = 0.6 * x[t - 1] - 0.2 * x[t - 2] + rng.normal(0, 0.5)
    model = fit_linear_lag_model(pd.Series(x), n_lags=2)
    # coefficients = [intercept, lag_1, lag_2]
    assert model.coefficients[1] == pytest.approx(0.6, abs=0.1)
    assert model.coefficients[2] == pytest.approx(-0.2, abs=0.1)


def test_fit_linear_lag_model_predict_shape() -> None:
    rng = np.random.default_rng(1)
    model = fit_linear_lag_model(pd.Series(rng.normal(0, 1, 200)), n_lags=3)
    out = model.predict(np.array([0.1, 0.2, 0.3]))
    assert isinstance(out, float)


def test_forecast_error_metrics_known_values() -> None:
    actual = pd.Series([1.0, 2.0, 3.0])
    pred = pd.Series([1.5, 2.5, 2.0])
    m = forecast_error_metrics(actual, pred)
    # errors = [-0.5, -0.5, 1.0] -> mae=2/3, rmse=sqrt(1.5/3), bias=0
    assert m["bias"] == pytest.approx(0.0)
    assert m["mae"] == pytest.approx(2.0 / 3.0)
    assert m["rmse"] == pytest.approx(np.sqrt(1.5 / 3.0))
