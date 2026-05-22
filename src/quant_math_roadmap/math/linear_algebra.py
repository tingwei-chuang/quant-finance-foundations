"""Linear-algebra utilities used across the roadmap.

These functions back Week 1 (covariance matrices, eigenvalues, quadratic
forms) and Week 5 (ordinary least squares as a projection). They are kept
small and explicit so the notebooks can show *what* the formula does, not just
call a black box.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]


def quadratic_form(weights: npt.ArrayLike, matrix: npt.ArrayLike) -> float:
    """Evaluate the quadratic form ``w^T M w``.

    In portfolio analysis, with ``M`` a covariance matrix and ``w`` portfolio
    weights, this is exactly the portfolio variance.

    Args:
        weights: Vector ``w`` of length ``n``.
        matrix: Square ``(n, n)`` matrix ``M``.

    Returns:
        The scalar ``w^T M w``.
    """
    w = np.asarray(weights, dtype=float).ravel()
    M = np.asarray(matrix, dtype=float)
    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        raise ValueError("matrix must be square")
    if w.shape[0] != M.shape[0]:
        raise ValueError("weights length must match matrix dimension")
    return float(w @ M @ w)


def is_symmetric(matrix: npt.ArrayLike, *, tol: float = 1e-8) -> bool:
    """Return ``True`` if ``matrix`` is (numerically) symmetric.

    Args:
        matrix: Square matrix to test.
        tol: Absolute tolerance for the symmetry check.
    """
    M = np.asarray(matrix, dtype=float)
    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        return False
    return bool(np.allclose(M, M.T, atol=tol))


def is_positive_semidefinite(matrix: npt.ArrayLike, *, tol: float = 1e-8) -> bool:
    """Return ``True`` if ``matrix`` is symmetric positive semidefinite (PSD).

    A symmetric matrix is PSD when all its eigenvalues are non-negative.
    Because covariance matrices represent variances, they *must* be PSD: a
    negative eigenvalue would correspond to a portfolio with negative
    variance, which is impossible.

    Args:
        matrix: Candidate matrix.
        tol: Eigenvalues above ``-tol`` are treated as non-negative, absorbing
            floating-point round-off.

    Returns:
        ``True`` if symmetric and all eigenvalues are ``>= -tol``.
    """
    M = np.asarray(matrix, dtype=float)
    if not is_symmetric(M, tol=max(tol, 1e-8)):
        return False
    eigenvalues = np.linalg.eigvalsh(M)
    return bool(np.min(eigenvalues) >= -tol)


def eigendecomposition(matrix: npt.ArrayLike) -> tuple[FloatArray, FloatArray]:
    """Return eigenvalues and eigenvectors of a *symmetric* matrix.

    Uses :func:`numpy.linalg.eigh`, which is appropriate for symmetric inputs
    such as covariance and correlation matrices. Eigenvalues are returned in
    ascending order.

    Args:
        matrix: Symmetric ``(n, n)`` matrix.

    Returns:
        A tuple ``(eigenvalues, eigenvectors)`` where column ``i`` of
        ``eigenvectors`` is the eigenvector for ``eigenvalues[i]``.
    """
    M = np.asarray(matrix, dtype=float)
    if not is_symmetric(M):
        raise ValueError("eigendecomposition expects a symmetric matrix")
    eigenvalues, eigenvectors = np.linalg.eigh(M)
    return eigenvalues, eigenvectors


def nearest_psd(matrix: npt.ArrayLike, *, epsilon: float = 0.0) -> FloatArray:
    """Project a symmetric matrix onto the set of PSD matrices.

    Negative eigenvalues are clipped to ``epsilon``. This is a teaching-grade
    repair for a covariance estimate that is *almost* PSD because of numerical
    noise; it is not a substitute for a proper shrinkage estimator.

    Args:
        matrix: Symmetric matrix, possibly with small negative eigenvalues.
        epsilon: Floor applied to eigenvalues.

    Returns:
        The nearest PSD matrix in the eigenvalue-clipping sense.
    """
    M = np.asarray(matrix, dtype=float)
    M = 0.5 * (M + M.T)
    eigenvalues, eigenvectors = np.linalg.eigh(M)
    clipped = np.clip(eigenvalues, epsilon, None)
    return (eigenvectors * clipped) @ eigenvectors.T


def ols_beta(X: npt.ArrayLike, y: npt.ArrayLike) -> FloatArray:
    """Solve the ordinary-least-squares normal equations ``beta = (XᵀX)⁻¹Xᵀy``.

    The implementation uses :func:`numpy.linalg.lstsq` rather than forming the
    inverse explicitly: it is numerically more stable while computing exactly
    the same least-squares solution. The caller is responsible for adding an
    intercept column to ``X`` if one is wanted.

    Args:
        X: Design matrix of shape ``(n_obs, n_features)``.
        y: Response vector of length ``n_obs``.

    Returns:
        The coefficient vector ``beta`` of length ``n_features``.
    """
    X_mat = np.asarray(X, dtype=float)
    y_vec = np.asarray(y, dtype=float).ravel()
    if X_mat.ndim == 1:
        X_mat = X_mat.reshape(-1, 1)
    if X_mat.shape[0] != y_vec.shape[0]:
        raise ValueError("X and y must have the same number of rows")
    if X_mat.shape[0] < X_mat.shape[1]:
        raise ValueError("under-determined system: more features than observations")
    beta, *_ = np.linalg.lstsq(X_mat, y_vec, rcond=None)
    return beta


def add_intercept(X: npt.ArrayLike) -> FloatArray:
    """Prepend a column of ones to a design matrix.

    Args:
        X: Matrix of shape ``(n_obs, n_features)`` (or a 1-D vector).

    Returns:
        Matrix of shape ``(n_obs, n_features + 1)`` whose first column is ones.
    """
    X_mat = np.asarray(X, dtype=float)
    if X_mat.ndim == 1:
        X_mat = X_mat.reshape(-1, 1)
    ones = np.ones((X_mat.shape[0], 1))
    return np.hstack([ones, X_mat])
