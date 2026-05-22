"""Time-series diagnostics (Week 7).

Before modelling a series you must understand it: is it stationary, does it
show autocorrelation, how does its volatility behave over time? The helpers
here compute autocorrelation, rolling statistics, and a stationarity test, and
are written so a notebook can show the arithmetic rather than hide it.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller


def autocorrelation(series: pd.Series, lag: int) -> float:
    """Return the sample autocorrelation of a series at a single ``lag``.

    The estimator divides by the *full-sample* variance (the standard
    convention, matching :func:`statsmodels.tsa.stattools.acf`): it correlates
    ``x_t`` with ``x_{t-lag}`` using deviations from the overall mean.

    Args:
        series: A 1-D time series.
        lag: Non-negative lag. Lag ``0`` is ``1.0`` by definition.

    Returns:
        The autocorrelation coefficient at ``lag``.
    """
    if lag < 0:
        raise ValueError("lag must be non-negative")
    x = np.asarray(series, dtype=float).ravel()
    n = x.size
    if lag >= n:
        raise ValueError("lag must be smaller than the series length")
    if lag == 0:
        return 1.0
    centred = x - x.mean()
    denominator = float(np.sum(centred**2))
    if denominator == 0.0:
        raise ValueError("series has zero variance; autocorrelation undefined")
    numerator = float(np.sum(centred[lag:] * centred[:-lag]))
    return numerator / denominator


def autocorrelation_function(series: pd.Series, max_lag: int) -> pd.Series:
    """Return the autocorrelation function (ACF) for lags ``0 .. max_lag``.

    Args:
        series: A 1-D time series.
        max_lag: Largest lag to compute.

    Returns:
        A ``Series`` indexed by lag.
    """
    if max_lag < 0:
        raise ValueError("max_lag must be non-negative")
    values = [autocorrelation(series, lag) for lag in range(max_lag + 1)]
    return pd.Series(values, index=pd.RangeIndex(max_lag + 1, name="lag"), name="acf")


def rolling_mean(series: pd.Series, window: int) -> pd.Series:
    """Return the trailing rolling mean.

    Only past and current observations enter each window (pandas' default), so
    the result contains no look-ahead. The first ``window - 1`` values are
    ``NaN`` because the window is not yet full — those rows should *stay*
    missing rather than be back-filled.

    Args:
        series: A 1-D time series.
        window: Rolling-window length (positive).

    Returns:
        The trailing rolling mean.
    """
    if window < 1:
        raise ValueError("window must be >= 1")
    return series.rolling(window=window).mean()


def rolling_volatility(returns: pd.Series, window: int, *, ddof: int = 1) -> pd.Series:
    """Return the trailing rolling standard deviation of returns.

    Rising rolling volatility is the visual signature of *volatility
    clustering* — calm and turbulent periods arrive in runs rather than at
    random.

    Args:
        returns: A return series.
        window: Rolling-window length.
        ddof: Delta degrees of freedom for the standard deviation.

    Returns:
        The trailing rolling volatility.
    """
    if window < 2:
        raise ValueError("window must be >= 2 for a standard deviation")
    return returns.rolling(window=window).std(ddof=ddof)


def adf_stationarity_test(series: pd.Series) -> dict[str, float]:
    """Run an Augmented Dickey-Fuller test for a unit root.

    The ADF null hypothesis is "the series has a unit root" (is
    non-stationary). A small p-value is evidence *against* the unit root, i.e.
    in favour of stationarity. This is a guide, not a proof — interpret it
    alongside the plots.

    Args:
        series: A 1-D time series with no missing values.

    Returns:
        A dictionary with the test statistic, p-value, used lag count and the
        number of observations.
    """
    x = np.asarray(series, dtype=float).ravel()
    if np.isnan(x).any():
        raise ValueError("series must not contain NaN values")
    statistic, p_value, used_lag, n_obs, *_ = adfuller(x, autolag="AIC")
    return {
        "adf_statistic": float(statistic),
        "p_value": float(p_value),
        "used_lag": float(used_lag),
        "n_obs": float(n_obs),
    }
