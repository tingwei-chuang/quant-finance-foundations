"""Builder for the Week 7 notebook (auto-extracted from build_notebooks.py).

Per-week modules let one week be edited (and merged) independently of the
others. See scripts/_notebook_lib/__init__.py for the dispatch table.
"""

from __future__ import annotations

import nbformat as nbf

from .cells import code, ex_code, md
from .parts import (
    checklist,
    exercises_intro,
    footer_references,
    header,
    mistakes,
    quiz_cells,
)


def week(solution: bool) -> list[nbf.NotebookNode]:
    cells = header(
        solution=solution,
        week="Week 7",
        title="時間序列診斷",
        objectives=[
            "比較價格序列與報酬序列的統計行為。",
            "計算並解讀自相關函數 (ACF)。",
            "計算 rolling 波動度並觀察波動度叢聚。",
            "比較定態（AR(1)）與非定態（隨機漫步）序列。",
        ],
        hours="8–10 小時",
        prereqs=["Week 1 的報酬", "Week 3 的隨機變數"],
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
            "## 概念說明\n\n"
            "### 定態性 (stationarity)\n\n"
            "**定態**序列的統計性質（平均、變異數、自相關）不隨時間改變。"
            "價格序列通常**非定態**（有趨勢、會漂移）；報酬序列通常**較接近定態**。\n\n"
            "### 自相關函數 (ACF)\n\n"
            "ACF 衡量序列與自身落後值的相關性：\n\n"
            "$$ \\rho_k = \\frac{\\operatorname{Cov}(x_t, x_{t-k})}"
            "{\\operatorname{Var}(x_t)}. $$\n\n"
            "**白噪音**在所有非零落後的 ACF 都接近 0。\n\n"
            "### 為什麼隨機切分不適用\n\n"
            "時間序列有順序。隨機 train/test 切分會讓模型「看到未來」，"
            "造成 look-ahead bias——這是 Week 8 的核心主題。"
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
        md("### 價格 vs 報酬序列"),
        code(
            "fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)\n"
            "axes[0].plot(prices.index, prices.values)\n"
            "axes[0].set_title('價格序列（通常非定態：有趨勢）')\n"
            "axes[0].set_ylabel('價格')\n"
            "axes[1].plot(returns.index, returns.values)\n"
            "axes[1].set_title('報酬序列（較接近定態，但有波動度叢聚）')\n"
            "axes[1].set_xlabel('日期')\n"
            "axes[1].set_ylabel('每日報酬')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        md("### ADF 定態性檢定"),
        code(
            "price_adf = adf_stationarity_test(prices)\n"
            "return_adf = adf_stationarity_test(returns)\n"
            "print('價格序列 ADF p-value :', round(price_adf['p_value'], 4))\n"
            "print('報酬序列 ADF p-value :', round(return_adf['p_value'], 4))\n"
            "print('小 p-value = 有證據反對單根（傾向定態）。')"
        ),
        md("### 自相關函數"),
        code(
            "acf_returns = autocorrelation_function(returns, max_lag=20)\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.bar(acf_returns.index, acf_returns.values)\n"
            "ax.set_title('報酬序列的自相關函數 (ACF)')\n"
            "ax.set_xlabel('落後期數 lag')\n"
            "ax.set_ylabel('自相關')\n"
            "plt.show()\n"
            "print('報酬的 ACF 在非零 lag 多半接近 0 — 接近白噪音。')"
        ),
        md("### Rolling 波動度與波動度叢聚"),
        code(
            "roll_vol = rolling_volatility(returns, window=40)\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(roll_vol.index, roll_vol.values, label='40 期 rolling 波動度')\n"
            "ax.set_title('Rolling 波動度：波動度叢聚')\n"
            "ax.set_xlabel('日期')\n"
            "ax.set_ylabel('rolling 標準差')\n"
            "ax.legend()\n"
            "plt.show()\n"
            "print('合成資料在後半段加入了波動度 regime shift，這裡清楚可見。')"
        ),
        md("### 定態 vs 非定態：AR(1) vs 隨機漫步"),
        code(
            "ar1 = generate_ar1_series(600, phi=0.6, seed=5)\n"
            "walk = generate_random_walk(600, drift=0.0, seed=5)\n"
            "\n"
            "fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)\n"
            "axes[0].plot(ar1.index, ar1.values)\n"
            "axes[0].set_title('AR(1), phi=0.6（定態：會回到平均）')\n"
            "axes[0].set_ylabel('數值')\n"
            "axes[1].plot(walk.index, walk.values)\n"
            "axes[1].set_title('隨機漫步（非定態：會漂移、不回頭）')\n"
            "axes[1].set_xlabel('日期')\n"
            "axes[1].set_ylabel('數值')\n"
            "plt.tight_layout()\n"
            "plt.show()\n"
            "print('AR(1)  ADF p-value:', round(adf_stationarity_test(ar1)['p_value'], 4))\n"
            "print('隨機漫步 ADF p-value:', round(adf_stationarity_test(walk)['p_value'], 4))"
        ),
        exercises_intro(),
        md(
            "### 基礎練習\n\n"
            "1. 用自己的話定義定態性，並說明為何價格通常非定態。\n"
            "2. 白噪音的 ACF 長什麼樣子？\n"
            "3. 解釋什麼是波動度叢聚。"
        ),
        md("### 應用練習"),
        ex_code(
            solution,
            prompt=(
                "# 應用練習 1：產生 phi=0.0、phi=0.5、phi=0.9 三種 AR(1)，\n"
                "# 計算各自 lag-1 的自相關，確認它接近 phi。"
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
            prompt=("# 應用練習 2：對價格序列與報酬序列各畫 ACF，比較兩者的差異。"),
            starter=(
                "acf_price = None  # TODO: autocorrelation_function(prices, max_lag=20)\n"
                "if acf_price is not None:\n"
                "    print('價格 lag-1 自相關:', round(acf_price.iloc[1], 4))\n"
                "    print('報酬 lag-1 自相關:', round(acf_returns.iloc[1], 4))"
            ),
            answer=(
                "acf_price = autocorrelation_function(prices, max_lag=20)\n"
                "print('價格 lag-1 自相關:', round(acf_price.iloc[1], 4))\n"
                "print('報酬 lag-1 自相關:', round(acf_returns.iloc[1], 4))\n"
                "print('價格高度自相關（非定態）；報酬接近白噪音。')"
            ),
        ),
        md(
            "### 反思問題\n\n"
            "1. 既然報酬序列的 ACF 幾乎都接近 0，這對「用過去報酬預測未來報酬」"
            "的策略有什麼啟示？"
        ),
        *quiz_cells(
            solution,
            week=7,
            items=[
                (
                    "定態（stationary）序列的特徵是？",
                    [
                        "價格永遠上漲",
                        "統計性質（平均、變異數、自相關）不隨時間改變",
                        "完全沒有波動",
                        "沒有任何自相關",
                    ],
                    "B",
                    "定態是統計性質的時不變性；序列本身仍可以隨機波動。",
                ),
                (
                    "白噪音的 ACF 在非零 lag 應該？",
                    ["接近 0", "接近 1", "隨 lag 遞增", "全部為負"],
                    "A",
                    "白噪音定義上各期不相關，理論 ACF 除 lag 0 外皆為 0。",
                ),
                (
                    "AR(1)：x_t = φx_{t−1} + ε_t 平穩的條件是？",
                    ["φ > 0", "|φ| < 1", "φ = 1", "φ > 1"],
                    "B",
                    "|φ|<1 時衝擊會衰減；φ=1 就是隨機漫步（非定態）。",
                ),
                (
                    "「波動度叢聚」指的是？",
                    [
                        "報酬集中在平均值附近",
                        "高波動期與低波動期各自成群出現",
                        "價格聚集在整數關卡",
                        "自相關為零",
                    ],
                    "B",
                    "報酬本身近乎無自相關，但報酬的「大小」高度自相關——風暴連著風暴。",
                ),
            ],
        ),
        mistakes(
            [
                "直接對非定態的價格序列建模，而不先轉成報酬。",
                "對時間序列用隨機 train/test 切分。",
                "rolling 計算時把前面視窗不足的 NaN 用未來值回填。",
                "把報酬微弱的自相關過度解讀成可獲利訊號。",
            ]
        ),
        checklist(
            [
                "能解釋定態性並判斷價格 vs 報酬。",
                "能計算並解讀 ACF。",
                "能計算 rolling 波動度並辨識波動度叢聚。",
                "能說明隨機切分為何不適用於時間序列。",
            ]
        ),
        footer_references(solution),
    ]
    return cells
