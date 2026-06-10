"""Tests for the P4 feature batch.

Covers: Sortino/Calmar, PSR / expected-max-Sharpe / DSR, robust (HC) OLS
standard errors, the circular block bootstrap, Ledoit-Wolf covariance,
bond duration/convexity, the American binomial pricer and finite-difference
Greeks, gap (purged) walk-forward splits, the multi-asset portfolio engine,
and the lookback parameter sweep.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quant_math_roadmap.backtesting.engine import run_backtest, run_portfolio_backtest
from quant_math_roadmap.backtesting.sweeps import (
    lookback_parameter_sweep,
    trailing_momentum_signal,
)
from quant_math_roadmap.data.synthetic import generate_ar1_series
from quant_math_roadmap.finance.derivatives import (
    binomial_american_option,
    binomial_european_option,
    binomial_greeks,
)
from quant_math_roadmap.finance.fixed_income import (
    bond_convexity,
    bond_price,
    macaulay_duration,
    modified_duration,
)
from quant_math_roadmap.finance.metrics import (
    calmar_ratio,
    deflated_sharpe_ratio,
    expected_max_sharpe,
    probabilistic_sharpe_ratio,
    sharpe_ratio,
    sortino_ratio,
)
from quant_math_roadmap.finance.portfolio import ledoit_wolf_covariance
from quant_math_roadmap.math.statistics import (
    block_bootstrap_mean_ci,
    bootstrap_mean_ci,
    ols_fit,
)
from quant_math_roadmap.time_series.splits import (
    expanding_window_splits,
    rolling_window_splits,
)

pytest.importorskip("statsmodels")
import statsmodels.api as sm  # noqa: E402


# ---------- Sortino / Calmar ----------
def test_sortino_known_value() -> None:
    # Hand-checkable: excess = returns (rf=0, target=0).
    r = pd.Series([0.02, -0.01, 0.03, -0.02])
    downside = np.sqrt(np.mean([0.0, 0.01**2, 0.0, 0.02**2]))
    expected = (r.mean() / downside) * np.sqrt(252)
    assert sortino_ratio(r) == pytest.approx(expected)


def test_sortino_zero_when_no_downside() -> None:
    r = pd.Series([0.01, 0.02, 0.005, 0.03])
    assert sortino_ratio(r) == 0.0


def test_sortino_exceeds_sharpe_for_upside_skewed_returns() -> None:
    # Big gains, small losses: total vol >> downside vol.
    rng = np.random.default_rng(0)
    r = pd.Series(np.where(rng.random(2000) < 0.2, 0.05, -0.005))
    assert sortino_ratio(r) > sharpe_ratio(r) > 0


def test_calmar_known_value() -> None:
    r = pd.Series([0.10, -0.20, 0.05] * 4)
    equity = (1.0 + r).cumprod()
    cagr = float(equity.iloc[-1]) ** (252 / len(r)) - 1.0
    mdd = abs(float((equity / equity.cummax() - 1.0).min()))
    assert calmar_ratio(r) == pytest.approx(cagr / mdd)


def test_calmar_zero_without_drawdown() -> None:
    r = pd.Series([0.01] * 30)
    assert calmar_ratio(r) == 0.0


# ---------- PSR / expected max SR / DSR ----------
def test_psr_high_for_strong_strategy() -> None:
    rng = np.random.default_rng(1)
    strong = pd.Series(rng.normal(0.002, 0.01, 1000))  # per-period SR ~0.2
    assert probabilistic_sharpe_ratio(strong) > 0.99


def test_psr_inconclusive_for_pure_noise() -> None:
    # A skill-less series must not look confidently skilled. (The exact value
    # wanders with the sample mean's luck, so only the upper bound is tight.)
    rng = np.random.default_rng(2)
    noise = pd.Series(rng.normal(0.0, 0.01, 4000))
    assert probabilistic_sharpe_ratio(noise) < 0.9


def test_psr_increases_with_sample_length() -> None:
    rng = np.random.default_rng(3)
    base = rng.normal(0.0005, 0.01, 4000)
    short = probabilistic_sharpe_ratio(pd.Series(base[:250]))
    long = probabilistic_sharpe_ratio(pd.Series(base))
    # Same data-generating process, more evidence -> more confident PSR.
    assert long > short


def test_expected_max_sharpe_monotone_in_trials() -> None:
    values = [expected_max_sharpe(n, sr_std=0.1) for n in (1, 2, 10, 100, 1000)]
    assert values[0] == 0.0
    assert all(b > a for a, b in zip(values[:-1], values[1:], strict=True))


def test_dsr_below_psr_when_many_trials() -> None:
    rng = np.random.default_rng(4)
    r = pd.Series(rng.normal(0.001, 0.01, 750))
    psr = probabilistic_sharpe_ratio(r)
    dsr = deflated_sharpe_ratio(r, n_trials=200, sr_std=0.05)
    assert dsr < psr  # selection penalty must bite


def test_psr_input_validation() -> None:
    with pytest.raises(ValueError, match="four observations"):
        probabilistic_sharpe_ratio(pd.Series([0.01, 0.02]))
    with pytest.raises(ValueError, match="zero-volatility"):
        probabilistic_sharpe_ratio(pd.Series([0.01] * 100))
    with pytest.raises(ValueError, match="n_trials"):
        expected_max_sharpe(0, sr_std=0.1)


# ---------- robust OLS standard errors ----------
def _heteroskedastic_data() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(5)
    n = 800
    x = rng.standard_normal(n)
    # Error variance grows with |x| -> classic heteroskedasticity.
    y = 1.0 + 2.0 * x + rng.standard_normal(n) * (0.5 + np.abs(x))
    return x, y


def test_hc0_matches_statsmodels() -> None:
    x, y = _heteroskedastic_data()
    ours = ols_fit(x, y, robust="HC0")
    sm_fit = sm.OLS(y, sm.add_constant(x)).fit(cov_type="HC0")
    np.testing.assert_allclose(ours.std_errors, sm_fit.bse, rtol=1e-8)
    assert ours.cov_type == "HC0"


def test_hc1_matches_statsmodels() -> None:
    x, y = _heteroskedastic_data()
    ours = ols_fit(x, y, robust="HC1")
    sm_fit = sm.OLS(y, sm.add_constant(x)).fit(cov_type="HC1")
    np.testing.assert_allclose(ours.std_errors, sm_fit.bse, rtol=1e-8)


def test_robust_changes_se_not_coefficients() -> None:
    x, y = _heteroskedastic_data()
    classic = ols_fit(x, y)
    robust = ols_fit(x, y, robust="HC1")
    np.testing.assert_allclose(classic.params, robust.params)
    # Under real heteroskedasticity the slope's robust SE must differ.
    assert robust.std_errors[1] != pytest.approx(classic.std_errors[1], rel=1e-3)


def test_robust_rejects_unknown_estimator() -> None:
    with pytest.raises(ValueError, match="HC0"):
        ols_fit(np.arange(10.0), np.arange(10.0), robust="HC9")


# ---------- block bootstrap ----------
def test_block_bootstrap_reproducible() -> None:
    rng = np.random.default_rng(6)
    x = rng.standard_normal(500)
    a = block_bootstrap_mean_ci(x, block_size=10, seed=0)
    b = block_bootstrap_mean_ci(x, block_size=10, seed=0)
    assert a == b


def test_block_bootstrap_close_to_iid_bootstrap_for_iid_data() -> None:
    rng = np.random.default_rng(7)
    x = rng.standard_normal(2000)
    plain = bootstrap_mean_ci(x, seed=0)
    block = block_bootstrap_mean_ci(x, block_size=1, seed=0)
    # block_size=1 is exactly the iid bootstrap mechanism.
    assert block[1] - block[0] == pytest.approx(plain[1] - plain[0], rel=0.15)


def test_block_bootstrap_wider_than_iid_for_autocorrelated_data() -> None:
    # AR(1) with strong positive autocorrelation: the effective sample size is
    # much smaller than n, which only the block bootstrap acknowledges.
    series = generate_ar1_series(2000, phi=0.9, seed=8)
    x = series.to_numpy()
    plain = bootstrap_mean_ci(x, seed=0)
    block = block_bootstrap_mean_ci(x, block_size=50, seed=0)
    assert (block[1] - block[0]) > 1.5 * (plain[1] - plain[0])


def test_block_bootstrap_validates_block_size() -> None:
    with pytest.raises(ValueError, match="block_size"):
        block_bootstrap_mean_ci(np.arange(10.0), block_size=0)
    with pytest.raises(ValueError, match="block_size"):
        block_bootstrap_mean_ci(np.arange(10.0), block_size=11)


# ---------- Ledoit-Wolf ----------
def test_ledoit_wolf_psd_and_bounded_shrinkage() -> None:
    rng = np.random.default_rng(9)
    rets = pd.DataFrame(rng.normal(0, 0.01, (100, 8)))
    cov, shrink = ledoit_wolf_covariance(rets)
    assert 0.0 <= shrink <= 1.0
    eigs = np.linalg.eigvalsh(cov.to_numpy())
    assert eigs.min() >= -1e-12


def test_ledoit_wolf_matches_sklearn_directly() -> None:
    from sklearn.covariance import LedoitWolf

    rng = np.random.default_rng(10)
    rets = pd.DataFrame(rng.normal(0, 0.01, (150, 5)), columns=list("ABCDE"))
    cov, shrink = ledoit_wolf_covariance(rets)
    ref = LedoitWolf().fit(rets.to_numpy())
    np.testing.assert_allclose(cov.to_numpy(), ref.covariance_)
    assert shrink == pytest.approx(float(ref.shrinkage_))
    assert list(cov.columns) == list("ABCDE")


def test_ledoit_wolf_stabilises_when_assets_outnumber_observations() -> None:
    rng = np.random.default_rng(11)
    rets = pd.DataFrame(rng.normal(0, 0.01, (30, 25)))  # n barely > p
    cov, shrink = ledoit_wolf_covariance(rets)
    # Sample covariance would be near-singular; LW must shrink hard and
    # produce a well-conditioned matrix.
    assert shrink > 0.1
    eigs = np.linalg.eigvalsh(cov.to_numpy())
    assert eigs.min() > 0


# ---------- duration / convexity ----------
def test_zero_coupon_macaulay_equals_maturity() -> None:
    assert macaulay_duration(1000, 0.0, 7, 0.05, coupons_per_year=1) == pytest.approx(7.0)


def test_coupons_pull_duration_below_maturity() -> None:
    assert macaulay_duration(1000, 0.08, 10, 0.05) < 10.0


def test_modified_duration_matches_finite_difference() -> None:
    args = (1000.0, 0.05, 10.0, 0.04)
    price = bond_price(*args, coupons_per_year=2)
    h = 1e-6
    dp = (
        bond_price(1000.0, 0.05, 10.0, 0.04 + h, coupons_per_year=2)
        - bond_price(1000.0, 0.05, 10.0, 0.04 - h, coupons_per_year=2)
    ) / (2 * h)
    assert modified_duration(*args, coupons_per_year=2) == pytest.approx(-dp / price, rel=1e-6)


def test_convexity_matches_finite_difference() -> None:
    args = (1000.0, 0.05, 10.0, 0.04)
    price = bond_price(*args, coupons_per_year=2)
    h = 1e-4
    d2p = (
        bond_price(1000.0, 0.05, 10.0, 0.04 + h, coupons_per_year=2)
        - 2 * price
        + bond_price(1000.0, 0.05, 10.0, 0.04 - h, coupons_per_year=2)
    ) / h**2
    assert bond_convexity(*args, coupons_per_year=2) == pytest.approx(d2p / price, rel=1e-5)


def test_convexity_positive_for_plain_bond() -> None:
    assert bond_convexity(1000, 0.03, 5, 0.06) > 0


# ---------- American options + Greeks ----------
def test_american_call_equals_european_without_dividends() -> None:
    kwargs = {"n_steps": 300, "option_type": "call"}
    eu = binomial_european_option(100, 110, 0.05, 0.25, 1.0, **kwargs)
    am = binomial_american_option(100, 110, 0.05, 0.25, 1.0, **kwargs)
    assert am == pytest.approx(eu, rel=1e-10)


def test_american_put_strictly_above_european_put() -> None:
    kwargs = {"n_steps": 300, "option_type": "put"}
    eu = binomial_european_option(100, 110, 0.08, 0.2, 2.0, **kwargs)
    am = binomial_american_option(100, 110, 0.08, 0.2, 2.0, **kwargs)
    assert am > eu  # early exercise premium for a deep-ish ITM put


def test_american_put_at_least_intrinsic() -> None:
    am = binomial_american_option(70, 100, 0.05, 0.2, 1.0, n_steps=200, option_type="put")
    assert am >= 30.0 - 1e-9


def test_american_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        binomial_american_option(-1, 100, 0.05, 0.2, 1.0)
    with pytest.raises(ValueError, match="option_type"):
        binomial_american_option(100, 100, 0.05, 0.2, 1.0, option_type="straddle")


def test_greeks_signs_and_ranges() -> None:
    call = binomial_greeks(100, 100, 0.05, 0.2, 1.0, option_type="call")
    put = binomial_greeks(100, 100, 0.05, 0.2, 1.0, option_type="put")
    assert 0.0 < call["delta"] < 1.0
    assert -1.0 < put["delta"] < 0.0
    assert call["vega"] > 0
    assert call["theta"] < 0  # long options decay
    assert call["rho"] > 0 > put["rho"]


def test_delta_parity_call_minus_put_is_one() -> None:
    # C - P is linear in S with slope exactly 1, so FD deltas differ by 1.
    call = binomial_greeks(100, 105, 0.04, 0.25, 1.0, option_type="call")
    put = binomial_greeks(100, 105, 0.04, 0.25, 1.0, option_type="put")
    assert call["delta"] - put["delta"] == pytest.approx(1.0, abs=1e-9)


def test_greeks_american_style_supported() -> None:
    g = binomial_greeks(100, 110, 0.05, 0.25, 1.0, option_type="put", option_style="american")
    assert -1.0 <= g["delta"] <= 0.0
    with pytest.raises(ValueError, match="option_style"):
        binomial_greeks(100, 100, 0.05, 0.2, 1.0, option_style="bermudan")


# ---------- purged (gap) splits ----------
def test_expanding_gap_is_respected() -> None:
    splits = list(expanding_window_splits(100, initial_train_size=40, test_size=10, gap=5))
    assert splits  # at least one split must fit
    for s in splits:
        assert s.test_index.min() - s.train_index.max() == 5 + 1


def test_rolling_gap_is_respected() -> None:
    splits = list(rolling_window_splits(100, train_size=30, test_size=10, gap=7))
    assert splits
    for s in splits:
        assert s.test_index.min() - s.train_index.max() == 7 + 1
        assert len(s.train_index) == 30


def test_gap_zero_reproduces_plain_behaviour() -> None:
    plain = list(expanding_window_splits(80, initial_train_size=30, test_size=10))
    gapped = list(expanding_window_splits(80, initial_train_size=30, test_size=10, gap=0))
    assert len(plain) == len(gapped)
    for a, b in zip(plain, gapped, strict=True):
        np.testing.assert_array_equal(a.test_index, b.test_index)


def test_gap_reduces_split_count_near_the_end() -> None:
    no_gap = list(expanding_window_splits(100, initial_train_size=80, test_size=10, gap=0))
    big_gap = list(expanding_window_splits(100, initial_train_size=80, test_size=10, gap=15))
    assert len(no_gap) >= 1
    assert len(big_gap) == 0  # 80 + 15 + 10 > 100


def test_gap_validation() -> None:
    with pytest.raises(ValueError, match="gap"):
        list(expanding_window_splits(50, initial_train_size=10, gap=-1))


# ---------- multi-asset portfolio engine ----------
@pytest.fixture
def panel() -> pd.DataFrame:
    idx = pd.bdate_range("2021-01-01", periods=250)
    rng = np.random.default_rng(12)
    return pd.DataFrame(rng.normal(0.0003, 0.01, (250, 3)), index=idx, columns=list("ABC"))


def test_portfolio_engine_single_asset_reduces_to_run_backtest(panel: pd.DataFrame) -> None:
    returns = panel["A"]
    signal = trailing_momentum_signal(returns, 20)
    single = run_backtest(signal, returns, signal_lag=1, cost_per_unit_turnover=0.001)
    multi = run_portfolio_backtest(
        signal.to_frame("A"),
        returns.to_frame("A"),
        weight_lag=1,
        cost_per_unit_turnover=0.001,
    )
    pd.testing.assert_series_equal(single.net_returns, multi.net_returns, check_names=False)


def test_portfolio_engine_lags_weights(panel: pd.DataFrame) -> None:
    weights = pd.DataFrame(1 / 3, index=panel.index, columns=panel.columns)
    result = run_portfolio_backtest(weights, panel, weight_lag=1)
    # First period must be flat: no weights known before the start.
    assert (result.positions.iloc[0] == 0.0).all()
    assert result.gross_returns.iloc[0] == 0.0


def test_portfolio_engine_costs_reduce_performance(panel: pd.DataFrame) -> None:
    rng = np.random.default_rng(13)
    weights = pd.DataFrame(
        rng.dirichlet(np.ones(3), size=len(panel)), index=panel.index, columns=panel.columns
    )
    free = run_portfolio_backtest(weights, panel, cost_per_unit_turnover=0.0)
    costly = run_portfolio_backtest(weights, panel, cost_per_unit_turnover=0.002)
    assert costly.summary()["total_net_return"] < free.summary()["total_net_return"]
    assert (costly.turnover >= 0).all()


def test_portfolio_engine_validates_inputs(panel: pd.DataFrame) -> None:
    weights = pd.DataFrame(1 / 3, index=panel.index, columns=panel.columns)
    with pytest.raises(ValueError, match="weight_lag"):
        run_portfolio_backtest(weights, panel, weight_lag=0)
    with pytest.raises(ValueError, match="columns"):
        run_portfolio_backtest(weights[["A", "B"]], panel[["B", "A"]])


def test_portfolio_engine_static_weights_match_rebalanced_average(panel: pd.DataFrame) -> None:
    weights = pd.DataFrame(1 / 3, index=panel.index, columns=panel.columns)
    result = run_portfolio_backtest(weights, panel, cost_per_unit_turnover=0.0)
    expected = panel.mean(axis=1)
    # After the lag period, returns equal the equal-weighted average.
    pd.testing.assert_series_equal(
        result.gross_returns.iloc[1:], expected.iloc[1:], check_names=False
    )


# ---------- parameter sweep ----------
def test_momentum_signal_no_lookahead() -> None:
    rng = np.random.default_rng(14)
    r = pd.Series(rng.normal(0, 0.01, 100))
    sig = trailing_momentum_signal(r, 10)
    # Window not yet full -> flat, never back-filled.
    assert (sig.iloc[:9] == 0.0).all()
    assert set(np.unique(sig)) <= {-1.0, 0.0, 1.0}
    with pytest.raises(ValueError, match="lookback"):
        trailing_momentum_signal(r, 0)


def test_sweep_outputs_well_formed(panel: pd.DataFrame) -> None:
    sweep = lookback_parameter_sweep(panel["A"], [5, 10, 20, 60])
    assert list(sweep.index) == [5, 10, 20, 60]
    assert {"is_sharpe", "oos_sharpe", "is_total_return", "oos_total_return"} <= set(sweep.columns)
    assert sweep.notna().all().all()


def test_sweep_validation(panel: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="lookbacks"):
        lookback_parameter_sweep(panel["A"], [])
    with pytest.raises(ValueError, match="in_sample_fraction"):
        lookback_parameter_sweep(panel["A"], [5], in_sample_fraction=1.5)
