"""Statistical inference helpers (Weeks 4 and 5).

The functions here cover estimation (standard errors, confidence intervals),
resampling (the bootstrap), hypothesis testing, and a small ordinary
least-squares fitter that reports the quantities a researcher actually reads:
coefficients, standard errors, t-statistics and R-squared.

A recurring theme of Week 4 is that these tools quantify *sampling
uncertainty* — they do not certify that a strategy is real.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
from scipy import stats

from .linear_algebra import add_intercept

FloatArray = npt.NDArray[np.float64]


def standard_error_of_mean(samples: npt.ArrayLike) -> float:
    """Return the standard error of the sample mean, ``s / sqrt(n)``.

    Args:
        samples: A 1-D sample.

    Returns:
        The estimated standard deviation of the sample-mean estimator.
    """
    x = np.asarray(samples, dtype=float).ravel()
    n = x.size
    if n < 2:
        raise ValueError("need at least two observations")
    return float(np.std(x, ddof=1) / np.sqrt(n))


def confidence_interval_mean(
    samples: npt.ArrayLike, *, confidence: float = 0.95
) -> tuple[float, float]:
    """Return a two-sided ``t`` confidence interval for the population mean.

    Args:
        samples: A 1-D sample.
        confidence: Coverage level in ``(0, 1)``, e.g. ``0.95``.

    Returns:
        The ``(lower, upper)`` bounds of the interval.
    """
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must lie in (0, 1)")
    x = np.asarray(samples, dtype=float).ravel()
    n = x.size
    if n < 2:
        raise ValueError("need at least two observations")
    mean = float(np.mean(x))
    se = standard_error_of_mean(x)
    alpha = 1.0 - confidence
    crit = float(stats.t.ppf(1.0 - alpha / 2.0, df=n - 1))
    return mean - crit * se, mean + crit * se


def bootstrap_mean_ci(
    samples: npt.ArrayLike,
    *,
    confidence: float = 0.95,
    n_resamples: int = 5000,
    seed: int = 0,
) -> tuple[float, float]:
    """Return a percentile bootstrap confidence interval for the mean.

    The bootstrap resamples the data *with replacement* and recomputes the
    statistic many times; the empirical percentiles of those replicates form
    the interval. It makes no normality assumption, which is useful for the
    fat-tailed, skewed return distributions seen in finance.

    Args:
        samples: A 1-D sample.
        confidence: Coverage level in ``(0, 1)``.
        n_resamples: Number of bootstrap resamples.
        seed: Random seed — fixing it makes the interval reproducible.

    Returns:
        The ``(lower, upper)`` percentile-bootstrap bounds.
    """
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must lie in (0, 1)")
    if n_resamples < 1:
        raise ValueError("n_resamples must be >= 1")
    x = np.asarray(samples, dtype=float).ravel()
    n = x.size
    if n < 2:
        raise ValueError("need at least two observations")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_resamples, n))
    means = x[idx].mean(axis=1)
    alpha = 1.0 - confidence
    lower = float(np.quantile(means, alpha / 2.0))
    upper = float(np.quantile(means, 1.0 - alpha / 2.0))
    return lower, upper


@dataclass(frozen=True)
class TTestResult:
    """Result of a one-sample t-test.

    Attributes:
        statistic: The t-statistic.
        p_value: Two-sided p-value.
        df: Degrees of freedom.
        mean: Sample mean.
    """

    statistic: float
    p_value: float
    df: int
    mean: float


def one_sample_ttest(samples: npt.ArrayLike, *, popmean: float = 0.0) -> TTestResult:
    """Test whether the population mean differs from ``popmean``.

    Typical use: test whether a strategy's mean return is different from zero.
    A small p-value is *necessary but not sufficient* evidence — see
    ``docs/math/statistical_inference_cheatsheet.md`` on multiple testing.

    Args:
        samples: A 1-D sample (e.g. strategy returns).
        popmean: The mean under the null hypothesis.

    Returns:
        A :class:`TTestResult`.
    """
    x = np.asarray(samples, dtype=float).ravel()
    n = x.size
    if n < 2:
        raise ValueError("need at least two observations")
    result = stats.ttest_1samp(x, popmean=popmean)
    return TTestResult(
        statistic=float(result.statistic),
        p_value=float(result.pvalue),
        df=n - 1,
        mean=float(np.mean(x)),
    )


@dataclass(frozen=True)
class OLSResult:
    """Result of an ordinary-least-squares fit.

    Attributes:
        params: Estimated coefficients (intercept first if one was added).
        std_errors: Standard errors of the coefficients.
        t_values: Coefficient t-statistics.
        residuals: Fit residuals ``y - X @ params``.
        r_squared: Coefficient of determination.
        adj_r_squared: R-squared adjusted for the number of regressors.
        n_obs: Number of observations.
        param_names: Labels for each coefficient.
    """

    params: FloatArray
    std_errors: FloatArray
    t_values: FloatArray
    residuals: FloatArray
    r_squared: float
    adj_r_squared: float
    n_obs: int
    param_names: list[str]

    def summary(self) -> str:
        """Return a compact text summary of the fit."""
        lines = [f"OLS fit  (n = {self.n_obs}, R^2 = {self.r_squared:.4f})"]
        header = f"  {'name':<14}{'coef':>12}{'std err':>12}{'t':>10}"
        lines.append(header)
        for name, c, se, t in zip(
            self.param_names,
            self.params,
            self.std_errors,
            self.t_values,
            strict=True,
        ):
            lines.append(f"  {name:<14}{c:>12.6f}{se:>12.6f}{t:>10.3f}")
        return "\n".join(lines)


def ols_fit(
    X: npt.ArrayLike,
    y: npt.ArrayLike,
    *,
    add_const: bool = True,
    feature_names: list[str] | None = None,
) -> OLSResult:
    """Fit ``y = X beta + e`` by ordinary least squares.

    Standard errors assume independent, homoskedastic errors. That assumption
    is frequently violated by financial data (volatility clustering produces
    heteroskedasticity); the Week 5 notebook discusses this explicitly and
    compares against :mod:`statsmodels`.

    Args:
        X: Design matrix of shape ``(n_obs, n_features)``.
        y: Response vector.
        add_const: When ``True``, prepend an intercept column.
        feature_names: Optional labels for the (non-intercept) features.

    Returns:
        An :class:`OLSResult`.
    """
    X_raw = np.asarray(X, dtype=float)
    if X_raw.ndim == 1:
        X_raw = X_raw.reshape(-1, 1)
    y_vec = np.asarray(y, dtype=float).ravel()
    if X_raw.shape[0] != y_vec.shape[0]:
        raise ValueError("X and y must have the same number of rows")

    design = add_intercept(X_raw) if add_const else X_raw
    n, k = design.shape
    if n <= k:
        raise ValueError("need more observations than parameters")

    beta, *_ = np.linalg.lstsq(design, y_vec, rcond=None)
    fitted = design @ beta
    residuals = y_vec - fitted

    ss_res = float(residuals @ residuals)
    ss_tot = float(((y_vec - y_vec.mean()) ** 2).sum())
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    adj_r_squared = 1.0 - (1.0 - r_squared) * (n - 1) / (n - k) if n > k else float("nan")

    sigma2 = ss_res / (n - k)
    cov_beta = sigma2 * np.linalg.inv(design.T @ design)
    std_errors = np.sqrt(np.diag(cov_beta))
    with np.errstate(divide="ignore", invalid="ignore"):
        t_values = np.where(std_errors > 0, beta / std_errors, 0.0)

    base_names = feature_names or [f"x{i + 1}" for i in range(X_raw.shape[1])]
    names = ["const", *base_names] if add_const else list(base_names)

    return OLSResult(
        params=beta,
        std_errors=std_errors,
        t_values=t_values,
        residuals=residuals,
        r_squared=r_squared,
        adj_r_squared=adj_r_squared,
        n_obs=n,
        param_names=names,
    )


def false_discovery_demo(
    *,
    n_strategies: int = 200,
    n_periods: int = 252,
    alpha: float = 0.05,
    seed: int = 0,
) -> dict[str, float]:
    """Quantify spurious 'significant' results when testing many noise signals.

    Generates ``n_strategies`` pure-noise return series (true mean zero) and
    counts how many reject the null of zero mean at level ``alpha``. With a
    valid test the expected count is ``alpha * n_strategies`` — every one of
    them is a false positive. This is the statistical core of the warning
    against un-corrected strategy mining.

    Args:
        n_strategies: Number of independent noise strategies.
        n_periods: Return observations per strategy.
        alpha: Significance level of each individual test.
        seed: Random seed.

    Returns:
        A dictionary with the number and fraction of false positives and the
        theoretically expected count.
    """
    rng = np.random.default_rng(seed)
    returns = rng.standard_normal(size=(n_strategies, n_periods))
    # Two-sided one-sample t-test of zero mean for every strategy.
    result = stats.ttest_1samp(returns, popmean=0.0, axis=1)
    p_values = np.asarray(result.pvalue, dtype=float)
    n_false_positives = int(np.sum(p_values < alpha))
    return {
        "n_strategies": float(n_strategies),
        "n_false_positives": float(n_false_positives),
        "fraction_false_positives": n_false_positives / n_strategies,
        "expected_false_positives": alpha * n_strategies,
    }
