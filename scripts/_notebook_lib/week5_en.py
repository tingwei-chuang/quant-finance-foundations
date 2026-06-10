"""Builder for the Week 5 notebook — English edition.

Generated content mirrors week5.py one-for-one (same cells, same code
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
        week="Week 5",
        title="Regression and factor models",
        objectives=[
            "Derive and implement OLS in matrix form.",
            "Estimate a CAPM-style market beta and interpret it.",
            "Fit a multi-factor model and inspect the residuals.",
            "Compute rolling betas and understand omitted variable bias.",
        ],
        hours="9–11 hours",
        prereqs=["Matrix operations from Week 1", "Standard errors from Week 4"],
        resources=[
            (
                "NTU OpenCourseWare Statistics I and Introductory Econometrics",
                "https://ocw.aca.ntu.edu.tw/courses/112S103",
            ),
            (
                "MIT OpenCourseWare 18.06SC Linear Algebra",
                "https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/",
            ),
        ],
    )
    cells += [
        md(
            "## Concepts\n\n"
            "### OLS in matrix form\n\n"
            "For the model $y = X\\beta + \\varepsilon$, the least-squares solution is\n\n"
            "$$ \\hat\\beta = (X^\\top X)^{-1} X^\\top y. $$\n\n"
            "Geometrically, $X\\hat\\beta$ is the **projection** of $y$ onto the subspace spanned by the columns of $X$; "
            "the residual $y - X\\hat\\beta$ is orthogonal to that subspace.\n\n"
            "### Financial meaning\n\n"
            "In the CAPM-style regression $r_{\\text{asset}} = \\alpha + \\beta\\, r_{\\text{market}} + \\varepsilon$, "
            "$\\beta$ measures the asset's exposure to the market. **But remember: a regression coefficient does not automatically become a tradable "
            "signal** — it merely describes a historical co-movement."
        ),
        code(
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import statsmodels.api as sm\n"
            "from quant_math_roadmap.math.statistics import ols_fit\n"
            "from quant_math_roadmap.math.linear_algebra import add_intercept, ols_beta\n"
            "\n"
            "rng = np.random.default_rng(2024)\n"
            "n = 600\n"
            "market = rng.normal(0.0003, 0.011, n)\n"
            "true_beta, true_alpha = 1.2, 0.0001\n"
            "idiosyncratic = rng.normal(0.0, 0.008, n)\n"
            "asset = true_alpha + true_beta * market + idiosyncratic\n"
            "print('Generated synthetic market and asset returns, n =', n)"
        ),
        md("### Hand-rolled OLS vs statsmodels"),
        code(
            "fit = ols_fit(market, asset, add_const=True, feature_names=['market'])\n"
            "print(fit.summary())\n"
            "print()\n"
            "sm_fit = sm.OLS(asset, sm.add_constant(market)).fit()\n"
            "print('statsmodels coefficients:', np.round(sm_fit.params, 6))\n"
            "print('our coefficients        :', np.round(fit.params, 6))\n"
            "assert np.allclose(fit.params, sm_fit.params)"
        ),
        md(
            "The estimated beta should be close to the true value 1.2. Our hand-rolled OLS matches `statsmodels` exactly, "
            "confirming $\\hat\\beta = (X^\\top X)^{-1}X^\\top y$."
        ),
        code(
            "fig, ax = plt.subplots(figsize=(6.5, 5))\n"
            "ax.scatter(market, asset, s=8, alpha=0.4, label='Observations')\n"
            "grid = np.linspace(market.min(), market.max(), 100)\n"
            "ax.plot(grid, fit.params[0] + fit.params[1] * grid,\n"
            "        label=f'OLS fitted line (beta={fit.params[1]:.3f})')\n"
            "ax.set_title('CAPM-style regression: asset return vs market return')\n"
            "ax.set_xlabel('Market return')\n"
            "ax.set_ylabel('Asset return')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md("### Multi-factor model"),
        code(
            "value_factor = rng.normal(0.0, 0.007, n)\n"
            "size_factor = rng.normal(0.0, 0.006, n)\n"
            "asset_multi = (0.0001 + 1.1 * market + 0.6 * value_factor\n"
            "               - 0.3 * size_factor + rng.normal(0, 0.005, n))\n"
            "X = np.column_stack([market, value_factor, size_factor])\n"
            "multi_fit = ols_fit(X, asset_multi, add_const=True,\n"
            "                    feature_names=['market', 'value', 'size'])\n"
            "print(multi_fit.summary())"
        ),
        md(
            "Each coefficient is the exposure to that factor 'holding the other factors fixed'. $R^2$ measures how much of the "
            "return variance the model explains — but a high $R^2$ does **not** mean profitability."
        ),
        md("### Rolling beta"),
        code(
            "asset_s = pd.Series(asset)\n"
            "market_s = pd.Series(market)\n"
            "window = 120\n"
            "rolling_beta = []\n"
            "for end in range(window, n + 1):\n"
            "    sl = slice(end - window, end)\n"
            "    b = ols_beta(add_intercept(market_s.iloc[sl].to_numpy()),\n"
            "                 asset_s.iloc[sl].to_numpy())\n"
            "    rolling_beta.append(b[1])\n"
            "rolling_beta = pd.Series(rolling_beta, index=range(window, n + 1))\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(rolling_beta.index, rolling_beta.values, label=f'{window}-period rolling beta')\n"
            "ax.axhline(true_beta, linestyle='--', label=f'True beta = {true_beta}')\n"
            "ax.set_title('Rolling beta estimates over time')\n"
            "ax.set_xlabel('Window end position')\n"
            "ax.set_ylabel('Estimated beta')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md(
            "Even though the true beta is constant, the rolling estimate still oscillates around it — that is the "
            "sampling uncertainty of estimation. With real data, betas also **genuinely change over time**."
        ),
        md(
            "### Heteroskedasticity and robust standard errors (HC0 / HC1)\n\n"
            "Financial data often exhibit **heteroskedasticity**: the error variance is not constant (for example, it grows with market volatility). "
            "In that case the OLS **coefficient estimates remain unbiased**, but the classical standard errors are wrong — significance tests get misled. "
            "White's (1980) **sandwich estimator** re-estimates the coefficient covariance using only 'the squared actual residuals', "
            "with no assumption about the error structure:\n\n"
            "$$ \\widehat{\\mathrm{Var}}(\\hat\\beta)_{HC0} = (X^\\top X)^{-1}"
            " X^\\top \\mathrm{diag}(e_i^2)\\, X (X^\\top X)^{-1} $$\n\n"
            "Below we deliberately build a dataset whose error variance grows with $|x|$ and compare classical against robust standard errors."
        ),
        code(
            "# Error std = 0.5 + |x| -> textbook-grade heteroskedasticity\n"
            "x_het = rng.standard_normal(800)\n"
            "y_het = 1.0 + 2.0 * x_het + rng.standard_normal(800) * (0.5 + np.abs(x_het))\n"
            "\n"
            "classic = ols_fit(x_het, y_het, feature_names=['x'])\n"
            "robust = ols_fit(x_het, y_het, feature_names=['x'], robust='HC1')\n"
            "print('Coefficients identical:', np.allclose(classic.params, robust.params))\n"
            "print(f'Classical std error of the slope  = {classic.std_errors[1]:.4f}')\n"
            "print(f'HC1 robust std error of the slope = {robust.std_errors[1]:.4f}')\n"
            "print('Under heteroskedasticity, classical standard errors clearly understate uncertainty -> t statistics are inflated.')"
        ),
        md(
            "**Takeaway**: when reporting financial regressions, defaulting to robust standard errors is good practice. Note that they only "
            "fix the inference (standard errors, t, p-values), not the coefficients themselves — the model's explanatory power is unchanged; "
            "what changes is your confidence in the significance."
        ),
        md("### Residual inspection and omitted variable bias"),
        code(
            "fig, ax = plt.subplots(figsize=(9, 4))\n"
            "ax.scatter(range(len(multi_fit.residuals)), multi_fit.residuals, s=8, alpha=0.4)\n"
            "ax.axhline(0.0, linestyle='--')\n"
            "ax.set_title('Residuals of the multi-factor model')\n"
            "ax.set_xlabel('Observation index')\n"
            "ax.set_ylabel('Residual')\n"
            "plt.show()"
        ),
        code(
            "# Deliberately omit the value factor and watch the beta get distorted\n"
            "biased = ols_fit(market, asset_multi, add_const=True, feature_names=['market'])\n"
            "full = ols_fit(X, asset_multi, add_const=True,\n"
            "               feature_names=['market', 'value', 'size'])\n"
            "print('market coefficient with omitted variable:', round(biased.params[1], 4))\n"
            "print('market coefficient in the full model    :', round(full.params[1], 4))\n"
            "print('If an omitted variable correlates with an included one, the estimated coefficient is biased.')"
        ),
        exercises_intro_en(),
        md(
            "### Basic exercises\n\n"
            "1. Explain what OLS does in the language of geometric projection.\n"
            "2. Explain what the intercept, beta, residuals and $R^2$ each represent.\n"
            "3. Why does 'the regression coefficient is significant' not mean 'we can trade on it'?"
        ),
        md("### Applied exercises"),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 1: without using ols_fit, estimate beta directly from the matrix formula (X^T X)^-1 X^T y\n"
                "# and compare against ols_fit (remember to add the intercept column)."
            ),
            starter=(
                "Xc = add_intercept(market)\n"
                "my_beta = None  # TODO: np.linalg.solve(Xc.T @ Xc, Xc.T @ asset)\n"
                "if my_beta is not None:\n"
                "    print('hand-computed beta:', np.round(my_beta, 6))"
            ),
            answer=(
                "Xc = add_intercept(market)\n"
                "my_beta = np.linalg.solve(Xc.T @ Xc, Xc.T @ asset)\n"
                "print('hand-computed beta:', np.round(my_beta, 6))\n"
                "print('ols_fit           :', np.round(fit.params, 6))\n"
                "assert np.allclose(my_beta, fit.params)"
            ),
        ),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 2: change the rolling window to 60 periods and observe how the volatility of the rolling beta changes."
            ),
            starter=(
                "win = 60\n"
                "betas = []  # TODO: compute the rolling beta with win, mirroring the code above\n"
                "print('Once done, compare the volatility of the 60-period and 120-period estimates.')"
            ),
            answer=(
                "win = 60\n"
                "betas = []\n"
                "for end in range(win, n + 1):\n"
                "    sl = slice(end - win, end)\n"
                "    b = ols_beta(add_intercept(market_s.iloc[sl].to_numpy()),\n"
                "                 asset_s.iloc[sl].to_numpy())\n"
                "    betas.append(b[1])\n"
                "betas = pd.Series(betas)\n"
                "print('60-period rolling beta std :', round(betas.std(), 4))\n"
                "print('120-period rolling beta std:', round(rolling_beta.std(), 4))\n"
                "print('The shorter the window, the less stable the estimate.')"
            ),
        ),
        md(
            "### Reflection question\n\n"
            "1. Suppose a regression tells you some factor is 'significant' for next-period returns. Before turning it into a backtest signal, "
            "what does Week 4 (multiple testing) warn you about, and what does Week 8 (leakage) warn you about?"
        ),
        *quiz_cells_en(
            solution,
            week=5,
            items=[
                (
                    "What is the matrix solution β̂ of OLS?",
                    ["(XᵀX)⁻¹Xᵀy", "Xᵀy", "X⁻¹y", "(XXᵀ)⁻¹yX"],
                    "A",
                    "Solved from the normal equations XᵀXβ = Xᵀy — the core formula of Week 5.",
                ),
                (
                    "What does R² measure?",
                    [
                        "How profitable the strategy is",
                        "The proportion of variance in the dependent variable explained by the model",
                        "The magnitude of the coefficients",
                        "The sum of the residuals",
                    ],
                    "B",
                    "R² = 1 − SS_res/SS_tot; a high R² implies neither profitability nor causality.",
                ),
                (
                    "Heteroskedasticity mainly affects which part of OLS?",
                    [
                        "The coefficient estimates",
                        "The standard errors (and thus the t statistics)",
                        "R²",
                        "The intercept",
                    ],
                    "B",
                    "OLS coefficients stay unbiased, but classical standard errors are wrong — inference (significance) gets misled.",
                ),
                (
                    "What do HC0/HC1 robust standard errors change?",
                    ["The regression coefficients", "The standard errors", "The residuals", "R²"],
                    "B",
                    "The sandwich estimator only fixes the estimate of the coefficient covariance matrix; the point estimates are untouched.",
                ),
            ],
        ),
        mistakes_en(
            [
                "Forgetting to add an intercept column to the design matrix.",
                "Treating a high $R^2$ as evidence that the strategy is profitable.",
                "Ignoring that heteroskedasticity invalidates plain OLS standard errors.",
                "Omitting an important variable and incurring omitted variable bias.",
                "Treating a regression coefficient directly as a tradable signal.",
            ]
        ),
        checklist_en(
            [
                "Derive and implement $\\hat\\beta=(X^\\top X)^{-1}X^\\top y$.",
                "Interpret the intercept, beta, residuals and $R^2$.",
                "Compute rolling betas and explain their volatility.",
                "Explain omitted variable bias.",
            ]
        ),
        footer_references_en(solution),
    ]
    return cells
