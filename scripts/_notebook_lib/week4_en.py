"""Builder for the Week 4 notebook — English edition.

Generated content mirrors week4.py one-for-one (same cells, same code
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
        week="Week 4",
        title="Statistical inference for strategy returns",
        objectives=[
            "Estimate the standard error and confidence interval of a mean return.",
            "Build a bootstrap confidence interval for a mean return.",
            "Understand what a p-value means and how it is commonly misused.",
            "Demonstrate how 'testing many random strategies' manufactures false positives.",
        ],
        hours="9–11 hours",
        prereqs=["Sampling uncertainty from Week 3", "Mean and standard deviation"],
        resources=[
            (
                "MIT OpenCourseWare 18.05 Introduction to Probability and Statistics",
                "https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/",
            ),
            (
                "NTU OpenCourseWare Statistics I and Introductory Econometrics",
                "https://ocw.aca.ntu.edu.tw/courses/112S103",
            ),
        ],
    )
    cells += [
        md(
            "## Concepts\n\n"
            "### Estimators, standard errors and confidence intervals\n\n"
            "An **estimator** is a function of the data (for example the sample mean). It has **bias** (systematic error) "
            "and **variance** (it varies from sample to sample). The **standard error** of the sample mean is $s/\\sqrt n$.\n\n"
            "A **confidence interval** gives 'the range of parameter values compatible with the data'. The correct reading of a 95% confidence interval is: "
            "if we repeated the sampling many times, about 95% of the intervals would cover the true parameter.\n\n"
            "### p-values and their misuse\n\n"
            "A p-value is 'the probability of seeing a result this extreme or more extreme, **assuming the null hypothesis is true**'. It is **not** "
            "'the probability that the strategy works'. The most dangerous misuse is **multiple testing**: test enough random "
            "strategies and a few will come out 'significant' on luck alone."
        ),
        code(
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "from quant_math_roadmap.math.probability import simulate_normal\n"
            "from quant_math_roadmap.math.statistics import (\n"
            "    bootstrap_mean_ci, confidence_interval_mean,\n"
            "    false_discovery_demo, one_sample_ttest, standard_error_of_mean,\n"
            ")\n"
            "from quant_math_roadmap.finance.metrics import sharpe_ratio\n"
            "import pandas as pd"
        ),
        md("### Standard error and confidence interval of a mean return"),
        code(
            "returns = simulate_normal(mean=0.0004, std=0.012, size=252, seed=42)\n"
            "se = standard_error_of_mean(returns)\n"
            "lower, upper = confidence_interval_mean(returns, confidence=0.95)\n"
            "print(f'Sample mean daily return = {returns.mean():.6f}')\n"
            "print(f'Standard error = {se:.6f}')\n"
            "print(f'95% confidence interval = [{lower:.6f}, {upper:.6f}]')\n"
            "print('Note: the interval most likely covers 0 — we cannot rule out a true expected return of 0.')"
        ),
        md("### Bootstrap confidence interval"),
        code(
            "boot_lower, boot_upper = bootstrap_mean_ci(\n"
            "    returns, confidence=0.95, n_resamples=5000, seed=0)\n"
            "print(f'bootstrap 95% confidence interval      = [{boot_lower:.6f}, {boot_upper:.6f}]')\n"
            "print(f't-distribution 95% confidence interval = [{lower:.6f}, {upper:.6f}]')\n"
            "print('The two methods give similar intervals; the bootstrap needs no normality assumption.')"
        ),
        md(
            "### Block bootstrap: when returns are autocorrelated\n\n"
            "The plain bootstrap treats every observation as independently resamplable — an implicit i.i.d. assumption. "
            "If returns are **autocorrelated** (momentum-style strategies often are), the plain bootstrap "
            "**understates** the uncertainty of the mean return. The **circular block bootstrap** resamples whole "
            "contiguous blocks instead, preserving the dependence structure within each block.\n\n"
            "Below we use a highly autocorrelated AR(1) series to show the gap between the two methods."
        ),
        code(
            "from quant_math_roadmap.math.statistics import block_bootstrap_mean_ci\n"
            "from quant_math_roadmap.data import generate_ar1_series\n"
            "\n"
            "# AR(1) with phi=0.9: the effective sample size is far smaller than the nominal one\n"
            "persistent = generate_ar1_series(2000, phi=0.9, seed=7).to_numpy()\n"
            "plain_ci = bootstrap_mean_ci(persistent, seed=0)\n"
            "block_ci = block_bootstrap_mean_ci(persistent, block_size=50, seed=0)\n"
            "print(f'plain bootstrap 95% CI width = {plain_ci[1] - plain_ci[0]:.4f}')\n"
            "print(f'block bootstrap 95% CI width = {block_ci[1] - block_ci[0]:.4f}')\n"
            "print('With autocorrelated data, the plain bootstrap gives an interval that is too narrow (overconfident).')"
        ),
        md("### Comparing two synthetic strategies"),
        code(
            "strategy_a = simulate_normal(mean=0.0002, std=0.010, size=252, seed=1)\n"
            "strategy_b = simulate_normal(mean=0.0007, std=0.018, size=252, seed=2)\n"
            "for name, s in [('Strategy A', strategy_a), ('Strategy B', strategy_b)]:\n"
            "    t = one_sample_ttest(s, popmean=0.0)\n"
            "    ci = confidence_interval_mean(s)\n"
            "    print(f'{name}: mean={s.mean():.6f}, p-value={t.p_value:.3f}, '\n"
            "          f'95% CI=[{ci[0]:.6f}, {ci[1]:.6f}]')"
        ),
        md(
            "Even when one strategy has the higher sample mean, its p-value can still be insignificant and its confidence interval can still cover 0. "
            "**A higher historical mean return does not equal a higher true expected return.**"
        ),
        md(
            "### Multiple testing: a false-positive factory\n\n"
            "Below we generate a large batch of **pure-noise** strategies (every true expected return is 0) and see how many "
            "get falsely flagged as 'significant' at $\\alpha=0.05$."
        ),
        code(
            "demo = false_discovery_demo(n_strategies=500, n_periods=252,\n"
            "                            alpha=0.05, seed=0)\n"
            "for k, v in demo.items():\n"
            "    print(f'{k}: {v}')\n"
            "print()\n"
            "print('All 500 strategies are pure noise, so every \"significant\" result is a false positive.')"
        ),
        code(
            "# Visualization: the equity curve of the best noise strategy can look gorgeous too\n"
            "rng = np.random.default_rng(0)\n"
            "noise = rng.standard_normal((500, 252)) * 0.01\n"
            "totals = (1 + noise).prod(axis=1) - 1\n"
            "best = noise[int(np.argmax(totals))]\n"
            "equity = (1 + pd.Series(best)).cumprod()\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(equity.index, equity.values, label='The \"best\" of 500 noise strategies')\n"
            "ax.axhline(1.0, linestyle='--', label='Starting capital')\n"
            "ax.set_title('A beautiful equity curve — built on pure luck')\n"
            "ax.set_xlabel('Trading day')\n"
            "ax.set_ylabel('Equity (start = 1)')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md(
            "This curve was generated entirely from noise, yet it may look prettier than a strategy with genuine signal. "
            "**A beautiful equity curve cannot prove that a strategy works.**"
        ),
        md(
            "### Turning 'multiple testing' into a number: PSR and the Deflated Sharpe Ratio\n\n"
            "We just showed that 'test enough strategies and a few will look significant'. Bailey and "
            "López de Prado turned that warning into computable metrics:\n\n"
            "- **PSR (Probabilistic Sharpe Ratio)**: the probability that the true Sharpe exceeds a benchmark, "
            "after accounting for sample length, skewness and kurtosis;\n"
            "- **DSR (Deflated Sharpe Ratio)**: raises the benchmark from 0 to "
            "'the expected Sharpe of the luckiest among N skill-less strategies' — the more strategies you tried, "
            "the higher the bar the winner has to clear."
        ),
        code(
            "from quant_math_roadmap.finance.metrics import (\n"
            "    deflated_sharpe_ratio, expected_max_sharpe, probabilistic_sharpe_ratio,\n"
            ")\n"
            "\n"
            "# Reuse the 500 pure-noise strategies from above: pick the 'champion' with the highest total return\n"
            "best_returns = pd.Series(best)\n"
            "\n"
            "# Per-period Sharpe estimates of each strategy; their cross-strategy std feeds the expected-max formula\n"
            "per_period_sr = noise.mean(axis=1) / noise.std(axis=1, ddof=1)\n"
            "sr_std = float(per_period_sr.std(ddof=1))\n"
            "\n"
            "psr = probabilistic_sharpe_ratio(best_returns)\n"
            "benchmark = expected_max_sharpe(500, sr_std=sr_std)\n"
            "dsr = deflated_sharpe_ratio(best_returns, n_trials=500, sr_std=sr_std)\n"
            "print(f'Champion strategy PSR (benchmark SR=0)        = {psr:.4f}  <- looks quite convincing')\n"
            "print(f'Expected max SR across 500 trials             = {benchmark:.4f}')\n"
            "print(f'Champion strategy DSR (selection effect removed) = {dsr:.4f}  <- the mask comes off')"
        ),
        md(
            "The PSR looks high — but only because we **picked the luckiest strategy**. Once the benchmark honestly "
            "accounts for 'we tried 500 times', the DSR collapses: this strategy's "
            "'outstanding' performance is indistinguishable from pure luck. **When reporting backtest results, you must also report "
            "how many configurations you tried in total.**"
        ),
        md("### A caution on risk-adjusted metrics"),
        code(
            "sr = sharpe_ratio(pd.Series(returns), frequency='daily')\n"
            "print(f'Annualized Sharpe ratio = {sr:.3f}')\n"
            "print('Caution: the Sharpe ratio is an estimate with its own sampling error; it ignores skewness and fat tails;')\n"
            "print('with a short sample, a backtest Sharpe of 2 can still be consistent with a true Sharpe of 0.')"
        ),
        exercises_intro_en(),
        md(
            "### Basic exercises\n\n"
            "1. Write the correct definition of a p-value in one sentence.\n"
            "2. What is the correct interpretation of a '95% confidence interval'? What is the common incorrect one?\n"
            "3. Why does 'testing many strategies and picking the best one' rob the p-value of its meaning?"
        ),
        md("### Applied exercises"),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 1: bootstrap strategy_a and compare the widths of the 90% and 99% confidence intervals."
            ),
            starter=(
                "ci90 = None  # TODO: bootstrap_mean_ci(strategy_a, confidence=0.90, seed=0)\n"
                "ci99 = None  # TODO: bootstrap_mean_ci(strategy_a, confidence=0.99, seed=0)\n"
                "if ci90 and ci99:\n"
                "    print('90% width:', ci90[1] - ci90[0])\n"
                "    print('99% width:', ci99[1] - ci99[0])"
            ),
            answer=(
                "ci90 = bootstrap_mean_ci(strategy_a, confidence=0.90, seed=0)\n"
                "ci99 = bootstrap_mean_ci(strategy_a, confidence=0.99, seed=0)\n"
                "print('90% width:', round(ci90[1] - ci90[0], 6))\n"
                "print('99% width:', round(ci99[1] - ci99[0], 6))\n"
                "print('Higher confidence means a wider interval — more conservative.')"
            ),
        ),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 2: change alpha to 0.01 in false_discovery_demo and\n"
                "# watch how the number of false positives changes."
            ),
            starter=(
                "strict = None  # TODO: false_discovery_demo(n_strategies=500, alpha=0.01, seed=0)\n"
                "if strict is not None:\n"
                "    print(strict)"
            ),
            answer=(
                "strict = false_discovery_demo(n_strategies=500, n_periods=252,\n"
                "                              alpha=0.01, seed=0)\n"
                "print('False positives at alpha=0.01:', strict['n_false_positives'])\n"
                "print('Theoretical expectation:', strict['expected_false_positives'])\n"
                "print('A stricter alpha reduces false positives but still cannot fully eliminate the multiple-testing problem.')"
            ),
        ),
        md(
            "### Reflection question\n\n"
            "1. You found a strategy with a great backtest among a large grid of parameter combinations. Before believing in it, "
            "what should you do about 'multiple testing' and 'out-of-sample validation'?"
        ),
        *quiz_cells_en(
            solution,
            week=4,
            items=[
                (
                    "What is the correct definition of a p-value?",
                    [
                        "The probability that the null hypothesis is true",
                        "The probability of seeing a result this extreme or more extreme, given that the null hypothesis is true",
                        "The probability that the strategy works",
                        "The probability of making a Type I error",
                    ],
                    "B",
                    "A p-value is the conditional probability P(data this extreme | H₀ is true), not the probability of H₀ or of the strategy itself.",
                ),
                (
                    "What is the correct interpretation of a 95% confidence interval?",
                    [
                        "The parameter has a 95% probability of lying inside the interval",
                        "Under repeated sampling, about 95% of the intervals would cover the true parameter",
                        "95% of the data falls inside the interval",
                        "The prediction accuracy is 95%",
                    ],
                    "B",
                    "It is the interval, not the parameter, that is random — that is the frequentist definition of a confidence interval.",
                ),
                (
                    "Testing 100 pure-noise strategies at significance level α=0.05, how many do we expect to be 'significant'?",
                    ["0", "1", "5", "50"],
                    "C",
                    "Each test has a 5% false-positive rate, so we expect 100 × 0.05 = 5 — the core of the multiple-testing problem.",
                ),
                (
                    "What is the purpose of the block bootstrap relative to the plain bootstrap?",
                    [
                        "Faster computation",
                        "Preserving the autocorrelation structure of the data",
                        "Making the sample larger",
                        "Reducing variance",
                    ],
                    "B",
                    "Resampling whole blocks preserves short-range dependence; the plain bootstrap understates uncertainty on autocorrelated data.",
                ),
            ],
        ),
        mistakes_en(
            [
                "Reading a p-value as 'the probability that the strategy works'.",
                "Testing many strategies and reporting only the best one, without any multiple-testing correction.",
                "Mistaking statistical significance for economic significance (even a real effect can be eaten by costs).",
                "Drawing conclusions from a single backtest Sharpe ratio while ignoring its sampling error.",
            ]
        ),
        checklist_en(
            [
                "Compute and interpret confidence intervals for a mean return (t-based and bootstrap).",
                "State the meaning of a p-value correctly.",
                "Demonstrate and explain the false positives created by multiple testing.",
                "Name at least three limitations of the Sharpe ratio.",
            ]
        ),
        footer_references_en(solution),
    ]
    return cells
