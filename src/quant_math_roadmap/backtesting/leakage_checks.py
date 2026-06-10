"""Look-ahead and data-leakage checks (Week 8).

Look-ahead bias — using information that would not have been available in real
time — is the single most common reason a backtest looks brilliant and a live
strategy does not. This module provides:

* the correct signal-to-position alignment (:func:`signal_to_positions`);
* an assertion that catches accidental leakage (:func:`assert_no_lookahead`);
* a deliberately *invalid* leaked strategy (:func:`leaked_strategy_returns`)
  used in the notebook to show what impossible performance looks like.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def signal_to_positions(signal: pd.Series, *, lag: int = 1) -> pd.Series:
    """Shift a signal forward so positions only use past information.

    A signal computed *from data up to and including time ``t``* cannot be
    traded until ``t + 1``. Shifting by ``lag`` (default 1) enforces that: the
    position held while earning the return of period ``t`` was decided using
    information available at ``t - lag``.

    Args:
        signal: The raw signal, indexed by time.
        lag: Number of periods to delay the signal (``>= 1``).

    Returns:
        The lagged position series; the first ``lag`` rows are ``0`` (flat).
    """
    if lag < 1:
        raise ValueError("lag must be >= 1 to avoid look-ahead")
    return signal.shift(lag).fillna(0.0)


def assert_no_lookahead(
    feature: pd.Series,
    target: pd.Series,
    *,
    name: str = "feature",
) -> None:
    """Assert that a feature does not depend on contemporaneous/future targets.

    The check correlates ``feature_t`` with ``target_t`` and with
    ``target_{t+1}``. A feature that legitimately uses only past information
    should not be near-perfectly correlated with the *current or future*
    target. A correlation extremely close to 1 is the fingerprint of leakage
    (for example, accidentally using the realised return as its own predictor).

    This is a heuristic teaching aid, not a formal proof of correctness.

    Args:
        feature: The predictor series.
        target: The series being predicted (e.g. next-period return).
        name: Label used in the error message.

    Raises:
        ValueError: If the feature looks like it leaks the target.
    """
    # Build (feature_t, target_t, target_{t+1}) aligned rows.
    frame = pd.concat(
        [
            feature.rename("feature"),
            target.rename("target_t"),
            target.shift(-1).rename("target_t1"),
        ],
        axis=1,
        join="inner",
    ).dropna()
    if frame.shape[0] < 3:
        return
    f = frame["feature"].to_numpy()
    t0 = frame["target_t"].to_numpy()
    t1 = frame["target_t1"].to_numpy()
    if np.std(f) == 0:
        return

    threshold = 0.999

    def _flag(corr: float, label: str) -> None:
        raise ValueError(
            f"possible leakage: {name!r} is almost perfectly correlated with "
            f"the {label} target (|corr| = {corr:.4f}). A real feature must "
            "be built from past data only."
        )

    if np.std(t0) > 0:
        c0 = abs(float(np.corrcoef(f, t0)[0, 1]))
        if c0 > threshold:
            _flag(c0, "contemporaneous")
    if np.std(t1) > 0:
        c1 = abs(float(np.corrcoef(f, t1)[0, 1]))
        if c1 > threshold:
            _flag(c1, "next-period (future)")


def strategy_returns(positions: pd.Series, asset_returns: pd.Series) -> pd.Series:
    """Combine positions with realised returns into strategy returns.

    The caller is responsible for having already lagged the positions (see
    :func:`signal_to_positions`). This function does *not* shift anything; it
    simply multiplies aligned series.

    Args:
        positions: Position held during each period.
        asset_returns: Realised asset returns for the same periods.

    Returns:
        The per-period strategy return ``position_t * return_t``.
    """
    if not positions.index.equals(asset_returns.index):
        raise ValueError("positions and asset_returns must share an index")
    return positions * asset_returns


def leaked_strategy_returns(asset_returns: pd.Series) -> pd.Series:
    """Return the performance of an INVALID strategy that peeks at the future.

    .. danger::
       This function is **intentionally wrong**. It sets each period's position
       to the *sign of that same period's return* — knowledge that is
       impossible to have before the period ends. It always "predicts"
       correctly and produces absurd, monotonically rising performance.

    It exists only so the Week 8 notebook can show what leakage looks like and
    contrast it with the honest, lagged backtest. Its output must never be
    interpreted as a strategy result.

    Args:
        asset_returns: Realised asset returns.

    Returns:
        The (invalid) leaked strategy returns ``|return_t|``.
    """
    cheating_position = np.sign(asset_returns)
    return cheating_position * asset_returns
