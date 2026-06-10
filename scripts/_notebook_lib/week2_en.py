"""Builder for the Week 2 notebook — English edition.

Generated content mirrors week2.py one-for-one (same cells, same code
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
        week="Week 2",
        title="Multivariable Calculus and the Minimum-Variance Portfolio",
        objectives=[
            "Compute the gradient and Hessian of a quadratic objective function.",
            "Derive equality-constrained optimization with a Lagrange multiplier.",
            "Implement and interpret the minimum-variance portfolio.",
            "Observe how noisy covariance estimates make weights unstable.",
        ],
        hours="9–11 hours",
        prereqs=["Partial derivatives and gradients", "Covariance and quadratic forms from Week 1"],
        resources=[
            (
                "MIT OpenCourseWare 18.02SC Multivariable Calculus",
                "https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/",
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
            "### Gradient and Hessian\n\n"
            "For $f(w) = w^\\top\\Sigma w$ (with $\\Sigma$ symmetric), we have\n\n"
            "$$ \\nabla f(w) = 2\\Sigma w, \\qquad \\nabla^2 f(w) = 2\\Sigma. $$\n\n"
            "If $\\Sigma$ is PSD, the Hessian is PSD and $f$ is **convex** — "
            "which guarantees the minimization problem has a well-behaved, unique solution.\n\n"
            "### The minimum-variance portfolio\n\n"
            "The problem is:\n\n"
            "$$ \\min_w\\ w^\\top\\Sigma w \\quad \\text{s.t.}\\quad \\mathbf{1}^\\top w = 1. $$\n\n"
            "Using the Lagrangian $L(w,\\lambda) = w^\\top\\Sigma w - \\lambda(\\mathbf{1}^\\top w - 1)$, "
            "differentiating with respect to $w$ and setting it to zero gives the closed-form solution\n\n"
            "$$ w^\\* = \\frac{\\Sigma^{-1}\\mathbf{1}}{\\mathbf{1}^\\top\\Sigma^{-1}\\mathbf{1}}. $$"
        ),
        code(
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "from quant_math_roadmap.data import SyntheticConfig, generate_correlated_returns\n"
            "from quant_math_roadmap.finance.metrics import covariance_matrix\n"
            "from quant_math_roadmap.finance.portfolio import (\n"
            "    equal_weights, minimum_variance_portfolio,\n"
            "    portfolio_variance, shrinkage_covariance,\n"
            ")\n"
            "from quant_math_roadmap.math.optimization import (\n"
            "    quadratic_gradient, quadratic_hessian,\n"
            ")\n"
            "\n"
            "config = SyntheticConfig(n_assets=6, n_periods=504, seed=7,\n"
            "                         average_correlation=0.45)\n"
            "returns = generate_correlated_returns(config)\n"
            "cov = covariance_matrix(returns).to_numpy()\n"
            "cov.shape"
        ),
        md("### Numerical vs analytic gradient"),
        code(
            "w0 = equal_weights(6)\n"
            "analytic = quadratic_gradient(cov, w0)\n"
            "\n"
            "# Verify the analytic gradient with finite differences\n"
            "eps = 1e-6\n"
            "numeric = np.zeros_like(w0)\n"
            "for i in range(len(w0)):\n"
            "    step = np.zeros_like(w0)\n"
            "    step[i] = eps\n"
            "    f_plus = portfolio_variance(w0 + step, cov)\n"
            "    f_minus = portfolio_variance(w0 - step, cov)\n"
            "    numeric[i] = (f_plus - f_minus) / (2 * eps)\n"
            "\n"
            "print('Analytic gradient:', np.round(analytic, 6))\n"
            "print('Numerical gradient:', np.round(numeric, 6))\n"
            "print('Max error:', np.max(np.abs(analytic - numeric)))"
        ),
        md(
            "The analytic gradient $2\\Sigma w$ agrees closely with the finite differences. The Hessian is the constant matrix $2\\Sigma$:"
        ),
        code(
            "hessian = quadratic_hessian(cov)\n"
            "print('Is the Hessian symmetric?', np.allclose(hessian, hessian.T))\n"
            "print('Smallest Hessian eigenvalue:', np.linalg.eigvalsh(hessian).min())\n"
            "print('-> Non-negative eigenvalues mean the objective is convex.')"
        ),
        md(
            "### Second-order Taylor approximation: what the function looks like *near* a point\n\n"
            "For a quadratic objective, the second-order Taylor approximation is **exactly** equal to the "
            "original function at any expansion point (because the function itself is quadratic). Below we expand around the equal-weight point "
            "and verify that $f(w_0) + g^\\top (w-w_0) + \\tfrac12 (w-w_0)^\\top H (w-w_0)$ matches the true value."
        ),
        code(
            "from quant_math_roadmap.math.optimization import taylor_quadratic_approximation\n"
            "\n"
            "w0 = equal_weights(6)\n"
            "f0 = portfolio_variance(w0, cov)\n"
            "g0 = quadratic_gradient(cov, w0)\n"
            "H0 = quadratic_hessian(cov)\n"
            "# Pick an offset in one direction as the point to approximate\n"
            "w_far = w0 + np.array([0.1, -0.05, 0.0, -0.05, 0.0, 0.0])\n"
            "approx = taylor_quadratic_approximation(f0, g0, H0, w0, w_far)\n"
            "true = portfolio_variance(w_far, cov)\n"
            "print(f'Second-order Taylor approximation = {approx:.10f}')\n"
            "print(f'True value                        = {true:.10f}')\n"
            "print('For a quadratic function the second-order Taylor approximation = the true value (zero error).')"
        ),
        md("### Minimum variance vs equal weight"),
        code(
            "mvp = minimum_variance_portfolio(cov)\n"
            "eq = equal_weights(6)\n"
            "print('Minimum-variance weights:', np.round(mvp, 4), ' sum =', round(mvp.sum(), 6))\n"
            "print('Equal weights           :', np.round(eq, 4))\n"
            "print()\n"
            "print(f'Minimum-variance portfolio variance = {portfolio_variance(mvp, cov):.8f}')\n"
            "print(f'Equal-weight variance               = {portfolio_variance(eq, cov):.8f}')"
        ),
        md(
            "**In-sample**, the minimum-variance portfolio's variance is by definition $\\le$ the equal-weight one. "
            "But that does not guarantee it is better **out-of-sample** — which we test next."
        ),
        md("### In-sample vs out-of-sample: instability caused by noise"),
        code(
            "# Estimate weights on the first half, test on the second half\n"
            "half = len(returns) // 2\n"
            "train, test = returns.iloc[:half], returns.iloc[half:]\n"
            "cov_train = covariance_matrix(train).to_numpy()\n"
            "cov_test = covariance_matrix(test).to_numpy()\n"
            "\n"
            "mvp_train = minimum_variance_portfolio(cov_train)\n"
            "in_sample = portfolio_variance(mvp_train, cov_train)\n"
            "out_sample = portfolio_variance(mvp_train, cov_test)\n"
            "eq_out = portfolio_variance(eq, cov_test)\n"
            "print(f'Minimum-variance in-sample variance      = {in_sample:.8f}')\n"
            "print(f'Minimum-variance out-of-sample variance  = {out_sample:.8f}')\n"
            "print(f'Equal-weight out-of-sample variance      = {eq_out:.8f}')\n"
            "print('Observation: out-of-sample is usually worse than in-sample, sometimes even losing to equal weight.')"
        ),
        md("### Shrinkage: covariance estimation that fights noise"),
        code(
            "weights_by_shrinkage = {}\n"
            "for delta in [0.0, 0.2, 0.5, 0.8]:\n"
            "    cov_shrunk = shrinkage_covariance(train, shrinkage=delta).to_numpy()\n"
            "    w = minimum_variance_portfolio(cov_shrunk)\n"
            "    weights_by_shrinkage[delta] = w\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(8, 4.5))\n"
            "for delta, w in weights_by_shrinkage.items():\n"
            "    ax.plot(range(1, 7), w, marker='o', label=f'shrinkage={delta}')\n"
            "ax.axhline(1 / 6, linestyle='--', label='equal weight')\n"
            "ax.set_title('Effect of shrinkage intensity on minimum-variance weights')\n"
            "ax.set_xlabel('Asset index')\n"
            "ax.set_ylabel('Weight')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md(
            "The stronger the shrinkage, the more the weights are pulled toward equal weight and away from extremes. "
            "This trades a little bias for a lot of stability, and often improves out-of-sample performance."
        ),
        md(
            "### Ledoit–Wolf: letting the data choose the shrinkage intensity\n\n"
            'Above we tried a few shrinkage intensities by hand — but "how strong should it be" is itself an '
            "estimation problem. Ledoit & Wolf (2004) derived the optimal intensity that **minimizes the expected estimation error**, "
            "and it can be computed directly from the data. `ledoit_wolf_covariance()` wraps the scikit-learn "
            "implementation and returns the covariance matrix together with the data-driven shrinkage coefficient."
        ),
        code(
            "from quant_math_roadmap.finance.portfolio import ledoit_wolf_covariance\n"
            "\n"
            "lw_cov, lw_shrinkage = ledoit_wolf_covariance(train)\n"
            "print(f'Shrinkage intensity chosen automatically by Ledoit-Wolf = {lw_shrinkage:.4f}')\n"
            "\n"
            "w_lw = minimum_variance_portfolio(lw_cov.to_numpy())\n"
            "out_lw = portfolio_variance(w_lw, cov_test)\n"
            "print(f'Sample-covariance MVP out-of-sample variance = {out_sample:.8f}')\n"
            "print(f'Ledoit-Wolf MVP out-of-sample variance       = {out_lw:.8f}')\n"
            "print(f'Equal-weight out-of-sample variance          = {eq_out:.8f}')"
        ),
        md(
            "Ledoit–Wolf needs no manual tuning, yet automatically keeps the weights only as extreme as the data "
            "can support. With many assets and relatively short samples (the norm in quant research), "
            "it is usually a more robust default than the raw sample covariance."
        ),
        exercises_intro_en(),
        md(
            "### Basic exercises\n\n"
            "1. Write down the Lagrangian of the minimum-variance problem and explain what each term means.\n"
            '2. Why does "the Hessian is PSD" guarantee the problem has a well-behaved solution?\n'
            "3. Explain in one sentence what trade-off shrinkage is making."
        ),
        md("### Applied exercises"),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 1: compute the minimum-variance weights yourself using the closed form\n"
                "# w* = (Σ^-1 1)/(1^T Σ^-1 1), and compare against minimum_variance_portfolio()."
            ),
            starter=(
                "ones = np.ones(6)\n"
                "my_mvp = None  # TODO: inv = np.linalg.solve(cov, ones); my_mvp = inv / (ones @ inv)\n"
                "if my_mvp is not None:\n"
                "    print('Max error:', np.max(np.abs(my_mvp - minimum_variance_portfolio(cov))))"
            ),
            answer=(
                "ones = np.ones(6)\n"
                "inv_dot_ones = np.linalg.solve(cov, ones)\n"
                "my_mvp = inv_dot_ones / (ones @ inv_dot_ones)\n"
                "print('Max error:', np.max(np.abs(my_mvp - minimum_variance_portfolio(cov))))"
            ),
        ),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 2: compute the long-only (no short selling) minimum-variance portfolio,\n# and confirm there are no negative weights."
            ),
            starter=(
                "long_only = None  # TODO: minimum_variance_portfolio(cov, long_only=True)\n"
                "if long_only is not None:\n"
                "    print('Smallest weight:', long_only.min(), '| sum:', long_only.sum())"
            ),
            answer=(
                "long_only = minimum_variance_portfolio(cov, long_only=True)\n"
                "print('Smallest weight:', round(long_only.min(), 6), '| sum:', round(long_only.sum(), 6))\n"
                "assert (long_only >= -1e-9).all()"
            ),
        ),
        md(
            "### Reflection question\n\n"
            "1. The minimum-variance portfolio always beats equal weight in-sample, but not necessarily out-of-sample. "
            'How does this phenomenon relate to "overfitting the in-sample period" in Week 8?'
        ),
        *quiz_cells_en(
            solution,
            week=2,
            items=[
                (
                    "What is the closed-form solution w* of the minimum-variance portfolio?",
                    ["Σ1 / (1ᵀΣ1)", "Σ⁻¹1 / (1ᵀΣ⁻¹1)", "1/n equal weights", "Σ⁻¹μ"],
                    "B",
                    "Differentiate the Lagrangian with respect to w and normalize with the constraint 1ᵀw=1.",
                ),
                (
                    "What is the gradient of f(w) = wᵀΣw?",
                    ["Σw", "2Σw", "wᵀΣ", "2w"],
                    "B",
                    "The gradient of a quadratic form with a symmetric matrix is 2Σw — the core derivative of Week 2.",
                ),
                (
                    "A PSD Hessian means the objective function has which property?",
                    ["Convex", "Concave", "Linear", "Periodic"],
                    "A",
                    "PSD Hessian ⟺ convex function, which guarantees the minimization problem is well-behaved.",
                ),
                (
                    "What is the most common consequence of directly inverting a very noisy covariance estimate?",
                    [
                        "The code raises an error",
                        "Extreme and unstable portfolio weights",
                        "Higher returns",
                        "Negative variance",
                    ],
                    "B",
                    "Matrix inversion amplifies estimation error, producing extreme long-short weights — the motivation for shrinkage.",
                ),
            ],
        ),
        mistakes_en(
            [
                "Inverting a very noisy covariance matrix and getting extreme, unstable weights.",
                "Mistaking low in-sample variance for an out-of-sample guarantee.",
                "Forgetting the constraint $\\mathbf{1}^\\top w = 1$ and getting meaningless weights.",
                "Ignoring how sensitive the optimization result is to covariance estimation error.",
            ]
        ),
        checklist_en(
            [
                "Write down and explain the Lagrangian of the minimum-variance problem.",
                "Compute the minimum-variance weights with the closed-form solution.",
                "Compare in-sample and out-of-sample variance.",
                "Explain how shrinkage stabilizes the weights.",
            ]
        ),
        footer_references_en(solution),
    ]
    return cells
