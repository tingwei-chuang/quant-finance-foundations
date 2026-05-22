"""Portfolio construction (Weeks 1 and 2).

This module builds the small set of portfolios the roadmap compares:
equal-weight, minimum-variance, and (for context) the buy-and-hold weight
*drift* that a one-time allocation experiences. It also includes a simple
shrinkage covariance estimator, because Week 2 shows that minimum-variance
weights are only as good as the covariance matrix they are built from.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..math.linear_algebra import quadratic_form
from ..math.optimization import min_variance_weights, min_variance_weights_long_only


def equal_weights(n_assets: int) -> np.ndarray:
    """Return equal portfolio weights ``1/n`` for ``n`` assets.

    Args:
        n_assets: Number of assets (positive).

    Returns:
        A length-``n`` array of identical weights summing to one.
    """
    if n_assets < 1:
        raise ValueError("n_assets must be >= 1")
    return np.full(n_assets, 1.0 / n_assets)


def portfolio_variance(weights: np.ndarray, covariance: np.ndarray) -> float:
    """Return the portfolio variance ``w^T Sigma w``.

    Args:
        weights: Portfolio weights.
        covariance: Asset covariance matrix.

    Returns:
        The (non-negative, for a PSD covariance) portfolio variance.
    """
    return quadratic_form(weights, covariance)


def portfolio_return(weights: np.ndarray, mean_returns: np.ndarray) -> float:
    """Return the expected portfolio return ``w^T mu``.

    Args:
        weights: Portfolio weights.
        mean_returns: Per-asset expected returns.

    Returns:
        The weighted-average expected return.
    """
    w = np.asarray(weights, dtype=float).ravel()
    mu = np.asarray(mean_returns, dtype=float).ravel()
    if w.shape != mu.shape:
        raise ValueError("weights and mean_returns must have the same length")
    return float(w @ mu)


def minimum_variance_portfolio(
    covariance: pd.DataFrame | np.ndarray,
    *,
    long_only: bool = False,
    ridge: float = 0.0,
) -> np.ndarray:
    """Construct global minimum-variance portfolio weights.

    Args:
        covariance: Asset covariance matrix (``DataFrame`` or array).
        long_only: When ``True``, forbid short positions (``w >= 0``).
        ridge: Optional diagonal stabilisation for the unconstrained solver.

    Returns:
        Portfolio weights summing to one.
    """
    cov = np.asarray(covariance, dtype=float)
    if long_only:
        return min_variance_weights_long_only(cov)
    return min_variance_weights(cov, ridge=ridge)


def shrinkage_covariance(returns: pd.DataFrame, *, shrinkage: float = 0.2) -> pd.DataFrame:
    """Shrink a sample covariance matrix towards a scaled-identity target.

    The estimator is ``(1 - delta) * S + delta * F`` where ``S`` is the sample
    covariance and ``F`` is a diagonal matrix holding the average sample
    variance. Shrinkage trades a little bias for a large reduction in variance,
    which is exactly what unstable minimum-variance weights need.

    Args:
        returns: A ``DataFrame`` of asset returns.
        shrinkage: Shrinkage intensity ``delta`` in ``[0, 1]``. ``0`` returns
            the raw sample covariance; ``1`` returns the diagonal target.

    Returns:
        The shrunk covariance matrix as a labelled ``DataFrame``.
    """
    if not 0.0 <= shrinkage <= 1.0:
        raise ValueError("shrinkage must lie in [0, 1]")
    sample = returns.cov(ddof=1)
    avg_var = float(np.mean(np.diag(sample.to_numpy())))
    target = pd.DataFrame(
        np.eye(sample.shape[0]) * avg_var,
        index=sample.index,
        columns=sample.columns,
    )
    return (1.0 - shrinkage) * sample + shrinkage * target


def buy_and_hold_weights(initial_weights: np.ndarray, asset_returns: pd.DataFrame) -> pd.DataFrame:
    """Track how a one-time allocation's weights *drift* with asset returns.

    This is the heart of a correct buy-and-hold baseline: you allocate once and
    then *do nothing*. Winners grow as a share of the portfolio and losers
    shrink, so the weights move away from their starting point on their own —
    no rebalancing trades, no turnover, no transaction costs.

    Args:
        initial_weights: Weights at the first period (must sum to one).
        asset_returns: Per-period simple returns, one column per asset.

    Returns:
        A ``DataFrame`` of drifting weights aligned to ``asset_returns``.
    """
    w0 = np.asarray(initial_weights, dtype=float).ravel()
    if w0.shape[0] != asset_returns.shape[1]:
        raise ValueError("initial_weights length must match the number of assets")
    if not np.isclose(w0.sum(), 1.0):
        raise ValueError("initial_weights must sum to one")

    # Wealth in each asset compounds independently from the initial allocation.
    growth = (1.0 + asset_returns).cumprod()
    asset_value = growth * w0
    total_value = asset_value.sum(axis=1)
    return asset_value.div(total_value, axis=0)
