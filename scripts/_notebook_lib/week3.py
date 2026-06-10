"""Builder for the Week 3 notebook (auto-extracted from build_notebooks.py).

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
        week="Week 3",
        title="機率複習：模擬、LLN 與 CLT",
        objectives=[
            "模擬常見分布並由樣本估計動差。",
            "用模擬視覺化大數法則 (LLN)。",
            "用模擬視覺化中央極限定理 (CLT)。",
            "把抽樣不確定性連結到「估計平均策略報酬」。",
        ],
        hours="7–9 小時",
        prereqs=["隨機變數、期望值與變異數", "基本 numpy"],
        resources=[
            (
                "MIT OpenCourseWare 18.05 Introduction to Probability and Statistics",
                "https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/",
            ),
        ],
    )
    cells += [
        md(
            "## 概念說明\n\n"
            "### 大數法則 (Law of Large Numbers, LLN)\n\n"
            "當樣本數 $n$ 增加，樣本平均 $\\bar X_n$ 會收斂到真實期望值 $\\mu$：\n\n"
            "$$ \\bar X_n = \\frac1n\\sum_{i=1}^n X_i \\xrightarrow[n\\to\\infty]{} \\mu. $$\n\n"
            "### 中央極限定理 (Central Limit Theorem, CLT)\n\n"
            "不論母體分布形狀如何，樣本平均的**抽樣分布**會趨近常態：\n\n"
            "$$ \\frac{\\bar X_n - \\mu}{\\sigma/\\sqrt n} \\xrightarrow{d} N(0, 1). $$\n\n"
            "LLN 告訴我們平均**會收斂到哪**；CLT 告訴我們在有限 $n$ 下平均的"
            "**不確定性有多大**（標準誤 $\\sigma/\\sqrt n$）。"
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
            "### 模擬分布並估計動差\n\n"
            "下面先模擬一個常態分布（連續），再模擬一個 Bernoulli 分布（離散：成敗）。"
            "在策略研究裡 Bernoulli 自然對應「方向是否猜對」這類二元事件。"
        ),
        code(
            "# Bernoulli(p=0.55)：例如「明天上漲」的指示變數，p 是條件機率\n"
            "wins = simulate_bernoulli(p=0.55, size=10_000, seed=0)\n"
            "print('Bernoulli 樣本平均（≈ p）:', round(float(wins.mean()), 3))\n"
            "print('Bernoulli 變異數理論值 p(1-p) =', round(0.55 * 0.45, 4))\n"
            "print('Bernoulli 樣本變異數         =', round(float(wins.var(ddof=1)), 4))"
        ),
        code(
            "normal_draws = simulate_normal(mean=0.001, std=0.02, size=10_000, seed=1)\n"
            "moments = empirical_moments(normal_draws)\n"
            "print('估計動差:', {k: round(v, 6) for k, v in moments.items()})\n"
            "print('真實 mean = 0.001, 真實 std = 0.02')"
        ),
        md("### 視覺化 LLN：樣本平均的收斂"),
        code(
            "samples = simulate_normal(mean=0.05, std=1.0, size=20_000, seed=3)\n"
            "path = running_mean(samples)\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(range(1, len(path) + 1), path, label='累積樣本平均')\n"
            "ax.axhline(0.05, linestyle='--', label='真實期望值 = 0.05')\n"
            "ax.set_title('大數法則：樣本平均隨樣本數收斂')\n"
            "ax.set_xlabel('樣本數 n')\n"
            "ax.set_ylabel('累積平均')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md(
            "曲線一開始劇烈震盪，隨 $n$ 增加逐漸穩定到真實期望值。"
            "**前段的震盪正是抽樣不確定性**——這也是為什麼短期回測的平均報酬不可盡信。"
        ),
        md("### 視覺化 CLT：樣本平均的抽樣分布"),
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
            "axes[0].set_title('樣本數 n=5 的樣本平均分布')\n"
            "axes[0].set_xlabel('樣本平均')\n"
            "axes[0].set_ylabel('次數')\n"
            "axes[1].hist(large, bins=40)\n"
            "axes[1].set_title('樣本數 n=200 的樣本平均分布')\n"
            "axes[1].set_xlabel('樣本平均')\n"
            "axes[1].set_ylabel('次數')\n"
            "plt.tight_layout()\n"
            "plt.show()\n"
            "print('n=5 標準差:', round(float(np.std(small)), 4))\n"
            "print('n=200 標準差:', round(float(np.std(large)), 4))"
        ),
        md(
            "母體是**指數分布**（高度右偏），但樣本平均的分布隨 $n$ 增加越來越像"
            "常態，且越來越集中（標準誤縮小）。這就是 CLT。"
        ),
        md(
            "### 連結到策略報酬\n\n"
            "把「一檔策略每天的報酬」想成隨機變數。我們真正想知道的是它的"
            "**真實期望報酬 $\\mu$**，但只能用有限樣本的樣本平均去估計。"
            "CLT 告訴我們：樣本平均的不確定性是 $\\sigma/\\sqrt n$——"
            "報酬波動越大、資料越少，這個估計就越不可靠。"
        ),
        code(
            "# 一檔「真實期望報酬為 0」的策略，只是運氣好\n"
            "strategy = simulate_normal(mean=0.0, std=0.01, size=252, seed=99)\n"
            "mean_est = strategy.mean()\n"
            "se = strategy.std(ddof=1) / np.sqrt(len(strategy))\n"
            "print(f'一年資料的樣本平均日報酬 = {mean_est:.6f}')\n"
            "print(f'標準誤 = {se:.6f}')\n"
            "print('樣本平均看起來不為 0，但這完全可能只是抽樣雜訊。')"
        ),
        exercises_intro(),
        md(
            "### 基礎練習\n\n"
            "1. 用自己的話說明 LLN 與 CLT 各自回答了什麼問題。\n"
            "2. 標準誤 $\\sigma/\\sqrt n$ 中，要讓標準誤減半需要多少倍的樣本？\n"
            "3. 為什麼母體不是常態，樣本平均仍可能接近常態？"
        ),
        md("### 應用練習"),
        ex_code(
            solution,
            prompt=(
                "# 應用練習 1：模擬 50000 次擲一枚公正硬幣，計算正面比例的累積平均，\n"
                "# 並確認它收斂到 0.5。"
            ),
            starter=(
                "flips = rng.integers(0, 2, size=50_000).astype(float)\n"
                "coin_path = None  # TODO: running_mean(flips)\n"
                "if coin_path is not None:\n"
                "    print('最終累積比例:', round(float(coin_path[-1]), 4))"
            ),
            answer=(
                "flips = rng.integers(0, 2, size=50_000).astype(float)\n"
                "coin_path = running_mean(flips)\n"
                "print('最終累積比例:', round(float(coin_path[-1]), 4))\n"
                "assert abs(coin_path[-1] - 0.5) < 0.02"
            ),
        ),
        ex_code(
            solution,
            prompt=(
                "# 應用練習 2：對 sample_size = 2, 10, 50, 250 各做 4000 次實驗，\n"
                "# 印出樣本平均的標準差，觀察它如何隨 n 縮小。"
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
            "### 反思問題\n\n"
            "1. 若有人給你一檔「過去一年平均日報酬為正」的策略，根據本週的內容，"
            "你會用哪些理由質疑「這代表它真的有正期望報酬」？"
        ),
        *quiz_cells(
            solution,
            week=3,
            items=[
                (
                    "大數法則（LLN）描述的是？",
                    [
                        "樣本平均收斂到母體期望值",
                        "樣本平均服從常態分布",
                        "變異數會消失",
                        "所有分布終將變成常態",
                    ],
                    "A",
                    "LLN 說「收斂到哪」；分布形狀是 CLT 的事。",
                ),
                (
                    "中央極限定理（CLT）描述的是？",
                    [
                        "樣本平均收斂到期望值",
                        "標準化後的樣本平均趨近常態分布",
                        "樣本必須很大才能計算平均",
                        "母體必須是常態",
                    ],
                    "B",
                    "不論母體形狀，樣本平均經標準化後趨近 N(0,1)——不確定性的量化基礎。",
                ),
                (
                    "要把標準誤 σ/√n 減半，樣本數需要變為原來的？",
                    ["2 倍", "4 倍", "√2 倍", "8 倍"],
                    "B",
                    "標準誤與 √n 成反比，減半需要 n 變 4 倍——精度的代價是平方級的。",
                ),
                (
                    "Bernoulli(p) 的變異數是？",
                    ["p", "p²", "p(1−p)", "1−p"],
                    "C",
                    "E[X]=p、E[X²]=p，所以 Var = p − p² = p(1−p)，在 p=0.5 時最大。",
                ),
            ],
        ),
        mistakes(
            [
                "把 LLN（收斂到哪）和 CLT（不確定性多大）混為一談。",
                "忘記設定隨機種子，導致模擬結果無法重現。",
                "用很小的樣本估計平均，卻當作精確的真值。",
                "看到樣本平均為正就認定期望值為正。",
            ]
        ),
        checklist(
            [
                "能用模擬區分並解釋 LLN 與 CLT。",
                "能計算並解讀樣本平均的標準誤。",
                "能說明為什麼短期策略報酬的平均不可盡信。",
            ]
        ),
        footer_references(solution),
    ]
    return cells
