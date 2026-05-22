"""Transaction-cost modelling (Week 8).

Costs are where many backtests quietly die. A strategy that looks excellent on
gross returns can be unprofitable once trading frictions are charged. This
module implements a simple, transparent proportional-cost model and makes the
gross-vs-net gap impossible to ignore.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def position_turnover(positions: pd.Series) -> pd.Series:
    """Compute per-period turnover of a single-asset position series.

    Turnover at time ``t`` is ``|position_t - position_{t-1}|`` — the absolute
    change in exposure that has to be traded. The first period is charged the
    cost of opening the initial position from flat (zero).

    Args:
        positions: Target position (e.g. in ``[-1, 1]``) for each period.

    Returns:
        A non-negative turnover ``Series`` aligned to ``positions``.
    """
    previous = positions.shift(1).fillna(0.0)
    return (positions - previous).abs()


def apply_transaction_costs(
    gross_returns: pd.Series,
    positions: pd.Series,
    *,
    cost_per_unit_turnover: float = 0.0005,
) -> pd.Series:
    """Subtract proportional transaction costs from gross strategy returns.

    The cost charged in period ``t`` is
    ``cost_per_unit_turnover * turnover_t``. With ``cost_per_unit_turnover``
    interpreted as a fraction, ``0.0005`` is 5 basis points per unit of
    turnover — a deliberately round teaching number, not a calibrated estimate.

    .. note::
       This proportional model is a simplification. It does not capture the
       bid-ask spread varying with size, market impact, slippage, or financing
       costs. It is enough to teach *that costs matter*, not to certify a
       strategy as tradable.

    Args:
        gross_returns: Strategy returns *before* costs.
        positions: Position series used to derive turnover (same index).
        cost_per_unit_turnover: Cost charged per unit of turnover.

    Returns:
        Net returns: ``gross_returns - cost``.
    """
    if cost_per_unit_turnover < 0:
        raise ValueError("cost_per_unit_turnover must be non-negative")
    if not gross_returns.index.equals(positions.index):
        raise ValueError("gross_returns and positions must share an index")
    costs = cost_per_unit_turnover * position_turnover(positions)
    return gross_returns - costs


def cost_summary(
    gross_returns: pd.Series,
    net_returns: pd.Series,
) -> dict[str, float]:
    """Summarise the impact of costs as total gross vs net return.

    Args:
        gross_returns: Returns before costs.
        net_returns: Returns after costs.

    Returns:
        A dictionary with total gross return, total net return and the total
        cost drag (gross minus net), all as compounded fractions.
    """
    total_gross = float((1.0 + gross_returns).prod() - 1.0)
    total_net = float((1.0 + net_returns).prod() - 1.0)
    return {
        "total_gross_return": total_gross,
        "total_net_return": total_net,
        "cost_drag": total_gross - total_net,
    }


def annualized_turnover(positions: pd.Series, *, periods_per_year: int = 252) -> float:
    """Return average turnover scaled to an annual figure.

    Args:
        positions: Position series.
        periods_per_year: Periods used to annualise the average.

    Returns:
        The annualised turnover.
    """
    if periods_per_year < 1:
        raise ValueError("periods_per_year must be >= 1")
    return float(position_turnover(positions).mean() * periods_per_year)


def _ensure_series(values: pd.Series | np.ndarray, index: pd.Index) -> pd.Series:
    """Coerce an array-like to a ``Series`` on the given index (internal helper)."""
    if isinstance(values, pd.Series):
        return values
    return pd.Series(np.asarray(values, dtype=float), index=index)
