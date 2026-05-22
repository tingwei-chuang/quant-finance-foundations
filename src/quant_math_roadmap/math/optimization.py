"""Optimisation helpers (Week 2).

The roadmap teaches optimisation through one concrete, well-understood problem:
the global minimum-variance portfolio. This module provides the gradient/Hessian
building blocks and the constrained solver used in the Week 2 notebook.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]


def quadratic_gradient(matrix: npt.ArrayLike, weights: npt.ArrayLike) -> FloatArray:
    """Return the gradient of ``f(w) = w^T M w`` with respect to ``w``.

    For a symmetric ``M`` the gradient is ``2 M w``. This is the workhorse
    derivative behind minimum-variance optimisation.

    Args:
        matrix: Symmetric ``(n, n)`` matrix ``M``.
        weights: Point ``w`` at which to evaluate the gradient.

    Returns:
        The gradient vector ``2 M w``.
    """
    M = np.asarray(matrix, dtype=float)
    w = np.asarray(weights, dtype=float).ravel()
    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        raise ValueError("matrix must be square")
    if w.shape[0] != M.shape[0]:
        raise ValueError("weights length must match matrix dimension")
    M_sym = 0.5 * (M + M.T)
    return 2.0 * (M_sym @ w)


def quadratic_hessian(matrix: npt.ArrayLike) -> FloatArray:
    """Return the Hessian of ``f(w) = w^T M w``.

    The Hessian is the constant matrix ``2 M`` (symmetrised). When ``M`` is PSD
    the Hessian is PSD, so ``f`` is convex — which is *why* the
    minimum-variance problem has a unique, well-behaved solution.

    Args:
        matrix: Symmetric ``(n, n)`` matrix ``M``.

    Returns:
        The Hessian ``2 M``.
    """
    M = np.asarray(matrix, dtype=float)
    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        raise ValueError("matrix must be square")
    return 2.0 * (0.5 * (M + M.T))


def min_variance_weights(covariance: npt.ArrayLike, *, ridge: float = 0.0) -> FloatArray:
    """Solve the global minimum-variance portfolio in closed form.

    The problem is::

        minimise   w^T Sigma w
        subject to 1^T w = 1            (fully invested)

    Forming the Lagrangian and setting derivatives to zero gives the
    closed-form solution::

        w* = (Sigma^-1 1) / (1^T Sigma^-1 1)

    Short positions are allowed (weights may be negative); the long-only
    variant is :func:`min_variance_weights_long_only`.

    Args:
        covariance: A symmetric PSD covariance matrix.
        ridge: Optional non-negative ridge term added to the diagonal before
            inversion. A small ridge stabilises the solution when the
            covariance estimate is noisy or near-singular.

    Returns:
        Portfolio weights that sum to one.
    """
    Sigma = np.asarray(covariance, dtype=float)
    if Sigma.ndim != 2 or Sigma.shape[0] != Sigma.shape[1]:
        raise ValueError("covariance must be a square matrix")
    if ridge < 0.0:
        raise ValueError("ridge must be non-negative")
    n = Sigma.shape[0]
    Sigma = 0.5 * (Sigma + Sigma.T)
    if ridge > 0.0:
        Sigma = Sigma + ridge * np.eye(n)
    ones = np.ones(n)
    try:
        inv_dot_ones = np.linalg.solve(Sigma, ones)
    except np.linalg.LinAlgError as exc:
        raise ValueError("covariance matrix is singular; try a positive `ridge` term") from exc
    denominator = float(ones @ inv_dot_ones)
    if abs(denominator) < 1e-15:
        raise ValueError("degenerate covariance: 1^T Sigma^-1 1 is ~0")
    return inv_dot_ones / denominator


def min_variance_weights_long_only(
    covariance: npt.ArrayLike,
    *,
    max_iter: int = 10000,
    tol: float = 1e-10,
    ridge: float = 1e-10,
) -> FloatArray:
    """Solve the minimum-variance portfolio with a no-short-selling constraint.

    Adds ``w >= 0`` to the fully-invested constraint. The problem is a convex
    quadratic program; it is solved here with projected gradient descent so the
    repository keeps a pure NumPy/SciPy fallback and does not *require*
    ``cvxpy``. (If ``cvxpy`` is installed, the Week 2 notebook shows it as an
    optional cross-check.)

    Args:
        covariance: Symmetric PSD covariance matrix.
        max_iter: Maximum projected-gradient iterations.
        tol: Convergence tolerance on the weight update.
        ridge: Small diagonal term ensuring strict convexity.

    Returns:
        Non-negative portfolio weights that sum to one.
    """
    Sigma = np.asarray(covariance, dtype=float)
    if Sigma.ndim != 2 or Sigma.shape[0] != Sigma.shape[1]:
        raise ValueError("covariance must be a square matrix")
    n = Sigma.shape[0]
    Sigma = 0.5 * (Sigma + Sigma.T) + ridge * np.eye(n)

    # Step size from the largest eigenvalue keeps gradient descent stable.
    lipschitz = 2.0 * float(np.linalg.eigvalsh(Sigma).max())
    step = 1.0 / lipschitz
    w = np.full(n, 1.0 / n)
    for _ in range(max_iter):
        grad = 2.0 * (Sigma @ w)
        w_next = _project_to_simplex(w - step * grad)
        if np.linalg.norm(w_next - w) < tol:
            w = w_next
            break
        w = w_next
    return w


def _project_to_simplex(v: FloatArray) -> FloatArray:
    """Euclidean projection of a vector onto ``{w : w >= 0, sum(w) = 1}``.

    Implements the classic sorting-based simplex projection.
    """
    n = v.size
    sorted_v = np.sort(v)[::-1]
    cumulative = np.cumsum(sorted_v)
    rho_candidates = sorted_v + (1.0 - cumulative) / np.arange(1, n + 1)
    rho = np.nonzero(rho_candidates > 0)[0][-1]
    theta = (cumulative[rho] - 1.0) / (rho + 1.0)
    return np.maximum(v - theta, 0.0)


def taylor_quadratic_approximation(
    f_value: float,
    gradient: npt.ArrayLike,
    hessian: npt.ArrayLike,
    base_point: npt.ArrayLike,
    eval_point: npt.ArrayLike,
) -> float:
    """Evaluate the second-order Taylor approximation of a function.

    Computes ``f(x0) + g^T d + 0.5 d^T H d`` where ``d = x - x0``. Used in the
    Week 2 notebook to illustrate how a smooth objective looks locally
    quadratic near a point.

    Args:
        f_value: ``f(x0)``.
        gradient: Gradient at ``x0``.
        hessian: Hessian at ``x0``.
        base_point: The expansion point ``x0``.
        eval_point: The point ``x`` at which to approximate ``f``.

    Returns:
        The quadratic-approximation value.
    """
    g = np.asarray(gradient, dtype=float).ravel()
    H = np.asarray(hessian, dtype=float)
    x0 = np.asarray(base_point, dtype=float).ravel()
    x = np.asarray(eval_point, dtype=float).ravel()
    d = x - x0
    return float(f_value + g @ d + 0.5 * d @ H @ d)
