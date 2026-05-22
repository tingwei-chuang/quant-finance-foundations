"""Minimal forecasting models and baselines (Week 8).

Two beliefs drive this module:

1. **Lag features must never see the future.** ``x_t`` may use information up
   to time ``t`` only. The :func:`make_lag_features` helper enforces this by
   construction.
2. **A forecast is worthless without a baseline.** A model that cannot beat
   "predict the historical mean" or "predict zero" has learned nothing useful.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..math.linear_algebra import add_intercept, ols_beta


def make_lag_features(
    series: pd.Series, n_lags: int, *, dropna: bool = True
) -> pd.DataFrame:
    """Build a lagged-feature matrix for autoregressive modelling.

    Column ``lag_k`` holds ``series`` shifted forward by ``k`` periods, so the
    row labelled ``t`` contains only values from ``t-1, t-2, ..., t-n_lags`` —
    strictly past information. Pairing these features with the *current*
    ``series`` value as the target therefore never leaks the future.

    Args:
        series: The series to lag.
        n_lags: Number of lags (positive).
        dropna: When ``True``, drop the initial rows whose lags are undefined.

    Returns:
        A ``DataFrame`` with columns ``lag_1 .. lag_{n_lags}``.
    """
    if n_lags < 1:
        raise ValueError("n_lags must be >= 1")
    frame = pd.DataFrame(
        {f"lag_{k}": series.shift(k) for k in range(1, n_lags + 1)},
        index=series.index,
    )
    return frame.dropna() if dropna else frame


def historical_mean_forecast(train: pd.Series) -> float:
    """Return the simplest sensible baseline: the in-sample mean.

    For (near) zero-autocorrelation return series this is genuinely hard to
    beat, which is exactly why it is a fair benchmark.

    Args:
        train: The training return series.

    Returns:
        The mean of ``train``.
    """
    if train.empty:
        raise ValueError("train series is empty")
    return float(train.mean())


def zero_forecast(_: pd.Series) -> float:
    """Return the 'naive zero' baseline forecast (always ``0.0``).

    For returns, predicting zero is the humble null model: it claims no edge at
    all. Any real forecasting model must beat it out of sample.

    Args:
        _: Unused; kept for a consistent baseline signature.

    Returns:
        ``0.0``.
    """
    return 0.0


@dataclass(frozen=True)
class AR1Model:
    """A fitted AR(1) model ``x_t = const + phi * x_{t-1}``.

    Attributes:
        const: Estimated intercept.
        phi: Estimated autoregressive coefficient.
    """

    const: float
    phi: float

    def predict_next(self, last_value: float) -> float:
        """Forecast the next observation given the most recent value."""
        return self.const + self.phi * last_value


def fit_ar1(series: pd.Series) -> AR1Model:
    """Fit an AR(1) model by ordinary least squares on lagged data.

    Args:
        series: A 1-D time series with at least three observations.

    Returns:
        A fitted :class:`AR1Model`.
    """
    x = np.asarray(series, dtype=float).ravel()
    if x.size < 3:
        raise ValueError("need at least three observations to fit AR(1)")
    y = x[1:]
    lag = x[:-1].reshape(-1, 1)
    beta = ols_beta(add_intercept(lag), y)
    return AR1Model(const=float(beta[0]), phi=float(beta[1]))


@dataclass(frozen=True)
class LinearLagModel:
    """A linear model on lagged features, ``y_t = c + sum_k b_k * lag_k``.

    Attributes:
        coefficients: The full coefficient vector (intercept first).
        n_lags: Number of lag features used.
    """

    coefficients: np.ndarray
    n_lags: int

    def predict(self, lag_values: np.ndarray) -> float:
        """Forecast from an ordered array ``[lag_1, ..., lag_{n_lags}]``."""
        lags = np.asarray(lag_values, dtype=float).ravel()
        if lags.size != self.n_lags:
            raise ValueError(f"expected {self.n_lags} lag values")
        design = np.concatenate([[1.0], lags])
        return float(design @ self.coefficients)


def fit_linear_lag_model(series: pd.Series, n_lags: int) -> LinearLagModel:
    """Fit a linear autoregressive model on ``n_lags`` lagged features.

    Args:
        series: The target series.
        n_lags: Number of lag features.

    Returns:
        A fitted :class:`LinearLagModel`.
    """
    features = make_lag_features(series, n_lags, dropna=True)
    target = series.loc[features.index]
    beta = ols_beta(add_intercept(features.to_numpy()), target.to_numpy())
    return LinearLagModel(coefficients=beta, n_lags=n_lags)


def forecast_error_metrics(
    actual: pd.Series, predicted: pd.Series
) -> dict[str, float]:
    """Return basic point-forecast error metrics.

    Args:
        actual: Realised values.
        predicted: Forecast values (same index as ``actual``).

    Returns:
        A dictionary with mean absolute error (``mae``), root mean squared
        error (``rmse``) and mean error / bias (``bias``).
    """
    a = np.asarray(actual, dtype=float).ravel()
    p = np.asarray(predicted, dtype=float).ravel()
    if a.shape != p.shape:
        raise ValueError("actual and predicted must have the same length")
    if a.size == 0:
        raise ValueError("inputs must be non-empty")
    error = a - p
    return {
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "bias": float(np.mean(error)),
    }
