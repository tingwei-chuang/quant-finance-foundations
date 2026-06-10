"""Parameter sweeps and the anatomy of curve-fitting (Week 8).

Trying many parameter values and keeping the best one is the most common way
quantitative researchers fool themselves: the in-sample winner is partly
(often mostly) the luckiest, not the best. This module provides a deliberately
simple signal family — trailing momentum with a single ``lookback`` knob — and
a sweep helper that reports in-sample and out-of-sample performance side by
side so the gap is impossible to miss.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..finance.metrics import sharpe_ratio
from .engine import run_backtest


def trailing_momentum_signal(returns: pd.Series, lookback: int) -> pd.Series:
    """Return the sign of the trailing ``lookback``-period mean return.

    The signal at time ``t`` uses returns up to **and including** ``t`` — it
    still needs the usual one-period lag before it can be traded, which
    :func:`~quant_math_roadmap.backtesting.engine.run_backtest` applies
    internally. Early rows whose window is not yet full are ``0`` (flat), never
    back-filled.

    Args:
        returns: Per-period simple returns.
        lookback: Trailing window length (``>= 1``).

    Returns:
        A series in ``{-1, 0, +1}`` aligned to ``returns``.
    """
    if lookback < 1:
        raise ValueError("lookback must be >= 1")
    trailing_mean = returns.rolling(window=lookback).mean()
    return np.sign(trailing_mean).fillna(0.0)


def lookback_parameter_sweep(
    returns: pd.Series,
    lookbacks: list[int],
    *,
    in_sample_fraction: float = 0.6,
    cost_per_unit_turnover: float = 0.0005,
    frequency: str = "daily",
) -> pd.DataFrame:
    """Backtest the momentum signal for every lookback, split IS vs OOS.

    For each candidate ``lookback`` the **whole-sample** strategy is computed
    once (the rolling signal only ever sees the past, so this is legitimate),
    then its net returns are split chronologically into an in-sample (IS)
    segment and an out-of-sample (OOS) segment, and the Sharpe ratio of each
    segment is reported.

    The teaching point: pick the row with the best ``is_sharpe`` and check its
    ``oos_sharpe``. On noise-like return series the IS winner's OOS
    performance is usually unremarkable — that gap *is* curve-fitting.

    Args:
        returns: Per-period simple returns of the traded asset.
        lookbacks: Candidate trailing-window lengths.
        in_sample_fraction: Fraction of the sample (chronologically first)
            treated as in-sample, in ``(0, 1)``.
        cost_per_unit_turnover: Proportional cost passed to the engine.
        frequency: Data frequency for Sharpe annualisation.

    Returns:
        A ``DataFrame`` indexed by lookback with columns ``is_sharpe``,
        ``oos_sharpe``, ``is_total_return``, ``oos_total_return`` and
        ``avg_turnover``.
    """
    if not lookbacks:
        raise ValueError("lookbacks must be non-empty")
    if not 0.0 < in_sample_fraction < 1.0:
        raise ValueError("in_sample_fraction must lie in (0, 1)")
    n = len(returns)
    split_at = int(n * in_sample_fraction)
    if split_at < 2 or n - split_at < 2:
        raise ValueError("sample too short for the requested in_sample_fraction")

    rows = []
    for lookback in lookbacks:
        signal = trailing_momentum_signal(returns, lookback)
        result = run_backtest(
            signal,
            returns,
            signal_lag=1,
            cost_per_unit_turnover=cost_per_unit_turnover,
        )
        is_net = result.net_returns.iloc[:split_at]
        oos_net = result.net_returns.iloc[split_at:]
        rows.append(
            {
                "lookback": lookback,
                "is_sharpe": sharpe_ratio(is_net, frequency=frequency),
                "oos_sharpe": sharpe_ratio(oos_net, frequency=frequency),
                "is_total_return": float((1.0 + is_net).prod() - 1.0),
                "oos_total_return": float((1.0 + oos_net).prod() - 1.0),
                "avg_turnover": float(
                    (result.positions - result.positions.shift(1).fillna(0.0)).abs().mean()
                ),
            }
        )
    return pd.DataFrame(rows).set_index("lookback")
