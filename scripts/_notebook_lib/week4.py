"""Builder for the Week 4 notebook (auto-extracted from build_notebooks.py).

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
)


def week(solution: bool) -> list[nbf.NotebookNode]:
    cells = header(
        solution=solution,
        week="Week 4",
        title="策略報酬的統計推論",
        objectives=[
            "估計平均報酬的標準誤與信賴區間。",
            "用 bootstrap 建立平均報酬的信賴區間。",
            "理解 p-value 的意義與常見誤用。",
            "示範「測試大量隨機策略」如何製造假陽性。",
        ],
        hours="9–11 小時",
        prereqs=["Week 3 的抽樣不確定性", "平均、標準差"],
        resources=[
            (
                "MIT OpenCourseWare 18.05 Introduction to Probability and Statistics",
                "https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/",
            ),
            (
                "NTU OpenCourseWare 統計學一上與計量導論",
                "https://ocw.aca.ntu.edu.tw/courses/112S103",
            ),
        ],
    )
    cells += [
        md(
            "## 概念說明\n\n"
            "### 估計量、標準誤與信賴區間\n\n"
            "**估計量**是資料的函數（例如樣本平均）。它有 **bias**（系統性偏差）"
            "與 **variance**（隨樣本變動）。樣本平均的**標準誤**為 $s/\\sqrt n$。\n\n"
            "**信賴區間**給出「與資料相容的參數範圍」。95% 信賴區間的正確解讀是："
            "若重複抽樣很多次，約 95% 的區間會涵蓋真實參數。\n\n"
            "### p-value 與其誤用\n\n"
            "p-value 是「**若虛無假設為真**，看到目前或更極端結果的機率」。它**不是**"
            "「策略有效的機率」。最危險的誤用是 **multiple testing**：測試夠多隨機"
            "策略，總會有幾個僅憑運氣就「顯著」。"
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
        md("### 平均報酬的標準誤與信賴區間"),
        code(
            "returns = simulate_normal(mean=0.0004, std=0.012, size=252, seed=42)\n"
            "se = standard_error_of_mean(returns)\n"
            "lower, upper = confidence_interval_mean(returns, confidence=0.95)\n"
            "print(f'樣本平均日報酬 = {returns.mean():.6f}')\n"
            "print(f'標準誤 = {se:.6f}')\n"
            "print(f'95% 信賴區間 = [{lower:.6f}, {upper:.6f}]')\n"
            "print('注意：信賴區間很可能涵蓋 0 — 我們無法排除「真實期望為 0」。')"
        ),
        md("### Bootstrap 信賴區間"),
        code(
            "boot_lower, boot_upper = bootstrap_mean_ci(\n"
            "    returns, confidence=0.95, n_resamples=5000, seed=0)\n"
            "print(f'bootstrap 95% 信賴區間 = [{boot_lower:.6f}, {boot_upper:.6f}]')\n"
            "print(f't 分布   95% 信賴區間 = [{lower:.6f}, {upper:.6f}]')\n"
            "print('兩種方法給出相近的區間；bootstrap 不需要常態假設。')"
        ),
        md("### 比較兩個合成策略"),
        code(
            "strategy_a = simulate_normal(mean=0.0002, std=0.010, size=252, seed=1)\n"
            "strategy_b = simulate_normal(mean=0.0007, std=0.018, size=252, seed=2)\n"
            "for name, s in [('策略 A', strategy_a), ('策略 B', strategy_b)]:\n"
            "    t = one_sample_ttest(s, popmean=0.0)\n"
            "    ci = confidence_interval_mean(s)\n"
            "    print(f'{name}: 平均={s.mean():.6f}, p-value={t.p_value:.3f}, '\n"
            "          f'95% CI=[{ci[0]:.6f}, {ci[1]:.6f}]')"
        ),
        md(
            "即使某個策略的樣本平均較高，其 p-value 仍可能不顯著、信賴區間仍涵蓋 0。"
            "**較高的歷史平均報酬不等於較高的真實期望報酬。**"
        ),
        md(
            "### 多重檢定：假陽性的製造機\n\n"
            "下面產生大量**純雜訊**策略（真實期望報酬皆為 0），看看有多少會在"
            "$\\alpha=0.05$ 下被誤判為「顯著」。"
        ),
        code(
            "demo = false_discovery_demo(n_strategies=500, n_periods=252,\n"
            "                            alpha=0.05, seed=0)\n"
            "for k, v in demo.items():\n"
            "    print(f'{k}: {v}')\n"
            "print()\n"
            "print('全部 500 檔策略都是純雜訊，所有「顯著」結果都是假陽性。')"
        ),
        code(
            "# 視覺化：最佳雜訊策略的權益曲線看起來也可能很漂亮\n"
            "rng = np.random.default_rng(0)\n"
            "noise = rng.standard_normal((500, 252)) * 0.01\n"
            "totals = (1 + noise).prod(axis=1) - 1\n"
            "best = noise[int(np.argmax(totals))]\n"
            "equity = (1 + pd.Series(best)).cumprod()\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(equity.index, equity.values, label='500 檔雜訊策略中「最好」的一檔')\n"
            "ax.axhline(1.0, linestyle='--', label='起始資金')\n"
            "ax.set_title('一條漂亮的權益曲線 — 但它純粹是運氣')\n"
            "ax.set_xlabel('交易日')\n"
            "ax.set_ylabel('權益（起始 = 1）')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md(
            "這條曲線完全由雜訊產生，卻可能比真正有訊號的策略還漂亮。"
            "**一條漂亮的權益曲線無法證明策略有效。**"
        ),
        md("### 風險調整指標的警語"),
        code(
            "sr = sharpe_ratio(pd.Series(returns), frequency='daily')\n"
            "print(f'年化 Sharpe ratio = {sr:.3f}')\n"
            "print('警語：Sharpe 是估計值，本身有抽樣誤差；它忽略偏態與厚尾；')\n"
            "print('短樣本下，回測 Sharpe 為 2 也可能與「真實 Sharpe 為 0」相容。')"
        ),
        exercises_intro(),
        md(
            "### 基礎練習\n\n"
            "1. 用一句話寫出 p-value 的正確定義。\n"
            "2. 「95% 信賴區間」正確的解讀是什麼？常見的錯誤解讀又是什麼？\n"
            "3. 為什麼「測試很多策略後挑出最好的一個」會讓 p-value 失去意義？"
        ),
        md("### 應用練習"),
        ex_code(
            solution,
            prompt=("# 應用練習 1：對 strategy_a 做 bootstrap，比較 90% 與 99% 信賴區間的寬度。"),
            starter=(
                "ci90 = None  # TODO: bootstrap_mean_ci(strategy_a, confidence=0.90, seed=0)\n"
                "ci99 = None  # TODO: bootstrap_mean_ci(strategy_a, confidence=0.99, seed=0)\n"
                "if ci90 and ci99:\n"
                "    print('90% 寬度:', ci90[1] - ci90[0])\n"
                "    print('99% 寬度:', ci99[1] - ci99[0])"
            ),
            answer=(
                "ci90 = bootstrap_mean_ci(strategy_a, confidence=0.90, seed=0)\n"
                "ci99 = bootstrap_mean_ci(strategy_a, confidence=0.99, seed=0)\n"
                "print('90% 寬度:', round(ci90[1] - ci90[0], 6))\n"
                "print('99% 寬度:', round(ci99[1] - ci99[0], 6))\n"
                "print('信心水準越高，區間越寬 — 更保守。')"
            ),
        ),
        ex_code(
            solution,
            prompt=(
                "# 應用練習 2：把 false_discovery_demo 的 alpha 改成 0.01，\n"
                "# 觀察假陽性數量如何變化。"
            ),
            starter=(
                "strict = None  # TODO: false_discovery_demo(n_strategies=500, alpha=0.01, seed=0)\n"
                "if strict is not None:\n"
                "    print(strict)"
            ),
            answer=(
                "strict = false_discovery_demo(n_strategies=500, n_periods=252,\n"
                "                              alpha=0.01, seed=0)\n"
                "print('alpha=0.01 假陽性數:', strict['n_false_positives'])\n"
                "print('理論期望:', strict['expected_false_positives'])\n"
                "print('更嚴格的 alpha 減少假陽性，但仍無法完全消除多重檢定問題。')"
            ),
        ),
        md(
            "### 反思問題\n\n"
            "1. 你在大量參數組合中找到一個回測表現很好的策略。在相信它之前，"
            "你應該對「多重檢定」與「樣本外驗證」做哪些事？"
        ),
        mistakes(
            [
                "把 p-value 解讀成「策略有效的機率」。",
                "測試大量策略後只報告最好的，卻不做多重檢定校正。",
                "把統計顯著當成經濟顯著（即使有效也可能被成本吃掉）。",
                "用單一回測 Sharpe ratio 就下結論，忽略它的抽樣誤差。",
            ]
        ),
        checklist(
            [
                "能計算並解讀平均報酬的信賴區間（t 與 bootstrap）。",
                "能正確說明 p-value 的意義。",
                "能示範並解釋多重檢定造成的假陽性。",
                "能說出 Sharpe ratio 的至少三項侷限。",
            ]
        ),
        footer_references(solution),
    ]
    return cells
