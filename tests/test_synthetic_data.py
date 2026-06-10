"""Tests for the synthetic-data generators."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quant_math_roadmap.data.synthetic import (
    SyntheticConfig,
    generate_ar1_series,
    generate_correlated_prices,
    generate_correlated_returns,
    generate_random_walk,
)


def test_default_config_validates() -> None:
    cfg = SyntheticConfig()
    assert cfg.n_assets >= 1


@pytest.mark.parametrize(
    "kwargs",
    [
        {"n_assets": 0},
        {"n_periods": 1},
        {"average_correlation": 1.0},
        {"average_correlation": -0.1},
        {"initial_price": 0.0},
        {"vol_regime_multiplier": 0.0},
    ],
)
def test_invalid_config_is_rejected(kwargs: dict) -> None:
    base = {"n_periods": 50}
    base.update(kwargs)
    with pytest.raises(ValueError):
        SyntheticConfig(**base)


def test_generated_prices_are_strictly_positive_and_reproducible() -> None:
    cfg = SyntheticConfig(n_assets=4, n_periods=200, seed=123)
    a = generate_correlated_prices(cfg)
    b = generate_correlated_prices(cfg)
    pd.testing.assert_frame_equal(a, b)
    assert (a > 0).all().all()
    assert a.shape == (200, 4)


def test_generated_returns_match_expected_shape_and_index() -> None:
    cfg = SyntheticConfig(n_assets=3, n_periods=50, seed=0)
    r = generate_correlated_returns(cfg)
    assert r.shape == (50, 3)
    assert isinstance(r.index, pd.DatetimeIndex)


def test_market_factor_inflates_average_correlation() -> None:
    base = SyntheticConfig(
        n_assets=4,
        n_periods=2000,
        seed=0,
        average_correlation=0.0,
        market_factor_loading=0.0,
    )
    factor = SyntheticConfig(
        n_assets=4,
        n_periods=2000,
        seed=0,
        average_correlation=0.0,
        market_factor_loading=0.8,
    )
    base_corr = generate_correlated_returns(base).corr().to_numpy()
    factor_corr = generate_correlated_returns(factor).corr().to_numpy()
    # Average off-diagonal correlation should rise once the shared factor is on.
    off = ~np.eye(4, dtype=bool)
    assert factor_corr[off].mean() > base_corr[off].mean() + 0.3


def test_volatility_regime_shift_increases_second_half_vol() -> None:
    cfg = SyntheticConfig(
        n_assets=1,
        n_periods=2000,
        seed=0,
        vol_regime_multiplier=3.0,
    )
    r = generate_correlated_returns(cfg).iloc[:, 0]
    half = len(r) // 2
    first_std = r.iloc[:half].std()
    second_std = r.iloc[half:].std()
    assert second_std > 2.0 * first_std


def test_broadcast_per_asset_drift_and_vol() -> None:
    cfg = SyntheticConfig(
        n_assets=3,
        n_periods=4000,
        seed=0,
        annual_drift=[0.0, 0.0, 0.0],
        annual_vol=[0.05, 0.20, 0.40],
    )
    r = generate_correlated_returns(cfg)
    stds = r.std(ddof=1) * np.sqrt(252)
    # Realised annualised vols should track the configured values fairly well.
    np.testing.assert_allclose(stds.to_numpy(), [0.05, 0.20, 0.40], rtol=0.15)


def test_broadcast_rejects_wrong_length() -> None:
    cfg = SyntheticConfig(
        n_assets=3,
        n_periods=50,
        seed=0,
        annual_vol=[0.1, 0.2],
    )
    with pytest.raises(ValueError, match="annual_vol"):
        generate_correlated_returns(cfg)


def test_ar1_series_is_stationary() -> None:
    s = generate_ar1_series(2000, phi=0.5, seed=0)
    # mean should be near 0 (constant=0, |phi|<1)
    assert abs(s.mean()) < 0.2


def test_ar1_validates_n_periods() -> None:
    with pytest.raises(ValueError, match="n_periods"):
        generate_ar1_series(0)


def test_random_walk_is_seed_reproducible() -> None:
    a = generate_random_walk(100, drift=0.01, seed=0)
    b = generate_random_walk(100, drift=0.01, seed=0)
    pd.testing.assert_series_equal(a, b)


def test_random_walk_validates_n_periods() -> None:
    with pytest.raises(ValueError, match="n_periods"):
        generate_random_walk(0)
