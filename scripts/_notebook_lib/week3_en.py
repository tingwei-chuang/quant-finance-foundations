"""Builder for the Week 3 notebook — English edition.

Generated content mirrors week3.py one-for-one (same cells, same code
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
        week="Week 3",
        title="Probability refresher: simulation, LLN and CLT",
        objectives=[
            "Simulate common distributions and estimate moments from samples.",
            "Visualize the Law of Large Numbers (LLN) with simulation.",
            "Visualize the Central Limit Theorem (CLT) with simulation.",
            "Connect sampling uncertainty to 'estimating a strategy's mean return'.",
        ],
        hours="7–9 hours",
        prereqs=["Random variables, expectation and variance", "Basic numpy"],
        resources=[
            (
                "MIT OpenCourseWare 18.05 Introduction to Probability and Statistics",
                "https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/",
            ),
        ],
    )
    cells += [
        md(
            "## Concepts\n\n"
            "### Law of Large Numbers (LLN)\n\n"
            "As the sample size $n$ grows, the sample mean $\\bar X_n$ converges to the true expected value $\\mu$:\n\n"
            "$$ \\bar X_n = \\frac1n\\sum_{i=1}^n X_i \\xrightarrow[n\\to\\infty]{} \\mu. $$\n\n"
            "### Central Limit Theorem (CLT)\n\n"
            "Whatever the shape of the population distribution, the **sampling distribution** of the sample mean approaches a normal distribution:\n\n"
            "$$ \\frac{\\bar X_n - \\mu}{\\sigma/\\sqrt n} \\xrightarrow{d} N(0, 1). $$\n\n"
            "The LLN tells us **where** the mean converges to; the CLT tells us "
            "**how much uncertainty** the mean carries at finite $n$ (the standard error $\\sigma/\\sqrt n$)."
        ),
        code(
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "from quant_math_roadmap.math.probability import (\n"
            "    empirical_moments, running_mean,\n"
            "    sampling_distribution_of_mean,\n"
            "    simulate_bernoulli, simulate_normal,\n"
            ")\n"
            "\n"
            "rng = np.random.default_rng(2024)"
        ),
        md(
            "### Simulating distributions and estimating moments\n\n"
            "Below we first simulate a normal distribution (continuous), then a Bernoulli distribution (discrete: success/failure). "
            "In strategy research a Bernoulli naturally models binary events like 'did we call the direction correctly?'"
        ),
        code(
            "# Bernoulli(p=0.55): e.g. an indicator for 'the market goes up tomorrow'; p is the conditional probability\n"
            "wins = simulate_bernoulli(p=0.55, size=10_000, seed=0)\n"
            "print('Bernoulli sample mean (≈ p):', round(float(wins.mean()), 3))\n"
            "print('Bernoulli theoretical variance p(1-p) =', round(0.55 * 0.45, 4))\n"
            "print('Bernoulli sample variance             =', round(float(wins.var(ddof=1)), 4))"
        ),
        code(
            "normal_draws = simulate_normal(mean=0.001, std=0.02, size=10_000, seed=1)\n"
            "moments = empirical_moments(normal_draws)\n"
            "print('Estimated moments:', {k: round(v, 6) for k, v in moments.items()})\n"
            "print('True mean = 0.001, true std = 0.02')"
        ),
        md("### Visualizing the LLN: convergence of the sample mean"),
        code(
            "samples = simulate_normal(mean=0.05, std=1.0, size=20_000, seed=3)\n"
            "path = running_mean(samples)\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(range(1, len(path) + 1), path, label='Running sample mean')\n"
            "ax.axhline(0.05, linestyle='--', label='True expected value = 0.05')\n"
            "ax.set_title('Law of Large Numbers: the sample mean converges as n grows')\n"
            "ax.set_xlabel('Sample size n')\n"
            "ax.set_ylabel('Running mean')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md(
            "The curve swings wildly at first, then gradually settles onto the true expected value as $n$ increases. "
            "**The early swings are exactly sampling uncertainty** — and they are why the average return from a short backtest cannot be taken at face value."
        ),
        md("### Visualizing the CLT: the sampling distribution of the mean"),
        code(
            "small = sampling_distribution_of_mean(\n"
            "    population_sampler='exponential', sample_size=5,\n"
            "    n_experiments=5000, seed=4)\n"
            "large = sampling_distribution_of_mean(\n"
            "    population_sampler='exponential', sample_size=200,\n"
            "    n_experiments=5000, seed=4)\n"
            "\n"
            "fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))\n"
            "axes[0].hist(small, bins=40)\n"
            "axes[0].set_title('Distribution of the sample mean, n=5')\n"
            "axes[0].set_xlabel('Sample mean')\n"
            "axes[0].set_ylabel('Count')\n"
            "axes[1].hist(large, bins=40)\n"
            "axes[1].set_title('Distribution of the sample mean, n=200')\n"
            "axes[1].set_xlabel('Sample mean')\n"
            "axes[1].set_ylabel('Count')\n"
            "plt.tight_layout()\n"
            "plt.show()\n"
            "print('n=5 standard deviation:', round(float(np.std(small)), 4))\n"
            "print('n=200 standard deviation:', round(float(np.std(large)), 4))"
        ),
        md(
            "The population is **exponential** (heavily right-skewed), yet the distribution of the sample mean looks more and more normal as $n$ grows, "
            "and becomes more and more concentrated (the standard error shrinks). That is the CLT."
        ),
        md(
            "### Connecting to strategy returns\n\n"
            "Think of 'a strategy's daily return' as a random variable. What we really want to know is its "
            "**true expected return $\\mu$**, but we can only estimate it with the sample mean from a finite sample. "
            "The CLT tells us the uncertainty of that sample mean is $\\sigma/\\sqrt n$ — "
            "the more volatile the returns and the less data we have, the less reliable the estimate."
        ),
        code(
            "# A strategy whose true expected return is 0 — it just got lucky\n"
            "strategy = simulate_normal(mean=0.0, std=0.01, size=252, seed=99)\n"
            "mean_est = strategy.mean()\n"
            "se = strategy.std(ddof=1) / np.sqrt(len(strategy))\n"
            "print(f'Sample mean daily return over one year = {mean_est:.6f}')\n"
            "print(f'Standard error = {se:.6f}')\n"
            "print('The sample mean looks nonzero, but this may well be pure sampling noise.')"
        ),
        exercises_intro_en(),
        md(
            "### Basic exercises\n\n"
            "1. In your own words, explain what question the LLN answers and what question the CLT answers.\n"
            "2. Given the standard error $\\sigma/\\sqrt n$, how many times more samples do you need to cut the standard error in half?\n"
            "3. Why can the sample mean be approximately normal even when the population is not normal?"
        ),
        md("### Applied exercises"),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 1: simulate 50000 flips of a fair coin, compute the running mean\n"
                "# of the proportion of heads, and confirm it converges to 0.5."
            ),
            starter=(
                "flips = rng.integers(0, 2, size=50_000).astype(float)\n"
                "coin_path = None  # TODO: running_mean(flips)\n"
                "if coin_path is not None:\n"
                "    print('Final running proportion:', round(float(coin_path[-1]), 4))"
            ),
            answer=(
                "flips = rng.integers(0, 2, size=50_000).astype(float)\n"
                "coin_path = running_mean(flips)\n"
                "print('Final running proportion:', round(float(coin_path[-1]), 4))\n"
                "assert abs(coin_path[-1] - 0.5) < 0.02"
            ),
        ),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 2: run 4000 experiments for each of sample_size = 2, 10, 50, 250,\n"
                "# print the standard deviation of the sample mean, and watch it shrink with n."
            ),
            starter=(
                "for n in [2, 10, 50, 250]:\n"
                "    means = None  # TODO: sampling_distribution_of_mean(sample_size=n, n_experiments=4000, seed=0)\n"
                "    if means is not None:\n"
                "        print(f'n={n:>3}: std of mean = {np.std(means):.4f}')"
            ),
            answer=(
                "for n in [2, 10, 50, 250]:\n"
                "    means = sampling_distribution_of_mean(\n"
                "        sample_size=n, n_experiments=4000, seed=0)\n"
                "    print(f'n={n:>3}: std of mean = {np.std(means):.4f}')"
            ),
        ),
        md(
            "### Reflection question\n\n"
            "1. Suppose someone hands you a strategy whose 'average daily return over the past year was positive'. "
            "Based on this week's material, what reasons would you give for doubting that this proves it truly has a positive expected return?"
        ),
        *quiz_cells_en(
            solution,
            week=3,
            items=[
                (
                    "What does the Law of Large Numbers (LLN) describe?",
                    [
                        "The sample mean converges to the population expected value",
                        "The sample mean follows a normal distribution",
                        "The variance vanishes",
                        "All distributions eventually become normal",
                    ],
                    "A",
                    "The LLN says 'where it converges'; the shape of the distribution is the CLT's job.",
                ),
                (
                    "What does the Central Limit Theorem (CLT) describe?",
                    [
                        "The sample mean converges to the expected value",
                        "The standardized sample mean approaches a normal distribution",
                        "The sample must be very large before the mean can be computed",
                        "The population must be normal",
                    ],
                    "B",
                    "Whatever the population shape, the standardized sample mean approaches N(0,1) — the foundation for quantifying uncertainty.",
                ),
                (
                    "To cut the standard error σ/√n in half, the sample size must become how many times larger?",
                    ["2 times", "4 times", "√2 times", "8 times"],
                    "B",
                    "The standard error is inversely proportional to √n, so halving it requires 4× the samples — precision comes at a quadratic price.",
                ),
                (
                    "What is the variance of a Bernoulli(p) random variable?",
                    ["p", "p²", "p(1−p)", "1−p"],
                    "C",
                    "E[X]=p and E[X²]=p, so Var = p − p² = p(1−p), which is largest at p=0.5.",
                ),
            ],
        ),
        mistakes_en(
            [
                "Conflating the LLN (where the mean converges) with the CLT (how much uncertainty it carries).",
                "Forgetting to set a random seed, making simulation results irreproducible.",
                "Estimating a mean from a tiny sample and treating it as the precise true value.",
                "Concluding the expected value is positive just because the sample mean is positive.",
            ]
        ),
        checklist_en(
            [
                "Distinguish and explain the LLN and the CLT using simulation.",
                "Compute and interpret the standard error of the sample mean.",
                "Explain why the average of short-horizon strategy returns cannot be taken at face value.",
            ]
        ),
        footer_references_en(solution),
    ]
    return cells
