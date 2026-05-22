"""Probability simulation helpers (Week 3).

These functions support the Law of Large Numbers (LLN) and Central Limit
Theorem (CLT) demonstrations. Every function takes an explicit seed so that
notebook outputs are reproducible.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]


def running_mean(samples: npt.ArrayLike) -> FloatArray:
    """Return the cumulative sample mean after each observation.

    Plotting ``running_mean`` against the sample size visualises the Law of
    Large Numbers: the curve settles towards the true expectation.

    Args:
        samples: A 1-D sequence of draws.

    Returns:
        Array where element ``i`` is the mean of ``samples[: i + 1]``.
    """
    x = np.asarray(samples, dtype=float).ravel()
    if x.size == 0:
        raise ValueError("samples must be non-empty")
    counts = np.arange(1, x.size + 1)
    return np.cumsum(x) / counts


def sampling_distribution_of_mean(
    *,
    population_sampler: str = "uniform",
    sample_size: int = 30,
    n_experiments: int = 2000,
    seed: int = 0,
) -> FloatArray:
    """Simulate the sampling distribution of the sample mean.

    Repeatedly draws a sample of ``sample_size`` observations from a chosen
    (non-normal) population and records each sample mean. By the CLT the
    histogram of these means approaches a normal distribution as
    ``sample_size`` grows, *regardless* of the population shape.

    Args:
        population_sampler: One of ``"uniform"``, ``"exponential"`` or
            ``"bernoulli"`` — deliberately non-normal populations.
        sample_size: Observations per experiment.
        n_experiments: Number of repeated experiments.
        seed: Random seed.

    Returns:
        Array of ``n_experiments`` sample means.
    """
    if sample_size < 1:
        raise ValueError("sample_size must be >= 1")
    if n_experiments < 1:
        raise ValueError("n_experiments must be >= 1")
    rng = np.random.default_rng(seed)
    shape = (n_experiments, sample_size)

    if population_sampler == "uniform":
        draws = rng.uniform(0.0, 1.0, size=shape)
    elif population_sampler == "exponential":
        draws = rng.exponential(scale=1.0, size=shape)
    elif population_sampler == "bernoulli":
        draws = rng.binomial(n=1, p=0.3, size=shape).astype(float)
    else:
        raise ValueError("population_sampler must be 'uniform', 'exponential' or 'bernoulli'")
    return draws.mean(axis=1)


def simulate_bernoulli(p: float, size: int, *, seed: int = 0) -> FloatArray:
    """Simulate Bernoulli(``p``) draws.

    Args:
        p: Success probability in ``[0, 1]``.
        size: Number of draws.
        seed: Random seed.
    """
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    rng = np.random.default_rng(seed)
    return rng.binomial(n=1, p=p, size=size).astype(float)


def simulate_normal(mean: float, std: float, size: int, *, seed: int = 0) -> FloatArray:
    """Simulate Normal(``mean``, ``std``²) draws.

    Args:
        mean: Distribution mean.
        std: Standard deviation (must be positive).
        size: Number of draws.
        seed: Random seed.
    """
    if std <= 0.0:
        raise ValueError("std must be positive")
    rng = np.random.default_rng(seed)
    return rng.normal(loc=mean, scale=std, size=size)


def empirical_moments(samples: npt.ArrayLike) -> dict[str, float]:
    """Return basic empirical moments of a sample.

    Args:
        samples: A 1-D sequence of draws.

    Returns:
        A dictionary with ``mean``, ``variance`` (unbiased, ``ddof=1``) and
        ``std`` keys.
    """
    x = np.asarray(samples, dtype=float).ravel()
    if x.size < 2:
        raise ValueError("need at least two samples for an unbiased variance")
    return {
        "mean": float(np.mean(x)),
        "variance": float(np.var(x, ddof=1)),
        "std": float(np.std(x, ddof=1)),
    }
