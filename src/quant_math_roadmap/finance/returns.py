"""Return calculations (Week 1).

The first thing any quantitative workflow needs is a *correct* definition of
return. This module implements simple, log, and cumulative returns, and is
careful about the conventions that cause silent bugs: the first observation
has no return, and log returns are additive while simple returns are not.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .._typing import PandasData


def simple_returns(prices: PandasData, *, dropna: bool = True) -> PandasData:
    """Compute simple (arithmetic) returns ``r_t = P_t / P_{t-1} - 1``.

    Args:
        prices: A price ``Series`` or ``DataFrame`` indexed by time.
        dropna: When ``True``, drop the leading ``NaN`` row that has no prior
            price to compare against.

    Returns:
        Simple returns with the same column structure as ``prices``.
    """
    _check_positive(prices)
    returns = prices.pct_change()
    return returns.dropna() if dropna else returns


def log_returns(prices: PandasData, *, dropna: bool = True) -> PandasData:
    """Compute logarithmic returns ``r_t = ln(P_t / P_{t-1})``.

    Log returns are *time-additive*: the log return over a multi-day window is
    the sum of the daily log returns. That property makes them convenient for
    aggregation and for the AR/regression models used later in the roadmap.

    Args:
        prices: A price ``Series`` or ``DataFrame`` indexed by time.
        dropna: When ``True``, drop the leading ``NaN`` row.

    Returns:
        Log returns with the same column structure as ``prices``.
    """
    _check_positive(prices)
    returns = np.log(prices / prices.shift(1))
    return returns.dropna() if dropna else returns


def cumulative_returns(returns: PandasData, *, log_input: bool = False) -> PandasData:
    """Compound a stream of period returns into a growth path.

    A value of ``1.0`` means break-even relative to the start.

    Args:
        returns: Per-period returns.
        log_input: Set ``True`` if ``returns`` are *log* returns; they are then
            summed and exponentiated. Otherwise simple returns are compounded
            multiplicatively.

    Returns:
        The cumulative growth path (gross-of-fees, starting near ``1.0``).
    """
    if log_input:
        return np.exp(returns.cumsum())
    return returns.add(1.0).cumprod()


def total_return(returns: PandasData, *, log_input: bool = False) -> float | pd.Series:
    """Return the total compounded return over the whole sample.

    Args:
        returns: Per-period returns.
        log_input: Whether ``returns`` are log returns.

    Returns:
        The total return as a fraction (``0.10`` == +10%). A scalar for a
        ``Series`` input, or a per-column ``Series`` for a ``DataFrame``.
    """
    gross = np.exp(returns.sum()) if log_input else returns.add(1.0).prod()
    return gross - 1.0


def simple_to_log(simple: PandasData) -> PandasData:
    """Convert simple returns to log returns: ``ln(1 + r)``."""
    return np.log1p(simple)


def log_to_simple(log_ret: PandasData) -> PandasData:
    """Convert log returns to simple returns: ``exp(r) - 1``."""
    return np.expm1(log_ret)


def _check_positive(prices: PandasData) -> None:
    """Raise if any price is non-positive (returns would be undefined)."""
    if (prices <= 0).to_numpy().any():
        raise ValueError("prices must be strictly positive to compute returns")
