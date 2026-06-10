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

from .._typing import PandasData

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
    # ``vol == 0`` is too strict: a numerically-constant series produces a
    # tiny but non-zero float std and would otherwise yield an absurd Sharpe.
    if np.isnan(vol) or vol < 1e-12:
        return 0.0
    return float(excess.mean() / vol * np.sqrt(scale))


def sortino_ratio(
    returns: pd.Series,
    *,
    frequency: str = "daily",
    risk_free_rate: float = 0.0,
    target: float = 0.0,
) -> float:
    """Compute an annualised Sortino ratio.

    The Sortino ratio replaces total volatility with **downside deviation**:
    only returns below ``target`` count as risk. The downside deviation is the
    root of the mean *squared shortfall* over **all** observations (the
    standard "target downside deviation" convention — dividing by ``n``, not
    by the number of negative observations).

    .. warning::
       Like the Sharpe ratio, this is an estimate with sampling error, and it
       is even noisier because only a fraction of the sample informs the
       denominator. The usual multiple-testing caveats apply.

    Args:
        returns: Per-period returns of a single strategy.
        frequency: Data frequency used for annualisation.
        risk_free_rate: Annual risk-free rate, subtracted on a per-period basis.
        target: Per-period minimum acceptable return (default ``0``).

    Returns:
        The annualised Sortino ratio, or ``0.0`` if there is no downside
        deviation in the sample (in which case the ratio is undefined).
    """
    scale = periods_per_year(frequency)
    per_period_rf = risk_free_rate / scale
    excess = returns - per_period_rf
    shortfall = np.minimum(excess - target, 0.0)
    downside_dev = float(np.sqrt(np.mean(np.square(shortfall))))
    if np.isnan(downside_dev) or downside_dev < 1e-12:
        return 0.0
    return float((excess.mean() - target) / downside_dev * np.sqrt(scale))


def calmar_ratio(returns: pd.Series, *, frequency: str = "daily") -> float:
    """Compute the Calmar ratio: compound annual growth rate over |max drawdown|.

    Unlike Sharpe/Sortino, the numerator here is the **geometric** (compounded)
    annual return, and the denominator is the worst peak-to-trough loss of the
    compounded equity curve. It penalises strategies whose returns come with
    deep drawdowns even when their per-period volatility looks tame.

    Args:
        returns: Per-period simple returns of a single strategy.
        frequency: Data frequency used to annualise the growth rate.

    Returns:
        The Calmar ratio, or ``0.0`` if the equity curve never draws down
        (the ratio is undefined without a drawdown).
    """
    if len(returns) < 2:
        raise ValueError("need at least two observations")
    scale = periods_per_year(frequency)
    equity = (1.0 + returns).cumprod()
    if (equity <= 0).any():
        raise ValueError("equity curve hit zero or below; Calmar is undefined")
    gross = float(equity.iloc[-1])
    cagr = gross ** (scale / len(returns)) - 1.0
    mdd = max_drawdown(equity)
    if abs(mdd) < 1e-12:
        return 0.0
    return float(cagr / abs(mdd))


def probabilistic_sharpe_ratio(
    returns: pd.Series,
    *,
    benchmark_sr: float = 0.0,
) -> float:
    """Probability that the true (per-period) Sharpe ratio exceeds a benchmark.

    Implements the Probabilistic Sharpe Ratio (PSR) of Bailey & López de Prado
    (2012): the estimated Sharpe ratio is itself a random variable whose
    sampling distribution depends on the sample length and on the skewness and
    kurtosis of returns. PSR converts a point estimate into

    .. math::

       PSR = \\Phi\\!\\left(\\frac{(\\widehat{SR} - SR^*)\\sqrt{n-1}}
       {\\sqrt{1 - \\gamma_3\\widehat{SR}
       + \\tfrac{\\gamma_4 - 1}{4}\\widehat{SR}^2}}\\right)

    where :math:`\\gamma_3` is skewness and :math:`\\gamma_4` is (Pearson,
    normal = 3) kurtosis. Note that both ``benchmark_sr`` and the estimate are
    **per-period** (non-annualised) Sharpe ratios.

    Args:
        returns: Per-period returns of a single strategy.
        benchmark_sr: Per-period Sharpe ratio to beat (``0.0`` = "any skill").

    Returns:
        The probability, in ``[0, 1]``, that the true Sharpe exceeds
        ``benchmark_sr`` given the sample.
    """
    from scipy import stats

    x = np.asarray(returns, dtype=float).ravel()
    n = x.size
    if n < 4:
        raise ValueError("need at least four observations for skew/kurtosis")
    std = x.std(ddof=1)
    if std < 1e-12:
        raise ValueError("zero-volatility returns; Sharpe ratio undefined")
    sr_hat = float(x.mean() / std)
    skew = float(stats.skew(x, bias=False))
    kurt = float(stats.kurtosis(x, fisher=False, bias=False))
    denom_sq = 1.0 - skew * sr_hat + (kurt - 1.0) / 4.0 * sr_hat**2
    if denom_sq <= 0:
        raise ValueError(
            "PSR denominator is non-positive: the skew/kurtosis adjustment "
            "broke down for this sample (extreme higher moments)"
        )
    z = (sr_hat - benchmark_sr) * np.sqrt(n - 1.0) / np.sqrt(denom_sq)
    return float(stats.norm.cdf(z))


def expected_max_sharpe(n_trials: int, *, sr_std: float) -> float:
    """Expected maximum Sharpe ratio across ``n_trials`` skill-less strategies.

    Even when every candidate strategy has a true Sharpe of zero, the *best*
    of ``N`` backtests will show a positive estimated Sharpe purely by luck.
    Under the Bailey & López de Prado (2014) approximation the expected
    maximum is

    .. math::

       E[\\max SR] \\approx \\sigma_{SR}\\left[(1-\\gamma)\\,
       \\Phi^{-1}\\!\\left(1-\\tfrac{1}{N}\\right) + \\gamma\\,
       \\Phi^{-1}\\!\\left(1-\\tfrac{1}{Ne}\\right)\\right]

    with :math:`\\gamma` the Euler–Mascheroni constant.

    Args:
        n_trials: Number of independent strategy trials ``N``.
        sr_std: Cross-trial standard deviation of the estimated Sharpe ratios.

    Returns:
        The expected maximum (per-period) Sharpe under the null of no skill.
        ``0.0`` for ``n_trials == 1`` (no selection effect).
    """
    from scipy import stats

    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")
    if sr_std < 0:
        raise ValueError("sr_std must be non-negative")
    if n_trials == 1:
        return 0.0
    gamma = float(np.euler_gamma)
    z1 = float(stats.norm.ppf(1.0 - 1.0 / n_trials))
    z2 = float(stats.norm.ppf(1.0 - 1.0 / (n_trials * np.e)))
    return float(sr_std * ((1.0 - gamma) * z1 + gamma * z2))


def deflated_sharpe_ratio(
    returns: pd.Series,
    *,
    n_trials: int,
    sr_std: float,
) -> float:
    """Deflated Sharpe Ratio: PSR against the luck-of-the-best-of-N benchmark.

    The Deflated Sharpe Ratio (DSR) asks: *given that this strategy was the
    best of* ``n_trials`` *candidates, what is the probability that its true
    Sharpe is positive rather than a selection artefact?* It is the
    :func:`probabilistic_sharpe_ratio` evaluated against
    :func:`expected_max_sharpe` instead of zero.

    This is the quantitative version of the Week 4 multiple-testing warning:
    the more strategies you tried, the higher the bar your "winner" must clear.

    Args:
        returns: Per-period returns of the **selected** (best) strategy.
        n_trials: How many strategies were tried before selecting this one.
        sr_std: Cross-trial standard deviation of the estimated Sharpe ratios.

    Returns:
        The deflated probability in ``[0, 1]``. Values near ``0.5`` or below
        mean the track record is indistinguishable from selection luck.
    """
    benchmark = expected_max_sharpe(n_trials, sr_std=sr_std)
    return probabilistic_sharpe_ratio(returns, benchmark_sr=benchmark)


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
