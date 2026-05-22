"""Mathematical building blocks: linear algebra, probability, statistics, optimisation."""

from __future__ import annotations

from .linear_algebra import (
    add_intercept,
    eigendecomposition,
    is_positive_semidefinite,
    is_symmetric,
    nearest_psd,
    ols_beta,
    quadratic_form,
)
from .optimization import (
    min_variance_weights,
    min_variance_weights_long_only,
    quadratic_gradient,
    quadratic_hessian,
    taylor_quadratic_approximation,
)
from .probability import (
    empirical_moments,
    running_mean,
    sampling_distribution_of_mean,
    simulate_bernoulli,
    simulate_normal,
)
from .statistics import (
    OLSResult,
    TTestResult,
    bootstrap_mean_ci,
    confidence_interval_mean,
    false_discovery_demo,
    ols_fit,
    one_sample_ttest,
    standard_error_of_mean,
)

__all__ = [
    "OLSResult",
    "TTestResult",
    "add_intercept",
    "bootstrap_mean_ci",
    "confidence_interval_mean",
    "eigendecomposition",
    "empirical_moments",
    "false_discovery_demo",
    "is_positive_semidefinite",
    "is_symmetric",
    "min_variance_weights",
    "min_variance_weights_long_only",
    "nearest_psd",
    "ols_beta",
    "ols_fit",
    "one_sample_ttest",
    "quadratic_form",
    "quadratic_gradient",
    "quadratic_hessian",
    "running_mean",
    "sampling_distribution_of_mean",
    "simulate_bernoulli",
    "simulate_normal",
    "standard_error_of_mean",
    "taylor_quadratic_approximation",
]
