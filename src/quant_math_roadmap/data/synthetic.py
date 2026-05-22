"""Synthetic market-data generators.

Every notebook and test in this repository runs on data produced here. Using
synthetic data keeps the project fully reproducible, removes any dependency on
external data providers, and lets us *design* the statistical properties we
want to teach (known correlation, known volatility regimes, a known AR(1)
coefficient, and so on).

None of these series represent real assets. They are teaching instruments.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR: int = 252
"""Conventional number of trading days in a calendar year (daily annualisation)."""


@dataclass(frozen=True)
class SyntheticConfig:
    """Configuration for a synthetic multi-asset price panel.

    Attributes:
        n_assets: Number of assets (price columns) to generate.
        n_periods: Number of business-day observations.
        start: First date of the business-day index (``YYYY-MM-DD``).
        seed: Random seed; fixing it makes the output fully reproducible.
        annual_drift: Per-asset expected annual log-drift. Either a scalar
            (shared by all assets) or one value per asset.
        annual_vol: Per-asset annual volatility. Scalar or one value per asset.
        average_correlation: Average pairwise correlation between asset
            returns. Must lie in ``[0, 1)``.
        initial_price: Starting price level for every asset.
        market_factor_loading: If positive, a shared market factor is mixed
            into every asset's returns with this loading (adds systematic
            co-movement on top of ``average_correlation``).
        vol_regime_multiplier: Volatility multiplier applied to the second
            half of the sample. ``1.0`` disables the regime shift.
    """

    n_assets: int = 4
    n_periods: int = 756
    start: str = "2018-01-01"
    seed: int = 20240101
    annual_drift: float | list[float] = 0.06
    annual_vol: float | list[float] = 0.20
    average_correlation: float = 0.35
    initial_price: float = 100.0
    market_factor_loading: float = 0.0
    vol_regime_multiplier: float = 1.0
    asset_names: list[str] | None = field(default=None)

    def __post_init__(self) -> None:
        if self.n_assets < 1:
            raise ValueError("n_assets must be >= 1")
        if self.n_periods < 2:
            raise ValueError("n_periods must be >= 2")
        if not 0.0 <= self.average_correlation < 1.0:
            raise ValueError("average_correlation must lie in [0, 1)")
        if self.initial_price <= 0.0:
            raise ValueError("initial_price must be positive")
        if self.vol_regime_multiplier <= 0.0:
            raise ValueError("vol_regime_multiplier must be positive")


def _broadcast(value: float | list[float], n: int, name: str) -> np.ndarray:
    """Broadcast a scalar or length-``n`` sequence into an ``(n,)`` array."""
    arr = np.atleast_1d(np.asarray(value, dtype=float))
    if arr.size == 1:
        return np.full(n, float(arr[0]))
    if arr.size != n:
        raise ValueError(f"{name} must be a scalar or have length {n}")
    return arr


def _equicorrelation_matrix(n: int, rho: float) -> np.ndarray:
    """Return an ``(n, n)`` correlation matrix with constant off-diagonal ``rho``."""
    corr = np.full((n, n), rho, dtype=float)
    np.fill_diagonal(corr, 1.0)
    return corr


def generate_correlated_returns(config: SyntheticConfig) -> pd.DataFrame:
    """Generate a panel of correlated daily *log* returns.

    The model is deliberately simple and transparent:

    * Each asset has a constant daily drift ``mu`` and daily volatility
      ``sigma`` derived from the annual inputs.
    * Cross-asset co-movement comes from a Gaussian copula with an
      equicorrelation matrix, optionally reinforced by a shared market factor.
    * An optional volatility regime shift scales the second half of the sample.

    Args:
        config: Generation parameters.

    Returns:
        A ``DataFrame`` of daily log returns indexed by business day, with one
        column per asset.
    """
    rng = np.random.default_rng(config.seed)
    n, t = config.n_assets, config.n_periods

    annual_drift = _broadcast(config.annual_drift, n, "annual_drift")
    annual_vol = _broadcast(config.annual_vol, n, "annual_vol")

    daily_drift = annual_drift / TRADING_DAYS_PER_YEAR
    daily_vol = annual_vol / np.sqrt(TRADING_DAYS_PER_YEAR)

    corr = _equicorrelation_matrix(n, config.average_correlation)
    chol = np.linalg.cholesky(corr)

    # Standard normal shocks with the target correlation structure.
    independent = rng.standard_normal(size=(t, n))
    correlated = independent @ chol.T

    if config.market_factor_loading > 0.0:
        market = rng.standard_normal(size=(t, 1))
        loading = config.market_factor_loading
        correlated = np.sqrt(1.0 - loading**2) * correlated + loading * market

    # Volatility regime: scale the second half of the sample.
    vol_path = np.ones(t)
    if config.vol_regime_multiplier != 1.0:
        vol_path[t // 2 :] = config.vol_regime_multiplier

    returns = daily_drift + (daily_vol * vol_path[:, None]) * correlated

    index = pd.bdate_range(start=config.start, periods=t, name="date")
    names = config.asset_names or [f"ASSET_{i + 1}" for i in range(n)]
    if len(names) != n:
        raise ValueError(f"asset_names must have length {n}")
    return pd.DataFrame(returns, index=index, columns=names)


def generate_correlated_prices(config: SyntheticConfig) -> pd.DataFrame:
    """Generate a panel of synthetic price series.

    Prices are the cumulative product of ``exp(log_return)`` starting from
    ``config.initial_price``, so they are strictly positive by construction.

    Args:
        config: Generation parameters.

    Returns:
        A ``DataFrame`` of positive prices indexed by business day.
    """
    log_returns = generate_correlated_returns(config)
    growth = np.exp(log_returns.cumsum())
    prices = config.initial_price * growth
    return prices


def generate_ar1_series(
    n_periods: int,
    *,
    phi: float = 0.6,
    sigma: float = 1.0,
    constant: float = 0.0,
    seed: int = 0,
    start: str = "2018-01-01",
) -> pd.Series:
    """Generate a stationary AR(1) process ``x_t = c + phi * x_{t-1} + e_t``.

    Args:
        n_periods: Number of observations.
        phi: Autoregressive coefficient. ``abs(phi) < 1`` keeps the process
            stationary.
        sigma: Standard deviation of the white-noise innovations.
        constant: Additive constant ``c``.
        seed: Random seed.
        start: First date of the business-day index.

    Returns:
        A ``Series`` containing the AR(1) path.
    """
    if n_periods < 1:
        raise ValueError("n_periods must be >= 1")
    rng = np.random.default_rng(seed)
    innovations = rng.normal(scale=sigma, size=n_periods)
    x = np.empty(n_periods)
    # Start the chain at its unconditional mean to avoid a long burn-in.
    x[0] = constant / (1.0 - phi) if abs(phi) < 1.0 else 0.0
    for i in range(1, n_periods):
        x[i] = constant + phi * x[i - 1] + innovations[i]
    index = pd.bdate_range(start=start, periods=n_periods, name="date")
    return pd.Series(x, index=index, name="ar1")


def generate_random_walk(
    n_periods: int,
    *,
    drift: float = 0.0,
    sigma: float = 1.0,
    seed: int = 0,
    start: str = "2018-01-01",
) -> pd.Series:
    """Generate a (non-stationary) random walk with optional drift.

    A random walk is the canonical *non-stationary* counterpart to the AR(1)
    process above; the two are compared in the Week 7 notebook.

    Args:
        n_periods: Number of observations.
        drift: Per-step drift added to each increment.
        sigma: Standard deviation of the increments.
        seed: Random seed.
        start: First date of the business-day index.

    Returns:
        A ``Series`` containing the random-walk path.
    """
    if n_periods < 1:
        raise ValueError("n_periods must be >= 1")
    rng = np.random.default_rng(seed)
    increments = drift + rng.normal(scale=sigma, size=n_periods)
    index = pd.bdate_range(start=start, periods=n_periods, name="date")
    return pd.Series(np.cumsum(increments), index=index, name="random_walk")
