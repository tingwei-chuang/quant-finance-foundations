"""Time-series tools: diagnostics, forecasting, time-aware splitting."""

from __future__ import annotations

from .diagnostics import (
    adf_stationarity_test,
    autocorrelation,
    autocorrelation_function,
    rolling_mean,
    rolling_volatility,
)
from .forecasting import (
    AR1Model,
    LinearLagModel,
    fit_ar1,
    fit_linear_lag_model,
    forecast_error_metrics,
    historical_mean_forecast,
    make_lag_features,
    zero_forecast,
)
from .splits import (
    Split,
    expanding_window_splits,
    rolling_window_splits,
    train_test_split_time,
)

__all__ = [
    "AR1Model",
    "LinearLagModel",
    "Split",
    "adf_stationarity_test",
    "autocorrelation",
    "autocorrelation_function",
    "expanding_window_splits",
    "fit_ar1",
    "fit_linear_lag_model",
    "forecast_error_metrics",
    "historical_mean_forecast",
    "make_lag_features",
    "rolling_mean",
    "rolling_volatility",
    "rolling_window_splits",
    "train_test_split_time",
    "zero_forecast",
]
