"""Baseline strategies (Week 8).

A predictive strategy must be judged against honest baselines. This module
implements two that are easy to confuse but behave very differently:

* **Buy-and-hold** — allocate once and never trade again. Weights *drift* with
  performance. Zero turnover, zero costs.
* **Equal-weight rebalanced** — reset to equal weights every period. This
  *is* an active strategy: it generates turnover and therefore costs.

Treating a rebalanced portfolio as if it were "just holding" is a classic
backtesting mistake; keeping the two functions separate makes the distinction
explicit.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..finance.metrics import turnover as weight_turnover
from ..finance.portfolio import buy_and_hold_weights, equal_weights


def buy_and_hold_equity(
    asset_returns: pd.DataFrame,
    *,
    initial_weights: np.ndarray | None = None,
    initial_capital: float = 1.0,
) -> pd.Series:
    """Compute the equity curve of a true buy-and-hold portfolio.

    Capital is allocated **once** at the start. After that the portfolio is
    left alone: each asset's value compounds at its own return and the blended
    equity curve is their sum. There is no rebalancing, so weights drift —
    which is the correct, turnover-free baseline behaviour.

    Args:
        asset_returns: Per-period simple returns, one column per asset.
        initial_weights: Starting weights (must sum to one). Defaults to equal
            weight.
        initial_capital: Starting portfolio value.

    Returns:
        The portfolio equity curve, starting at ``initial_capital``.
    """
    n_assets = asset_returns.shape[1]
    weights = equal_weights(n_assets) if initial_weights is None else np.asarray(
        initial_weights, dtype=float
    )
    if not np.isclose(weights.sum(), 1.0):
        raise ValueError("initial_weights must sum to one")

    # Each asset's capital compounds independently from its initial allocation.
    growth = (1.0 + asset_returns).cumprod()
    asset_value = initial_capital * growth * weights
    return asset_value.sum(axis=1)


def equal_weight_rebalanced_equity(
    asset_returns: pd.DataFrame,
    *,
    initial_capital: float = 1.0,
) -> pd.Series:
    """Compute the equity curve of an equal-weight, every-period-rebalanced portfolio.

    Unlike buy-and-hold, this strategy trades the portfolio back to equal
    weights at the start of **every** period. That is a real, active decision:
    it sells winners and buys losers, generating turnover and (once costs are
    applied) a cost drag. Label it as a strategy, not as "holding".

    Args:
        asset_returns: Per-period simple returns.
        initial_capital: Starting portfolio value.

    Returns:
        The rebalanced equity curve.
    """
    n_assets = asset_returns.shape[1]
    weights = equal_weights(n_assets)
    # With constant equal weights, the portfolio return each period is just the
    # equal-weighted average of asset returns.
    portfolio_returns = asset_returns.to_numpy() @ weights
    equity = initial_capital * np.cumprod(1.0 + portfolio_returns)
    return pd.Series(equity, index=asset_returns.index, name="equal_weight_rebalanced")


def baseline_turnover_comparison(asset_returns: pd.DataFrame) -> dict[str, float]:
    """Contrast the realised turnover of the two baselines.

    Buy-and-hold turns over only once (the initial purchase); the rebalanced
    portfolio turns over every period it has to correct weight drift.

    Args:
        asset_returns: Per-period simple returns.

    Returns:
        A dictionary with the total turnover of each baseline.
    """
    n_assets = asset_returns.shape[1]
    initial = equal_weights(n_assets)

    bah_weights = buy_and_hold_weights(initial, asset_returns)
    bah_turnover = float(weight_turnover(bah_weights).sum())

    rebalanced_weights = pd.DataFrame(
        np.tile(initial, (len(asset_returns), 1)),
        index=asset_returns.index,
        columns=asset_returns.columns,
    )
    # Drift within a period, then snap back to equal weight next period.
    drifted = (1.0 + asset_returns) * rebalanced_weights
    drifted = drifted.div(drifted.sum(axis=1), axis=0)
    rebalance_trades = (rebalanced_weights - drifted.shift(1)).abs().sum(axis=1)
    rebalance_trades.iloc[0] = 1.0  # initial purchase from flat
    rebalanced_turnover = float(rebalance_trades.sum())

    return {
        "buy_and_hold_turnover": bah_turnover,
        "equal_weight_rebalanced_turnover": rebalanced_turnover,
    }
