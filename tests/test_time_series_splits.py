"""Tests for time-series diagnostics and time-aware splitting (Weeks 7-8)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quant_math_roadmap.data.synthetic import generate_ar1_series
from quant_math_roadmap.time_series.diagnostics import (
    autocorrelation,
    autocorrelation_function,
    rolling_mean,
    rolling_volatility,
)
from quant_math_roadmap.time_series.forecasting import fit_ar1, make_lag_features
from quant_math_roadmap.time_series.splits import (
    Split,
    expanding_window_splits,
    rolling_window_splits,
    train_test_split_time,
)


def test_time_split_preserves_order() -> None:
    split = train_test_split_time(100, test_size=0.25)
    assert split.train_index.max() < split.test_index.min()
    assert len(split.test_index) == 25
    assert len(split.train_index) == 75


def test_time_split_indices_are_contiguous_and_complete() -> None:
    split = train_test_split_time(50, test_size=0.4)
    combined = np.concatenate([split.train_index, split.test_index])
    np.testing.assert_array_equal(combined, np.arange(50))


def test_split_dataclass_rejects_lookahead() -> None:
    with pytest.raises(ValueError, match="look-ahead"):
        Split(train_index=np.array([0, 5]), test_index=np.array([3, 4]))


def test_expanding_window_splits_grow_and_stay_ordered() -> None:
    splits = list(
        expanding_window_splits(100, initial_train_size=40, test_size=10)
    )
    assert len(splits) == 6
    prev_train_size = 0
    for s in splits:
        assert s.train_index.max() < s.test_index.min()
        # Training window always starts at 0 and grows.
        assert s.train_index[0] == 0
        assert len(s.train_index) > prev_train_size
        prev_train_size = len(s.train_index)


def test_rolling_window_splits_have_constant_train_size() -> None:
    splits = list(rolling_window_splits(100, train_size=30, test_size=10))
    assert len(splits) == 7
    for s in splits:
        assert len(s.train_index) == 30
        assert s.train_index.max() < s.test_index.min()


def test_rolling_window_advances_forward() -> None:
    splits = list(rolling_window_splits(100, train_size=30, test_size=10))
    starts = [s.train_index[0] for s in splits]
    assert starts == sorted(starts)
    assert starts[0] == 0


def test_make_lag_features_uses_only_past_values() -> None:
    series = pd.Series(np.arange(10.0))
    features = make_lag_features(series, n_lags=2, dropna=True)
    # Row labelled t must hold values strictly before t.
    for t in features.index:
        assert features.loc[t, "lag_1"] == series.loc[t] - 1
        assert features.loc[t, "lag_2"] == series.loc[t] - 2
        # No lag value may equal or exceed the current observation.
        assert features.loc[t, "lag_1"] < series.loc[t]


def test_make_lag_features_drops_undefined_rows() -> None:
    series = pd.Series(np.arange(10.0))
    features = make_lag_features(series, n_lags=3, dropna=True)
    assert len(features) == 7  # first 3 rows have undefined lags
    assert not features.isna().to_numpy().any()


def test_autocorrelation_lag_zero_is_one() -> None:
    series = pd.Series(np.random.default_rng(0).standard_normal(200))
    assert autocorrelation(series, 0) == pytest.approx(1.0)


def test_autocorrelation_detects_ar1_persistence() -> None:
    ar1 = generate_ar1_series(4000, phi=0.7, seed=0)
    # A strongly persistent AR(1) has clearly positive lag-1 autocorrelation.
    assert autocorrelation(ar1, 1) == pytest.approx(0.7, abs=0.1)


def test_autocorrelation_white_noise_is_near_zero() -> None:
    noise = pd.Series(np.random.default_rng(1).standard_normal(5000))
    assert abs(autocorrelation(noise, 5)) < 0.1


def test_autocorrelation_function_matches_pointwise() -> None:
    series = generate_ar1_series(500, phi=0.5, seed=2)
    acf = autocorrelation_function(series, max_lag=5)
    assert len(acf) == 6
    for lag in range(6):
        assert acf.iloc[lag] == pytest.approx(autocorrelation(series, lag))


def test_rolling_mean_leaves_initial_window_missing() -> None:
    series = pd.Series(np.arange(20.0))
    rm = rolling_mean(series, window=5)
    # The first window-1 values must remain NaN (not back-filled).
    assert rm.iloc[:4].isna().all()
    assert not rm.iloc[4:].isna().any()
    # A full window mean is a plain average of the trailing values.
    assert rm.iloc[4] == pytest.approx(np.mean([0, 1, 2, 3, 4]))


def test_rolling_volatility_window_behaviour() -> None:
    returns = pd.Series(np.random.default_rng(3).normal(0, 0.01, 100))
    rv = rolling_volatility(returns, window=20)
    assert rv.iloc[:19].isna().all()
    assert (rv.dropna() >= 0).all()


def test_fit_ar1_recovers_coefficient() -> None:
    ar1 = generate_ar1_series(8000, phi=0.6, constant=0.0, seed=4)
    model = fit_ar1(ar1)
    assert model.phi == pytest.approx(0.6, abs=0.05)
