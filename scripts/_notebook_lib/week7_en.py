"""Builder for the Week 7 notebook — English edition.

Generated content mirrors ``week7.py`` (the Traditional Chinese original) cell
for cell; only the natural language differs. See
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
        week="Week 7",
        title="Time-Series Diagnostics",
        objectives=[
            "Compare the statistical behavior of price series and return series.",
            "Compute and interpret the autocorrelation function (ACF).",
            "Compute rolling volatility and observe volatility clustering.",
            "Compare stationary (AR(1)) and non-stationary (random walk) series.",
        ],
        hours="8–10 hours",
        prereqs=["Returns from Week 1", "Random variables from Week 3"],
        resources=[
            ("Forecasting: Principles and Practice, the Pythonic Way", "https://otexts.com/fpppy/"),
            (
                "Penn State STAT 510 Applied Time Series Analysis",
                "https://online.stat.psu.edu/stat510/",
            ),
        ],
    )
    cells += [
        md(
            "## Concepts\n\n"
            "### Stationarity\n\n"
            "A **stationary** series has statistical properties (mean, variance, "
            "autocorrelation) that do not change over time. Price series are "
            "usually **non-stationary** (they trend and drift); return series "
            "are usually **much closer to stationary**.\n\n"
            "### The autocorrelation function (ACF)\n\n"
            "The ACF measures how a series correlates with its own lagged values:\n\n"
            "$$ \\rho_k = \\frac{\\operatorname{Cov}(x_t, x_{t-k})}"
            "{\\operatorname{Var}(x_t)}. $$\n\n"
            "**White noise** has an ACF close to 0 at every nonzero lag.\n\n"
            "### Why random splits do not apply\n\n"
            "Time series are ordered. A random train/test split lets the model "
            "'see the future', creating look-ahead bias — the central theme of "
            "Week 8."
        ),
        code(
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "from quant_math_roadmap.data import (\n"
            "    SyntheticConfig, generate_correlated_prices,\n"
            "    generate_ar1_series, generate_random_walk,\n"
            ")\n"
            "from quant_math_roadmap.finance.returns import simple_returns\n"
            "from quant_math_roadmap.time_series.diagnostics import (\n"
            "    adf_stationarity_test, autocorrelation_function,\n"
            "    rolling_volatility,\n"
            ")\n"
            "\n"
            "config = SyntheticConfig(n_assets=1, n_periods=756, seed=21,\n"
            "                         vol_regime_multiplier=2.0)\n"
            "prices = generate_correlated_prices(config).iloc[:, 0]\n"
            "returns = simple_returns(prices)"
        ),
        md("### Prices vs returns"),
        code(
            "fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)\n"
            "axes[0].plot(prices.index, prices.values)\n"
            "axes[0].set_title('Price series (usually non-stationary: it trends)')\n"
            "axes[0].set_ylabel('Price')\n"
            "axes[1].plot(returns.index, returns.values)\n"
            "axes[1].set_title('Return series (closer to stationary, but with volatility clustering)')\n"
            "axes[1].set_xlabel('Date')\n"
            "axes[1].set_ylabel('Daily return')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        md("### The ADF stationarity test"),
        code(
            "price_adf = adf_stationarity_test(prices)\n"
            "return_adf = adf_stationarity_test(returns)\n"
            "print('Price series  ADF p-value :', round(price_adf['p_value'], 4))\n"
            "print('Return series ADF p-value :', round(return_adf['p_value'], 4))\n"
            "print('A small p-value = evidence against a unit root (leaning stationary).')"
        ),
        md("### The autocorrelation function"),
        code(
            "acf_returns = autocorrelation_function(returns, max_lag=20)\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.bar(acf_returns.index, acf_returns.values)\n"
            "ax.set_title('Autocorrelation function (ACF) of returns')\n"
            "ax.set_xlabel('Lag')\n"
            "ax.set_ylabel('Autocorrelation')\n"
            "plt.show()\n"
            "print('The return ACF is mostly near 0 at nonzero lags — close to white noise.')"
        ),
        md("### Rolling volatility and volatility clustering"),
        code(
            "roll_vol = rolling_volatility(returns, window=40)\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(roll_vol.index, roll_vol.values, label='40-period rolling volatility')\n"
            "ax.set_title('Rolling volatility: volatility clustering')\n"
            "ax.set_xlabel('Date')\n"
            "ax.set_ylabel('Rolling standard deviation')\n"
            "ax.legend()\n"
            "plt.show()\n"
            "print('The synthetic data adds a volatility regime shift in the second half — clearly visible here.')"
        ),
        md("### Stationary vs non-stationary: AR(1) vs a random walk"),
        code(
            "ar1 = generate_ar1_series(600, phi=0.6, seed=5)\n"
            "walk = generate_random_walk(600, drift=0.0, seed=5)\n"
            "\n"
            "fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)\n"
            "axes[0].plot(ar1.index, ar1.values)\n"
            "axes[0].set_title('AR(1), phi=0.6 (stationary: reverts to its mean)')\n"
            "axes[0].set_ylabel('Value')\n"
            "axes[1].plot(walk.index, walk.values)\n"
            "axes[1].set_title('Random walk (non-stationary: it drifts and does not come back)')\n"
            "axes[1].set_xlabel('Date')\n"
            "axes[1].set_ylabel('Value')\n"
            "plt.tight_layout()\n"
            "plt.show()\n"
            "print('AR(1)       ADF p-value:', round(adf_stationarity_test(ar1)['p_value'], 4))\n"
            "print('Random walk ADF p-value:', round(adf_stationarity_test(walk)['p_value'], 4))"
        ),
        exercises_intro_en(),
        md(
            "### Basic exercises\n\n"
            "1. Define stationarity in your own words, and explain why prices are usually non-stationary.\n"
            "2. What does the ACF of white noise look like?\n"
            "3. Explain what volatility clustering is."
        ),
        md("### Applied exercises"),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 1: generate three AR(1) series with phi=0.0, phi=0.5, and phi=0.9,\n"
                "# compute each one's lag-1 autocorrelation, and confirm it is close to phi."
            ),
            starter=(
                "from quant_math_roadmap.time_series.diagnostics import autocorrelation\n"
                "for phi in [0.0, 0.5, 0.9]:\n"
                "    series = generate_ar1_series(4000, phi=phi, seed=1)\n"
                "    ac1 = None  # TODO: autocorrelation(series, 1)\n"
                "    print(f'phi={phi}: lag-1 autocorr = {ac1}')"
            ),
            answer=(
                "from quant_math_roadmap.time_series.diagnostics import autocorrelation\n"
                "for phi in [0.0, 0.5, 0.9]:\n"
                "    series = generate_ar1_series(4000, phi=phi, seed=1)\n"
                "    ac1 = autocorrelation(series, 1)\n"
                "    print(f'phi={phi}: lag-1 autocorr = {ac1:.3f}')"
            ),
        ),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 2: compute the ACF for the price series and the return series, and compare them."
            ),
            starter=(
                "acf_price = None  # TODO: autocorrelation_function(prices, max_lag=20)\n"
                "if acf_price is not None:\n"
                "    print('Price lag-1 autocorrelation :', round(acf_price.iloc[1], 4))\n"
                "    print('Return lag-1 autocorrelation:', round(acf_returns.iloc[1], 4))"
            ),
            answer=(
                "acf_price = autocorrelation_function(prices, max_lag=20)\n"
                "print('Price lag-1 autocorrelation :', round(acf_price.iloc[1], 4))\n"
                "print('Return lag-1 autocorrelation:', round(acf_returns.iloc[1], 4))\n"
                "print('Prices are highly autocorrelated (non-stationary); returns are close to white noise.')"
            ),
        ),
        md(
            "### Reflection question\n\n"
            "1. Given that the return ACF is close to 0 almost everywhere, what "
            "does this imply for strategies that try to predict future returns "
            "from past returns?"
        ),
        *quiz_cells_en(
            solution,
            week=7,
            items=[
                (
                    "A stationary series is characterized by?",
                    [
                        "Prices always rise",
                        "Statistical properties (mean, variance, autocorrelation) do not change over time",
                        "No volatility at all",
                        "No autocorrelation at all",
                    ],
                    "B",
                    "Stationarity is time-invariance of the statistical properties; the series itself can still fluctuate randomly.",
                ),
                (
                    "The ACF of white noise at nonzero lags should be?",
                    ["Close to 0", "Close to 1", "Increasing with lag", "All negative"],
                    "A",
                    "White noise is by definition uncorrelated across periods; the theoretical ACF is 0 everywhere except lag 0.",
                ),
                (
                    "AR(1): x_t = φx_{t−1} + ε_t is stationary under which condition?",
                    ["φ > 0", "|φ| < 1", "φ = 1", "φ > 1"],
                    "B",
                    "With |φ|<1 shocks decay away; φ=1 is a random walk (non-stationary).",
                ),
                (
                    "'Volatility clustering' refers to?",
                    [
                        "Returns concentrating near the mean",
                        "High-volatility and low-volatility periods each arriving in clusters",
                        "Prices clustering at round-number levels",
                        "Zero autocorrelation",
                    ],
                    "B",
                    "Returns themselves are nearly uncorrelated, but their magnitude is highly autocorrelated — storms follow storms.",
                ),
            ],
        ),
        mistakes_en(
            [
                "Modeling the non-stationary price series directly instead of converting to returns first.",
                "Using a random train/test split on time series.",
                "Backfilling the leading NaNs of a rolling window with future values.",
                "Over-interpreting weak return autocorrelation as a profitable signal.",
            ]
        ),
        checklist_en(
            [
                "Explain stationarity and judge prices vs returns.",
                "Compute and interpret the ACF.",
                "Compute rolling volatility and recognize volatility clustering.",
                "Explain why random splits are unsuitable for time series.",
            ]
        ),
        footer_references_en(solution),
    ]
    return cells
