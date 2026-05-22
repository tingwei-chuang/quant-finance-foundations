"""Risk and performance metrics (Weeks 1 and 4).

Two ideas are enforced throughout this module:

1. **Annualisation is an explicit assumption.** Every annualised metric
   depends on how many periods fit in a year. That number lives in one place,
   :data:`PERIODS_PER_YEAR`, and must be passed deliberately. The code never
   silently assumes daily data.
2. **Risk-adjusted metrics are fragile.** The Sharpe ratio, in particular, is
   an *estimate* with its own sampling error and is easy to inflate. The
   helpers carry that warning in their docstrings.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

type PandasData = pd.Series | pd.DataFrame

PERIODS_PER_YEAR: dict[str, int] = {
    "daily": 252,
    "weekly": 52,
    "monthly": 12,
    "quarterly": 4,
    "annual": 1,
}
"""Trading periods per year, keyed by data frequency.

Centralising this mapping is a deliberate anti-bug measure: annualising weekly
data with ``252`` overstates volatility by roughly ``sqrt(252/52) ~ 2.2x``.
"""


def periods_per_year(frequency: str) -> int:
    """Look up the number of periods per year for a named frequency.

    Args:
        frequency: One of the keys of :data:`PERIODS_PER_YEAR` (e.g. ``"daily"``).

    Returns:
        The periods-per-year integer.
    """
    key = frequency.lower()
    if key not in PERIODS_PER_YEAR:
        raise ValueError(f"unknown frequency {frequency!r}; choose from {sorted(PERIODS_PER_YEAR)}")
    return PERIODS_PER_YEAR[key]


def annualized_mean(returns: PandasData, *, frequency: str = "daily") -> float | pd.Series:
    """Annualise the mean period return by scaling with periods-per-year.

    This uses the simple linear scaling ``mean * periods``. It is the standard
    convention for *arithmetic* mean returns; it is not the same as a
    compounded (geometric) annual return.

    Args:
        returns: Per-period returns.
        frequency: Data frequency used to look up periods-per-year.

    Returns:
        The annualised mean return.
    """
    scale = periods_per_year(frequency)
    return returns.mean() * scale


def annualized_volatility(returns: PandasData, *, frequency: str = "daily") -> float | pd.Series:
    """Annualise return volatility using the square-root-of-time rule.

    Volatility scales with ``sqrt(periods)`` under the (idealised) assumption
    of independent, identically distributed returns. Real returns show
    volatility clustering, so this is an approximation — a point made in the
    Week 7 notebook.

    Args:
        returns: Per-period returns.
        frequency: Data frequency used to look up periods-per-year.

    Returns:
        The annualised standard deviation of returns.
    """
    scale = periods_per_year(frequency)
    return returns.std(ddof=1) * np.sqrt(scale)


def sharpe_ratio(
    returns: pd.Series,
    *,
    frequency: str = "daily",
    risk_free_rate: float = 0.0,
) -> float:
    """Compute an annualised Sharpe ratio.

    .. warning::
       The Sharpe ratio is an *estimate*. With only a year or two of data its
       confidence interval is wide; a backtested Sharpe of 2 can easily be
       consistent with a true Sharpe of 0. It also ignores skew, fat tails and
       autocorrelation. Treat it as one diagnostic among many, never as proof.

    Args:
        returns: Per-period returns of a single strategy.
        frequency: Data frequency used for annualisation.
        risk_free_rate: Annual risk-free rate, subtracted on a per-period basis.

    Returns:
        The annualised Sharpe ratio, or ``0.0`` if volatility is zero.
    """
    scale = periods_per_year(frequency)
    per_period_rf = risk_free_rate / scale
    excess = returns - per_period_rf
    vol = excess.std(ddof=1)
    if vol == 0 or np.isnan(vol):
        return 0.0
    return float(excess.mean() / vol * np.sqrt(scale))


def max_drawdown(equity_curve: pd.Series) -> float:
    """Return the maximum peak-to-trough drawdown of an equity curve.

    Args:
        equity_curve: A cumulative-value (wealth) series, strictly positive.

    Returns:
        The most negative drawdown as a fraction (e.g. ``-0.25`` for -25%).
    """
    if (equity_curve <= 0).any():
        raise ValueError("equity_curve must be strictly positive")
    running_peak = equity_curve.cummax()
    drawdown = equity_curve / running_peak - 1.0
    return float(drawdown.min())


def covariance_matrix(
    returns: pd.DataFrame, *, annualize: bool = False, frequency: str = "daily"
) -> pd.DataFrame:
    """Compute the sample covariance matrix of asset returns.

    Args:
        returns: A ``DataFrame`` of per-period returns, one column per asset.
        annualize: When ``True``, scale the covariance by periods-per-year.
        frequency: Data frequency used when ``annualize`` is set.

    Returns:
        The covariance matrix as a labelled ``DataFrame``.
    """
    cov = returns.cov(ddof=1)
    if annualize:
        cov = cov * periods_per_year(frequency)
    return cov


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Compute the sample correlation matrix of asset returns.

    Args:
        returns: A ``DataFrame`` of per-period returns.

    Returns:
        The correlation matrix as a labelled ``DataFrame``.
    """
    return returns.corr()


def turnover(weights: pd.DataFrame) -> pd.Series:
    """Compute per-period portfolio turnover from a weight schedule.

    Turnover at time ``t`` is ``sum(|w_t - w_{t-1}|)``: the total absolute
    weight that had to be traded. It drives transaction costs.

    Args:
        weights: A ``DataFrame`` of portfolio weights over time.

    Returns:
        A ``Series`` of per-period turnover (the first period is ``0``).
    """
    changes = weights.diff().abs().sum(axis=1)
    changes.iloc[0] = 0.0
    return changes
