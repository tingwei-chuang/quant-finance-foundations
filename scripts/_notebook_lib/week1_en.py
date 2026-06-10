"""Builder for the Week 1 notebook — English edition.

Generated content mirrors week1.py one-for-one (same cells, same code
semantics); only the natural-language content is translated. See
scripts/_notebook_lib/__init__.py for the dispatch table.
"""

from __future__ import annotations

import nbformat as nbf

from .cells import code, ex_code, md
from .parts_en import (
    checklist_en,
    exercises_intro_en,
    footer_references_en,
    header_en,
    mistakes_en,
    quiz_cells_en,
)


def week(solution: bool) -> list[nbf.NotebookNode]:
    cells = header_en(
        solution=solution,
        week="Week 1",
        title="Returns, Risk and Linear Algebra",
        objectives=[
            "Correctly compute simple returns, log returns and cumulative returns.",
            "Compute annualized mean, annualized volatility, the covariance matrix and the correlation matrix.",
            "Compute portfolio variance with the quadratic form $w^\\top\\Sigma w$.",
            "Understand eigenvalues, eigenvectors and positive semidefinite (PSD) matrices.",
        ],
        hours="8–10 hours",
        prereqs=["Vector and matrix operations", "Definitions of mean and variance"],
        resources=[
            (
                "MIT OpenCourseWare 18.06SC Linear Algebra",
                "https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/",
            ),
            (
                "NTU OpenCourseWare: Foundations of Financial Literacy",
                "https://ocw.aca.ntu.edu.tw/courses/110S204",
            ),
        ],
    )
    cells += [
        md(
            "## Concepts\n\n"
            "### Returns\n\n"
            "Given prices $P_t$, the **simple return** and the **log return** are defined as:\n\n"
            "$$ r_t = \\frac{P_t - P_{t-1}}{P_{t-1}}, \\qquad "
            "\\ell_t = \\ln\\!\\left(\\frac{P_t}{P_{t-1}}\\right). $$\n\n"
            "Log returns are **additive over time**: the multi-period log return equals the sum of the per-period ones.\n\n"
            "### Portfolio variance\n\n"
            "With a weight vector $w$ and covariance matrix $\\Sigma$, portfolio variance is the quadratic form:\n\n"
            "$$ \\operatorname{Var}(r_p) = w^\\top \\Sigma\\, w. $$\n\n"
            "Because a variance can never be negative, $w^\\top\\Sigma w \\ge 0$ for every $w$ — "
            "which is exactly what it means for $\\Sigma$ to be **positive semidefinite (PSD)**, "
            "equivalent to all of its eigenvalues being $\\ge 0$."
        ),
        code(
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "from quant_math_roadmap.data import SyntheticConfig, generate_correlated_prices\n"
            "from quant_math_roadmap.finance.returns import simple_returns, log_returns\n"
            "from quant_math_roadmap.finance.metrics import (\n"
            "    annualized_mean, annualized_volatility,\n"
            "    covariance_matrix, correlation_matrix,\n"
            ")\n"
            "from quant_math_roadmap.finance.portfolio import equal_weights, portfolio_variance\n"
            "from quant_math_roadmap.math.linear_algebra import (\n"
            "    eigendecomposition, is_positive_semidefinite,\n"
            ")\n"
            "\n"
            "config = SyntheticConfig(n_assets=4, n_periods=756, seed=11,\n"
            "                         average_correlation=0.4)\n"
            "prices = generate_correlated_prices(config)\n"
            "prices.tail()"
        ),
        md("### Computing returns and comparing simple vs log"),
        code(
            "simple = simple_returns(prices)\n"
            "log = log_returns(prices)\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(simple.index, simple.iloc[:, 0], label='simple return')\n"
            "ax.plot(log.index, log.iloc[:, 0], label='log return')\n"
            "ax.set_title(f'{prices.columns[0]}: simple vs log return')\n"
            "ax.set_xlabel('Date')\n"
            "ax.set_ylabel('Daily return')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md(
            "At the daily scale the two nearly overlap; the difference only becomes visible for larger returns. "
            "The advantage of log returns is additivity, which is very convenient for the regression and time-series models later on."
        ),
        md("### Annualized mean and volatility (note: annualization is an explicit assumption)"),
        code(
            "ann_mean = annualized_mean(simple, frequency='daily')\n"
            "ann_vol = annualized_volatility(simple, frequency='daily')\n"
            "summary = ann_mean.to_frame('Annualized mean').join(ann_vol.to_frame('Annualized volatility'))\n"
            "summary"
        ),
        md(
            "We pass `frequency='daily'` (252 trading days per year) **explicitly**. "
            "If the data were actually weekly but annualized with 252, volatility would be overstated by roughly $\\sqrt{252/52}\\approx 2.2$ times."
        ),
        md("### Covariance, correlation matrix and the quadratic form"),
        code(
            "cov = covariance_matrix(simple)\n"
            "corr = correlation_matrix(simple)\n"
            "print('Covariance matrix:')\n"
            "print(cov.round(6))\n"
            "print('\\nCorrelation matrix:')\n"
            "print(corr.round(3))"
        ),
        code(
            "weights = equal_weights(prices.shape[1])\n"
            "# Compute the quadratic form w^T Sigma w by hand\n"
            "manual = float(weights @ cov.to_numpy() @ weights)\n"
            "# Using the reusable function\n"
            "via_function = portfolio_variance(weights, cov.to_numpy())\n"
            "print(f'Portfolio variance by hand     = {manual:.8f}')\n"
            "print(f'Portfolio variance via function = {via_function:.8f}')\n"
            "assert np.isclose(manual, via_function)"
        ),
        md("### Eigenvalues and the PSD check"),
        code(
            "eigenvalues, eigenvectors = eigendecomposition(cov.to_numpy())\n"
            "print('Eigenvalues of the covariance matrix:', np.round(eigenvalues, 8))\n"
            "print('Is it PSD (all eigenvalues >= 0)?', is_positive_semidefinite(cov.to_numpy()))\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(7, 4))\n"
            "ax.bar(range(1, len(eigenvalues) + 1), eigenvalues)\n"
            "ax.set_title('Eigenvalues of the covariance matrix')\n"
            "ax.set_xlabel('Eigenvalue index')\n"
            "ax.set_ylabel('Eigenvalue')\n"
            "plt.show()"
        ),
        md(
            "All eigenvalues are $\\ge 0$, so the covariance matrix is PSD. The eigenvector belonging to the "
            "largest eigenvalue is often interpreted as the dominant direction of common movement across assets (related to PCA)."
        ),
        md(
            "### What if the estimated matrix is not PSD?\n\n"
            "Sometimes noise or floating-point error gives a covariance estimate a tiny negative eigenvalue. "
            "`nearest_psd()` clips negative eigenvalues to 0 (or some lower bound epsilon), "
            "projecting onto the nearest PSD matrix. This is a teaching-grade repair, not a substitute for shrinkage."
        ),
        code(
            "from quant_math_roadmap.math.linear_algebra import nearest_psd\n"
            "\n"
            "# Deliberately inject a small negative eigenvalue into the covariance matrix\n"
            "noisy = cov.to_numpy().copy()\n"
            "noisy[0, 0] -= 2 * eigenvalues.max()  # force a negative eigenvalue\n"
            "print('Smallest eigenvalue before repair:', round(float(np.linalg.eigvalsh(noisy).min()), 6))\n"
            "repaired = nearest_psd(noisy, epsilon=1e-8)\n"
            "print('Smallest eigenvalue after repair:', round(float(np.linalg.eigvalsh(repaired).min()), 8))"
        ),
        exercises_intro_en(),
        md(
            "### Basic exercises\n\n"
            "1. Explain in words why log returns are additive while simple returns are not.\n"
            "2. Explain what impossible situation a covariance matrix with one negative eigenvalue would imply.\n"
            "3. Why is the diagonal of a correlation matrix always 1?"
        ),
        md("### Applied exercises"),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 1: implement simple returns from scratch with numpy (no pct_change),\n"
                "# and compare against the result of simple_returns()."
            ),
            starter=(
                "p = prices.iloc[:, 0].to_numpy()\n"
                "my_simple = None  # TODO: (p[1:] - p[:-1]) / p[:-1]\n"
                "if my_simple is not None:\n"
                "    print('Max error:', np.max(np.abs(my_simple - simple.iloc[:, 0].to_numpy())))"
            ),
            answer=(
                "p = prices.iloc[:, 0].to_numpy()\n"
                "my_simple = (p[1:] - p[:-1]) / p[:-1]\n"
                "print('Max error:', np.max(np.abs(my_simple - simple.iloc[:, 0].to_numpy())))"
            ),
        ),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 2: compare the equal-weight portfolio variance with the variance of\n"
                '# "buying only the lowest-volatility asset". Which is lower? Why does diversification usually help?'
            ),
            starter=(
                "eq_var = portfolio_variance(equal_weights(prices.shape[1]), cov.to_numpy())\n"
                "lowest_vol_idx = None  # TODO: int(np.argmin(np.diag(cov.to_numpy())))\n"
                "print('Equal-weight variance:', eq_var)\n"
                "print('(After completing the TODO, print the single-asset variance)')"
            ),
            answer=(
                "eq_var = portfolio_variance(equal_weights(prices.shape[1]), cov.to_numpy())\n"
                "lowest_vol_idx = int(np.argmin(np.diag(cov.to_numpy())))\n"
                "single_var = cov.to_numpy()[lowest_vol_idx, lowest_vol_idx]\n"
                "print(f'Equal-weight variance = {eq_var:.8f}')\n"
                "print(f'Lowest-volatility single-asset variance = {single_var:.8f}')\n"
                "print('Diversification exploits correlations below 1 to lower the overall variance.')"
            ),
        ),
        md(
            "### Reflection question\n\n"
            "1. The covariance matrix is estimated from **historical** data. What can go wrong if you use it directly "
            "to predict **future** portfolio risk? What does that imply for backtesting?"
        ),
        *quiz_cells_en(
            solution,
            week=1,
            items=[
                (
                    "What is the matrix formula for portfolio variance?",
                    ["wᵀΣw", "wᵀμ", "Σw", "wwᵀ"],
                    "A",
                    "The quadratic form of the weight vector w with the covariance matrix Σ is the portfolio variance.",
                ),
                (
                    "Why must a covariance matrix be PSD?",
                    [
                        "Because it is a symmetric matrix",
                        "Because the variance wᵀΣw of any portfolio can never be negative",
                        "Because eigenvalues must be integers",
                        "For numerical stability",
                    ],
                    "B",
                    "If a negative eigenvalue existed, you could construct a portfolio with negative variance — which is mathematically impossible.",
                ),
                (
                    "What is the key property of log returns versus simple returns?",
                    [
                        "Always larger",
                        "Additive across periods",
                        "Independent of prices",
                        "Always positive",
                    ],
                    "B",
                    "The multi-period log return is the sum of the per-period ones; simple returns compound multiplicatively and cannot simply be added.",
                ),
                (
                    "To annualize daily volatility, multiply by?",
                    ["252", "√252", "12", "√12"],
                    "B",
                    "Under the i.i.d. assumption variance scales linearly with the horizon, so the standard deviation is multiplied by √252.",
                ),
            ],
        ),
        mistakes_en(
            [
                "Forgetting that a return series has one fewer observation than the price series (there is no return on day one).",
                "Annualizing without stating the data frequency, assuming everything is daily.",
                "Calling an eigendecomposition on a non-symmetric or non-square matrix.",
                "Treating the sample covariance matrix as exact and ignoring that it is only a noisy estimate.",
            ]
        ),
        checklist_en(
            [
                "Correctly compute simple/log returns and explain the difference.",
                "Compute annualized mean and volatility, and state the annualization assumption.",
                "Compute portfolio variance with $w^\\top\\Sigma w$.",
                "Check whether a matrix is PSD and explain what that means.",
            ]
        ),
        footer_references_en(solution),
    ]
    return cells
