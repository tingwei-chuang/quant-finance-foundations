"""Builder for the Week 0 notebook — English edition.

Generated content mirrors week0.py one-for-one (same cells, same code
semantics); only the natural-language content is translated. See
scripts/_notebook_lib/__init__.py for the dispatch table.
"""

from __future__ import annotations

import nbformat as nbf

from .cells import code, ex_code, md
from .parts_en import (
    checklist_en,
    docs_prefix_en,
    exercises_intro_en,
    footer_references_en,
    header_en,
    mistakes_en,
    quiz_cells_en,
)


def week(solution: bool) -> list[nbf.NotebookNode]:
    cells = header_en(
        solution=solution,
        week="Week 0",
        title="Environment Setup and Readiness Check",
        objectives=[
            "Confirm that your Python environment and the `quant_math_roadmap` package work correctly.",
            "Generate and load reproducible synthetic price data.",
            "Honestly self-assess eight topic areas and get a suggested study path.",
        ],
        hours="1.5–2.5 hours",
        prereqs=["Basic Python", "Environment created with uv as described in the README"],
        resources=[],
    )
    cells += [
        md(
            "## 1. Environment check\n\nFirst, confirm your Python version (this project requires 3.12+) and that the core packages import cleanly."
        ),
        code(
            "import sys\n"
            "print('Python', sys.version.split()[0])\n"
            "assert sys.version_info >= (3, 12), 'Please use Python 3.12 or newer'\n"
            "\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib\n"
            "import scipy\n"
            "import statsmodels\n"
            "print('numpy', np.__version__, '| pandas', pd.__version__)\n"
            "print('matplotlib', matplotlib.__version__, '| scipy', scipy.__version__)"
        ),
        code(
            "import quant_math_roadmap as qmr\n"
            "print('quant_math_roadmap version:', qmr.__version__)\n"
            "print('Package imported successfully — your environment is ready.')"
        ),
        md(
            "## 2. Generating and loading synthetic data\n\n"
            "Every notebook in this project **uses synthetic data only by default** — fully reproducible, no network access required.\n\n"
            "Below we first use `SyntheticConfig` to generate a set of correlated asset prices, then show how to load "
            "the project's built-in sample dataset `data/sample/synthetic_prices.csv`."
        ),
        code(
            "import matplotlib.pyplot as plt\n"
            "from quant_math_roadmap.data import (\n"
            "    SyntheticConfig,\n"
            "    generate_correlated_prices,\n"
            "    load_sample_prices,\n"
            ")\n"
            "\n"
            "config = SyntheticConfig(n_assets=3, n_periods=400, seed=20240101)\n"
            "prices = generate_correlated_prices(config)\n"
            "prices.head()"
        ),
        code(
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "for column in prices.columns:\n"
            "    ax.plot(prices.index, prices[column], label=column)\n"
            "ax.set_title('Synthetic asset prices (Week 0 example)')\n"
            "ax.set_xlabel('Date')\n"
            "ax.set_ylabel('Price')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md(
            "Each line above is the price path of one synthetic asset. They are **not** real assets — just teaching tools. "
            "Because we use a fixed random seed, you will get exactly the same result every time you run this."
        ),
        code(
            "sample_prices = load_sample_prices()\n"
            "print('Sample dataset shape:', sample_prices.shape)\n"
            "print('Date range:', sample_prices.index[0].date(), '~', "
            "sample_prices.index[-1].date())\n"
            "sample_prices.head()"
        ),
        md(
            "## 3. Self-assessment checklist\n\n"
            "Honestly rate yourself on each topic below (**1 = completely unfamiliar, 5 = could explain it clearly to someone else**). "
            "This assessment does **not** judge you as a person — it only helps you plan your study.\n\n"
            "| Topic | Week | Your score (1–5) |\n"
            "|------|:--------:|:--------------:|\n"
            "| Linear algebra (eigenvalues, PSD, quadratic forms) | Week 1 |  |\n"
            "| Multivariable calculus (gradient, Hessian, Lagrange) | Week 2 |  |\n"
            "| Probability (LLN, CLT, conditional probability) | Week 3 |  |\n"
            "| Statistical inference (confidence intervals, p-values, bootstrap) | Week 4 |  |\n"
            "| Regression (OLS, beta, residuals) | Week 5 |  |\n"
            "| Financial mathematics (discounting, bonds, option payoffs) | Week 6 |  |\n"
            "| Time series (stationarity, ACF, AR) | Week 7 |  |\n"
            "| Backtest integrity (leakage, transaction costs) | Week 8 |  |\n\n"
            f"Copy your scores into [`docs/progress_tracker.md`]({docs_prefix_en(solution)}progress_tracker.md)."
        ),
        md(
            "## 4. Quick concept questions\n\n"
            "Answer these **without** writing any code — use pen and paper or mental arithmetic (answers are at the end of the notebook):\n\n"
            "1. If an asset's price rises from 100 to 110, what are the simple return and the log return?\n"
            "2. Is the sample mean itself a random variable? Why?\n"
            "3. Why is randomly splitting time-series data into train/test sets dangerous?"
        ),
        exercises_intro_en(),
        md(
            "### Basic exercises\n\n"
            "1. Define simple return and log return, each in one sentence.\n"
            "2. Explain why synthetic data matters for reproducibility.\n"
            "3. List the topics where your self-assessment score is ≤ 2."
        ),
        md("### Applied exercises"),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 1: compute the simple-return series for the first asset in prices.\n"
                "# Hint: you can use quant_math_roadmap.finance.returns.simple_returns"
            ),
            starter=(
                "from quant_math_roadmap.finance.returns import simple_returns\n"
                "first_asset = prices.iloc[:, 0]\n"
                "asset_returns = None  # TODO: replace with simple_returns(first_asset)\n"
                "print(asset_returns if asset_returns is None else asset_returns.head())"
            ),
            answer=(
                "from quant_math_roadmap.finance.returns import simple_returns\n"
                "first_asset = prices.iloc[:, 0]\n"
                "asset_returns = simple_returns(first_asset)\n"
                "asset_returns.head()"
            ),
        ),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 2: compute the mean and standard deviation of that asset's returns.\n"
                "# Think: how much uncertainty is in each of these two numbers? (Weeks 3 and 4 will answer this.)"
            ),
            starter=(
                "mean_return = None   # TODO: asset_returns.mean()\n"
                "std_return = None    # TODO: asset_returns.std(ddof=1)\n"
                "print('mean =', mean_return, '| std =', std_return)"
            ),
            answer=(
                "mean_return = simple_returns(prices.iloc[:, 0]).mean()\n"
                "std_return = simple_returns(prices.iloc[:, 0]).std(ddof=1)\n"
                "print(f'mean = {mean_return:.6f} | std = {std_return:.6f}')"
            ),
        ),
        md(
            "### Reflection question\n\n"
            '1. After seeing any "beautiful equity curve", what three questions should you ask before deciding whether to believe it?'
        ),
        *quiz_cells_en(
            solution,
            week=0,
            items=[
                (
                    "A price rises from 100 to 110. What are the simple return and the log return, approximately?",
                    ["10% and 9.53%", "10% and 10%", "9.53% and 10%", "11% and 10.5%"],
                    "A",
                    "simple = 110/100 − 1 = 10%; log = ln(1.1) ≈ 9.53%. The larger the move, the bigger the gap between the two.",
                ),
                (
                    "Why do all notebooks in this project use synthetic data by default?",
                    [
                        "Real data is not accurate enough",
                        "Reproducibility, offline execution, and no data-licensing issues",
                        "Synthetic data has higher returns",
                        "It downloads faster",
                    ],
                    "B",
                    "Synthetic data makes every result fully reproducible without network access, and avoids third-party data terms of use.",
                ),
                (
                    'What does it mean that "the sample mean is a random variable"?',
                    [
                        "It gives a different result every time you compute it",
                        "It depends on the sample drawn — a different sample gives a different value",
                        "It cannot be computed",
                        "It is always inaccurate",
                    ],
                    "B",
                    "The sample mean is a function of the data; the data are the result of random sampling, so the sample mean itself has a sampling distribution.",
                ),
                (
                    "What is the main problem with a random train/test split for time series?",
                    [
                        "It is too slow to compute",
                        'The training set can contain "future" information, causing look-ahead bias',
                        "The test set is too small",
                        "You cannot make plots",
                    ],
                    "B",
                    'A random split lets the model learn from future data and then "predict" the past, making results systematically over-optimistic.',
                ),
            ],
        ),
        mistakes_en(
            [
                "Mixing up simple returns and log returns without realizing it.",
                "Using random data without a fixed seed, so results cannot be reproduced.",
                "Believing a strategy works just because its equity curve goes up.",
            ]
        ),
        checklist_en(
            [
                "Import `quant_math_roadmap` successfully and run this entire notebook.",
                "Generate and load reproducible synthetic data.",
                "Honestly list your 2–3 weakest topics and plan a study path.",
            ]
        ),
        md(
            "## Suggested study path\n\n"
            "Based on your self-assessment in Section 3:\n\n"
            "- **Any topic scored ≤ 2**: read the matching `docs/math/` or `docs/finance/` concept notes first, "
            "then work through that week's notebook, and budget extra time for the external resources.\n"
            "- **Score of 3**: proceed at the normal pace, but spend extra time on the notebook exercises.\n"
            "- **Score ≥ 4**: you can move through that week faster, but be sure to still complete backtest integrity (Week 8).\n\n"
            "Whatever your self-assessment says, **Week 8 (backtest integrity) is mandatory for everyone**."
        ),
        md(
            "## Answers to the quick concept questions\n\n"
            "1. simple return = 110/100 − 1 = **0.10 (10%)**; "
            "log return = ln(110/100) ≈ **0.0953**. The larger the move, the bigger the gap between the two.\n"
            "2. **Yes.** The sample mean is a function of the data, and the data are the result of random sampling, "
            "so the sample mean is itself a random variable that varies from sample to sample (the topic of Weeks 3 and 4).\n"
            '3. Because a random split lets the model use "future" data to predict the "past", '
            "causing look-ahead bias and making backtest results over-optimistic (the topic of Weeks 7 and 8)."
        ),
        footer_references_en(solution),
    ]
    return cells
