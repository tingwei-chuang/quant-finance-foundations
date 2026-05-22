"""Synthetic data generation, loading, and validation."""

from __future__ import annotations

from .loaders import load_prices_csv, load_sample_prices, sample_data_dir
from .synthetic import (
    SyntheticConfig,
    generate_ar1_series,
    generate_correlated_prices,
    generate_correlated_returns,
    generate_random_walk,
)
from .validation import ValidationReport, validate_price_frame

__all__ = [
    "SyntheticConfig",
    "ValidationReport",
    "generate_ar1_series",
    "generate_correlated_prices",
    "generate_correlated_returns",
    "generate_random_walk",
    "load_prices_csv",
    "load_sample_prices",
    "sample_data_dir",
    "validate_price_frame",
]
