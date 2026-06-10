"""Tests that guard against look-ahead bias and data leakage (Week 8).

These are the most important tests in the repository from a methodology
standpoint: they verify that the *correct* pipeline never sees the future, and
that the *intentionally invalid* leaked example is unambiguously labelled and
behaves as the impossible result it is.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quant_math_roadmap.backtesting.engine import run_backtest
from quant_math_roadmap.backtesting.leakage_checks import (
    assert_no_lookahead,
    leaked_strategy_returns,
    signal_to_positions,
    strategy_returns,
)


@pytest.fixture
def returns() -> pd.Series:
    idx = pd.bdate_range("2021-01-01", periods=400)
    rng = np.random.default_rng(0)
    return pd.Series(rng.normal(0.0002, 0.012, 400), index=idx, name="ret")


def test_signal_to_positions_shifts_forward() -> None:
    idx = pd.bdate_range("2021-01-01", periods=5)
    signal = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0], index=idx)
    positions = signal_to_positions(signal, lag=1)
    # Position on day t equals the signal from day t-1.
    assert positions.iloc[0] == 0.0  # nothing known before the start
    for t in range(1, 5):
        assert positions.iloc[t] == signal.iloc[t - 1]


def test_signal_to_positions_rejects_zero_lag() -> None:
    signal = pd.Series([1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="lag must be >= 1"):
        signal_to_positions(signal, lag=0)


def test_position_never_uses_contemporaneous_signal() -> None:
    # The defining property: position_t must not depend on signal_t.
    idx = pd.bdate_range("2021-01-01", periods=50)
    rng = np.random.default_rng(1)
    signal = pd.Series(rng.standard_normal(50), index=idx)
    positions = signal_to_positions(signal, lag=1)
    aligned = pd.concat([positions, signal], axis=1).dropna()
    # Same-day correlation between position and signal must be ~0...
    same_day = aligned.iloc[:, 0].corr(aligned.iloc[:, 1])
    assert abs(same_day) < 0.2
    # ...while position vs lagged signal is perfect.
    assert (
        positions.iloc[1:]
        .reset_index(drop=True)
        .equals(signal.shift(1).iloc[1:].reset_index(drop=True))
    )


def test_assert_no_lookahead_passes_for_lagged_feature(returns: pd.Series) -> None:
    target = returns
    # A properly lagged feature: yesterday's return predicting today's.
    feature = returns.shift(1)
    assert_no_lookahead(feature, target, name="lagged_return")  # must not raise


def test_assert_no_lookahead_catches_leaked_feature(returns: pd.Series) -> None:
    target = returns
    feature = returns.copy()  # the feature *is* the target -> leakage
    with pytest.raises(ValueError, match="leakage"):
        assert_no_lookahead(feature, target, name="leaked_return")


def test_leaked_strategy_is_unrealistically_profitable(returns: pd.Series) -> None:
    """The intentionally invalid leaked example must be obviously impossible."""
    leaked = leaked_strategy_returns(returns)
    honest = strategy_returns(signal_to_positions(np.sign(returns), lag=1), returns)
    leaked_total = (1.0 + leaked).prod() - 1.0
    honest_total = (1.0 + honest).prod() - 1.0
    # The leaked strategy "wins" every single period by construction.
    assert (leaked >= -1e-12).all()
    # Its cumulative result dwarfs the honest backtest -- the tell-tale sign.
    assert leaked_total > honest_total
    assert leaked_total > 1.0  # absurd performance over the sample


def test_leaked_strategy_equals_absolute_return(returns: pd.Series) -> None:
    # Documenting precisely why it is invalid: it captures |r_t| every period,
    # which requires knowing the sign of r_t before the period ends.
    leaked = leaked_strategy_returns(returns)
    np.testing.assert_allclose(leaked.to_numpy(), returns.abs().to_numpy())


def test_honest_backtest_engine_lags_the_signal_internally(
    returns: pd.Series,
) -> None:
    # P1-6: the previous version of this test duplicated the leaked-vs-honest
    # comparison covered in test_leaked_strategy_is_unrealistically_profitable.
    # The engine-specific behavior worth checking is that run_backtest applies
    # the lag for you: feeding the raw sign-of-current-return signal still
    # produces lagged positions and therefore non-leaked returns.
    raw_signal = np.sign(returns)  # would be leaked if used contemporaneously
    result = run_backtest(raw_signal, returns, signal_lag=1, cost_per_unit_turnover=0.0)
    # Reconstruct the "honest" returns by hand and compare.
    expected_positions = signal_to_positions(raw_signal, lag=1)
    expected_returns = strategy_returns(expected_positions, returns)
    pd.testing.assert_series_equal(result.gross_returns, expected_returns, check_names=False)
    # And confirm we are nowhere near the absurd leaked performance.
    leaked_total = (1.0 + leaked_strategy_returns(returns)).prod() - 1.0
    honest_total = (1.0 + result.gross_returns).prod() - 1.0
    assert honest_total < 0.5 * leaked_total


def test_run_backtest_positions_are_lagged(returns: pd.Series) -> None:
    signal = pd.Series(
        np.sign(np.random.default_rng(2).standard_normal(len(returns))),
        index=returns.index,
    )
    result = run_backtest(signal, returns, signal_lag=1)
    # The first position is flat: no signal was available before the start.
    assert result.positions.iloc[0] == 0.0
    # Positions equal the once-lagged signal.
    pd.testing.assert_series_equal(result.positions, signal.shift(1).fillna(0.0), check_names=False)


def test_early_rolling_features_do_not_create_positions() -> None:
    # Missing early rolling features must lead to NO position, never a
    # back-filled one. We emulate a rolling-window signal here.
    idx = pd.bdate_range("2021-01-01", periods=30)
    raw = pd.Series(np.arange(30.0), index=idx)
    rolling_signal = raw.rolling(window=10).mean()  # first 9 entries are NaN
    positions = signal_to_positions(rolling_signal.fillna(0.0), lag=1)
    # The early periods (no full window yet) must hold a flat position.
    assert (positions.iloc[:10] == 0.0).all()
