"""Builder for the Week 8 notebook — English edition.

Generated content mirrors ``week8.py`` (the Traditional Chinese original) cell
for cell; only the natural language differs. See
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
        week="Week 8",
        title="Walk-Forward Forecasting and Backtest Integrity",
        objectives=[
            "Implement time-based train/test splits and walk-forward evaluation.",
            "Build a forecast model and compare it against naive baselines.",
            "Apply trading costs and compare gross vs net performance.",
            "Deliberately exhibit a leaked model and explain why its results are invalid.",
        ],
        hours="10–12 hours",
        prereqs=["Time series from Week 7", "Regression from Week 5"],
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
            "This week assembles the previous seven weeks into one **correct** "
            "research workflow. The core principles:\n\n"
            "1. **Time-based splits**: the training set always comes before the test set.\n"
            "2. **Walk-forward evaluation**: expanding (anchored start, growing "
            "window) or rolling (fixed length, sliding forward).\n"
            "3. **No leakage**: features at time $t$ may only use information up "
            "to $t$; positions driven by a signal must be **correctly lagged** "
            "to line up with future returns.\n"
            "4. **Trading costs**: compare gross vs net; only net is the honest result.\n"
            "5. **Baselines**: a model that cannot beat a naive baseline has no value.\n\n"
            "> This notebook is **methodology training**, not an investable "
            "strategy. No result here represents real-world profitability."
        ),
        code(
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "from quant_math_roadmap.data import SyntheticConfig, generate_correlated_prices\n"
            "from quant_math_roadmap.finance.returns import simple_returns\n"
            "from quant_math_roadmap.time_series.splits import (\n"
            "    expanding_window_splits, train_test_split_time,\n"
            ")\n"
            "from quant_math_roadmap.time_series.forecasting import (\n"
            "    fit_linear_lag_model, forecast_error_metrics,\n"
            "    historical_mean_forecast, zero_forecast,\n"
            ")\n"
            "from quant_math_roadmap.backtesting.engine import (\n"
            "    buy_and_hold_benchmark, information_coefficient, run_backtest,\n"
            ")\n"
            "from quant_math_roadmap.backtesting.leakage_checks import (\n"
            "    assert_no_lookahead, leaked_strategy_returns, signal_to_positions,\n"
            ")\n"
            "from quant_math_roadmap.backtesting.costs import cost_summary\n"
            "\n"
            "config = SyntheticConfig(n_assets=1, n_periods=900, seed=33)\n"
            "prices = generate_correlated_prices(config).iloc[:, 0]\n"
            "returns = simple_returns(prices)\n"
            "print('Return series length:', len(returns))"
        ),
        md("### A time-based train/test split"),
        code(
            "split = train_test_split_time(len(returns), test_size=0.3)\n"
            "train = returns.iloc[split.train_index]\n"
            "test = returns.iloc[split.test_index]\n"
            "print(f'Train: {len(train)} periods | Test: {len(test)} periods')\n"
            "print('Last train day <', 'first test day:',\n"
            "      train.index[-1] < test.index[0])"
        ),
        md(
            "### Purged splits: a firebreak between train and test\n\n"
            "When features or labels **span multiple periods** (rolling "
            "features, multi-day forward returns), the tail of the training set "
            "and the start of the test set actually **share the same "
            "information** — even with a strictly chronological split, the "
            "boundary still leaks. The fix is 'purging': leave a **gap** between "
            "train and test at least as long as the information overlap. Both "
            "`expanding_window_splits` and `rolling_window_splits` support a "
            "`gap` argument."
        ),
        code(
            "with_gap = list(expanding_window_splits(\n"
            "    len(returns), initial_train_size=600, test_size=50, gap=10))\n"
            "no_gap = list(expanding_window_splits(\n"
            "    len(returns), initial_train_size=600, test_size=50, gap=0))\n"
            "s_gap, s_plain = with_gap[0], no_gap[0]\n"
            "print(f'No gap: train ends at {s_plain.train_index.max()}, '\n"
            "      f'test starts at {s_plain.test_index.min()}')\n"
            "print(f'gap=10: train ends at {s_gap.train_index.max()}, '\n"
            "      f'test starts at {s_gap.test_index.min()}  <- the 10 periods between are used by neither side')\n"
            "print('If a feature uses a 10-period rolling window, gap >= 10 keeps the boundary clean.')"
        ),
        md("### Forecast model vs naive baselines"),
        code(
            "# Honest one-step-ahead forecasts via a walk-forward expanding window\n"
            "predictions, actuals, baseline_mean, baseline_zero = [], [], [], []\n"
            "for sp in expanding_window_splits(len(returns), initial_train_size=400,\n"
            "                                  test_size=1):\n"
            "    tr = returns.iloc[sp.train_index]\n"
            "    te = returns.iloc[sp.test_index]\n"
            "    # Simple linear lag forecast: most recent return times the train-set lag-1 autocorrelation\n"
            "    lag1 = tr.autocorr(lag=1)\n"
            "    pred = lag1 * tr.iloc[-1]\n"
            "    predictions.append(pred)\n"
            "    actuals.append(te.iloc[0])\n"
            "    baseline_mean.append(historical_mean_forecast(tr))\n"
            "    baseline_zero.append(zero_forecast(tr))\n"
            "\n"
            "actual_s = pd.Series(actuals)\n"
            "print('Lag forecast    :', forecast_error_metrics(actual_s, pd.Series(predictions)))\n"
            "print('Historical mean :', forecast_error_metrics(actual_s, pd.Series(baseline_mean)))\n"
            "print('Naive zero      :', forecast_error_metrics(actual_s, pd.Series(baseline_zero)))"
        ),
        md(
            "On synthetic (near white-noise) returns, the forecast model "
            "**usually fails to beat** the naive baselines. That is a healthy "
            "outcome: it honestly reflects how hard returns are to predict."
        ),
        md(
            "### Quantifying forecast power with a multi-lag linear model + the information coefficient (IC)\n\n"
            "The lag-1 forecast above was hand-rolled. `fit_linear_lag_model` fits "
            "$y_t = c + \\sum_k b_k\\, x_{t-k}$ in one go; `information_coefficient` "
            "computes the correlation between the **signal** and **future "
            "returns** — a single number that tells you whether the forecast has "
            "any directional skill."
        ),
        code(
            "# Fit a 3-lag linear model on the training set, then forecast the test set period by period\n"
            "train = returns.iloc[:600]\n"
            "test = returns.iloc[600:]\n"
            "lag_model = fit_linear_lag_model(train, n_lags=3)\n"
            "print('Coefficients [intercept, lag1, lag2, lag3] =', np.round(lag_model.coefficients, 6))\n"
            "\n"
            "# Build test-set forecasts from the sliding window of the 3 most recent historical returns\n"
            "rolling_lags = pd.concat([returns.shift(k) for k in (1, 2, 3)], axis=1)\n"
            "rolling_lags = rolling_lags.loc[test.index]\n"
            "preds = pd.Series(\n"
            "    [lag_model.predict(row.to_numpy()) for _, row in rolling_lags.iterrows()],\n"
            "    index=test.index,\n"
            ")\n"
            "ic = information_coefficient(preds, test)\n"
            "print(f'Test-set information coefficient (IC) = {ic:.4f}')\n"
            "print('|IC| near 0 is expected: synthetic daily returns are essentially white noise.')"
        ),
        md("### Turning signals into positions (lagged correctly to avoid leakage)"),
        code(
            "# Signal: the sign of yesterday's return. Positions must be lagged 1 period before trading.\n"
            "raw_signal = np.sign(returns)\n"
            "positions = signal_to_positions(raw_signal, lag=1)\n"
            "print('First 5 signals  :', raw_signal.head().to_list())\n"
            "print('First 5 positions:', positions.head().to_list())\n"
            "print('Positions are the lagged signal — day one is 0 (no usable information yet).')"
        ),
        md("### Gross vs net: the impact of trading costs"),
        code(
            "result = run_backtest(raw_signal, returns, signal_lag=1,\n"
            "                      cost_per_unit_turnover=0.0005)\n"
            "summary = result.summary()\n"
            "for k, v in summary.items():\n"
            "    print(f'{k}: {v:.6f}')\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(result.gross_equity.index, result.gross_equity.values,\n"
            "        label='gross (before costs)')\n"
            "ax.plot(result.net_equity.index, result.net_equity.values,\n"
            "        label='net (after costs)')\n"
            "bnh = buy_and_hold_benchmark(returns)\n"
            "ax.plot(bnh.index, bnh.values, label='buy-and-hold benchmark', linestyle='--')\n"
            "ax.set_title('Backtest equity curves: gross vs net vs benchmark')\n"
            "ax.set_xlabel('Date')\n"
            "ax.set_ylabel('Equity (start = 1)')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md(
            "Trading costs open a clear gap between gross and net. "
            "**A backtest that only shows gross is not honest.**"
        ),
        md(
            "### The multi-asset version: backtesting a whole portfolio from a weight schedule\n\n"
            "Every discipline from the single-asset engine — lagging, costs, "
            "gross vs net — applies just the same with multiple assets. "
            "`run_portfolio_backtest()` takes a table of **target weights** "
            "(each row computed from information known that day), lags it one "
            "period automatically, and charges costs on the change in weights."
        ),
        code(
            "from quant_math_roadmap.backtesting import run_portfolio_backtest\n"
            "panel_cfg = SyntheticConfig(n_assets=4, n_periods=900, seed=44,\n"
            "                            average_correlation=0.3)\n"
            "panel_prices = generate_correlated_prices(panel_cfg)\n"
            "panel_returns = simple_returns(panel_prices)\n"
            "\n"
            "# Simple demo: fixed equal weights vs 30-day momentum-tilted weights\n"
            "eq_weights = pd.DataFrame(0.25, index=panel_returns.index,\n"
            "                          columns=panel_returns.columns)\n"
            "momentum = panel_returns.rolling(30).mean()\n"
            "tilt = momentum.rank(axis=1)  # momentum rank as the basis for the weights\n"
            "tilt = tilt.div(tilt.sum(axis=1), axis=0).fillna(0.0)\n"
            "\n"
            "res_eq = run_portfolio_backtest(eq_weights, panel_returns,\n"
            "                                cost_per_unit_turnover=0.0005)\n"
            "res_tilt = run_portfolio_backtest(tilt, panel_returns,\n"
            "                                  cost_per_unit_turnover=0.0005)\n"
            "print('Equal weight  :', {k: round(v, 4) for k, v in res_eq.summary().items()})\n"
            "print('Momentum tilt :', {k: round(v, 4) for k, v in res_tilt.summary().items()})\n"
            "print('Note the clearly higher avg_turnover and cost_drag of the momentum version.')"
        ),
        md(
            "### Parameter sweeps: watching curve-fitting happen\n\n"
            "The final lesson: take a strategy with a single knob (the trailing-"
            "momentum lookback), run one backtest per candidate value, and plot "
            "the **in-sample** and **out-of-sample** Sharpe side by side. The "
            "parameter with the best IS Sharpe is usually unremarkable OOS — "
            "that gap is the price of curve-fitting."
        ),
        code(
            "from quant_math_roadmap.backtesting import lookback_parameter_sweep\n"
            "\n"
            "lookbacks = [3, 5, 8, 13, 21, 34, 55, 89]\n"
            "sweep = lookback_parameter_sweep(returns, lookbacks,\n"
            "                                 in_sample_fraction=0.6,\n"
            "                                 cost_per_unit_turnover=0.0005)\n"
            "print(sweep[['is_sharpe', 'oos_sharpe']].round(3))\n"
            "best_is = sweep['is_sharpe'].idxmax()\n"
            "print(f'Best IS lookback = {best_is}, its OOS Sharpe = '\n"
            "      f\"{sweep.loc[best_is, 'oos_sharpe']:.3f}\")"
        ),
        code(
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(sweep.index, sweep['is_sharpe'], marker='o', label='in-sample Sharpe')\n"
            "ax.plot(sweep.index, sweep['oos_sharpe'], marker='s', label='out-of-sample Sharpe')\n"
            "ax.axvline(best_is, linestyle='--', alpha=0.5,\n"
            "           label=f'best IS lookback = {best_is}')\n"
            "ax.set_title('Parameter sweep: how the in-sample winner really looks out of sample')\n"
            "ax.set_xlabel('Momentum lookback (periods)')\n"
            "ax.set_ylabel('Annualized Sharpe')\n"
            "ax.legend()\n"
            "plt.show()\n"
            "print('The peaks of the IS curve are mostly the shape of noise; the OOS curve is closer to the true expectation.')"
        ),
        md(
            "### A deliberate data-leakage demo (invalid by construction)\n\n"
            "The experiment below **cheats on purpose**: it uses the sign of the "
            "**current-period** return as the position — which requires knowing "
            "the future. It inevitably wins every period and looks absurdly "
            "good.\n\n"
            "> **This result must never be treated as a strategy.** Its only "
            "purpose is to teach you what leakage looks like."
        ),
        code(
            "leaked = leaked_strategy_returns(returns)\n"
            "leaked_equity = (1 + leaked).cumprod()\n"
            "honest_equity = result.net_equity\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(leaked_equity.index, leaked_equity.values,\n"
            "        label='[INVALID] leaked model (peeks at the future)')\n"
            "ax.plot(honest_equity.index, honest_equity.values,\n"
            "        label='honest backtest (net)')\n"
            "ax.set_title('Leakage demo: an absurd curve is a warning sign, not a strategy')\n"
            "ax.set_xlabel('Date')\n"
            "ax.set_ylabel('Equity (start = 1)')\n"
            "ax.legend()\n"
            "plt.show()\n"
            "print(f'Leaked total return = {(leaked_equity.iloc[-1] - 1):.2%}  <-- impossible, invalid')\n"
            "print(f'Honest net total return = {(honest_equity.iloc[-1] - 1):.2%}')"
        ),
        code(
            "# Automated leakage check: using the current-period return as a feature gets caught\n"
            "try:\n"
            "    assert_no_lookahead(returns, returns, name='current-period return as feature')\n"
            "    print('No leakage detected')\n"
            "except ValueError as exc:\n"
            "    print('Leakage detected:', exc)"
        ),
        exercises_intro_en(),
        md(
            "### Basic exercises\n\n"
            "1. In your own words, explain the difference between an expanding window and a rolling window.\n"
            "2. Why must positions driven by a signal be lagged?\n"
            "3. What is survivorship bias, and why does it make backtests overly optimistic?"
        ),
        md("### Applied exercises"),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 1: raise trading costs from 5 bps to 20 bps and compare net total returns."
            ),
            starter=(
                "high_cost = None  # TODO: run_backtest(raw_signal, returns, signal_lag=1, cost_per_unit_turnover=0.002)\n"
                "if high_cost is not None:\n"
                "    print('20 bps net total return:', high_cost.summary()['total_net_return'])"
            ),
            answer=(
                "high_cost = run_backtest(raw_signal, returns, signal_lag=1,\n"
                "                         cost_per_unit_turnover=0.002)\n"
                "print('5 bps  net total return:', round(summary['total_net_return'], 4))\n"
                "print('20 bps net total return:', round(high_cost.summary()['total_net_return'], 4))\n"
                "print('Higher costs, worse net performance — high-turnover strategies are especially cost-sensitive.')"
            ),
        ),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 2: use cost_summary to compare gross vs net total returns and the cost drag."
            ),
            starter=(
                "cs = None  # TODO: cost_summary(result.gross_returns, result.net_returns)\n"
                "if cs is not None:\n"
                "    print(cs)"
            ),
            answer=(
                "cs = cost_summary(result.gross_returns, result.net_returns)\n"
                "for k, v in cs.items():\n"
                "    print(f'{k}: {v:.6f}')\n"
                "print('cost_drag is always >= 0: costs can only drag performance down.')"
            ),
        ),
        md(
            "### Reflection question\n\n"
            "1. Look back over Weeks 1–7. Where could a great-looking backtest "
            "have quietly introduced leakage, overfitting, or multiple-testing "
            "problems? List at least three places, and check them against "
            f"[`docs/common_backtesting_mistakes.md`]({docs_prefix_en(solution)}common_backtesting_mistakes.md)."
        ),
        *quiz_cells_en(
            solution,
            week=8,
            items=[
                (
                    "Positions must be lagged at least one period behind the signal because?",
                    [
                        "It increases returns",
                        "A signal computed only at the close of period t can be traded no sooner than the next period",
                        "It reduces trading costs",
                        "It makes the curve smoother",
                    ],
                    "B",
                    "Without the lag you trade on current-period (future) information — the most common look-ahead bias.",
                ),
                (
                    "The difference between expanding and rolling windows is?",
                    [
                        "An expanding window has fixed length",
                        "A rolling window has fixed length and gradually forgets older data",
                        "They are exactly the same",
                        "Rolling windows cannot be used on time series",
                    ],
                    "B",
                    "An expanding window is anchored at the start and keeps learning more; rolling has fixed length, suited to a drifting data-generating process.",
                ),
                (
                    "The purpose of a purge gap (space between train and test) is?",
                    [
                        "Faster computation",
                        "Removing leakage from overlapping information at the boundary (e.g. multi-period return labels)",
                        "Increasing the sample size",
                        "Lowering trading costs",
                    ],
                    "B",
                    "When features or labels span multiple periods, adjacent train/test share information; the gap clears it out.",
                ),
                (
                    "After a parameter sweep, the in-sample best parameter usually performs out of sample?",
                    [
                        "Just as well",
                        "Better",
                        "Clearly worse — part of the IS performance was luck",
                        "It cannot be computed",
                    ],
                    "C",
                    "The IS best is also the luckiest; OOS the luck is gone and performance reverts toward the mean.",
                ),
            ],
        ),
        mistakes_en(
            [
                "Using random splits instead of time-based splits.",
                "Not lagging positions behind the signal — i.e. peeking at the future (look-ahead bias).",
                "Reporting only gross performance, ignoring trading costs and turnover.",
                "Not comparing against naive baselines (zero return, historical mean, buy-and-hold).",
                "Mistaking the deliberately leaked, absurd result for a real strategy.",
                "Backfilling the leading NaNs of rolling features with future information.",
            ]
        ),
        checklist_en(
            [
                "Implement time-based splits and walk-forward evaluation.",
                "Compare a forecast model honestly against naive baselines.",
                "Apply trading costs and compare gross vs net.",
                "Recognize leakage and explain why its results are invalid.",
                "Complete a small leak-free, cost-aware, reproducible backtesting workflow.",
            ]
        ),
        md(
            "## Closing thoughts\n\n"
            "After eight weeks you can go from 'refreshing the mathematical "
            "foundations' to 'a small but correct, leakage-proof quantitative "
            "research workflow'. Remember the core belief of this roadmap:\n\n"
            "**Evaluate correctly before refining models; be reproducible "
            "before chasing performance.**\n\n"
            "This project is education and research-methodology training — "
            "**not investment advice** — and it **claims no** profitable "
            "strategy."
        ),
        footer_references_en(solution),
    ]
    return cells
