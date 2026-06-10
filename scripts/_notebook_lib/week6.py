"""Builder for the Week 6 notebook (auto-extracted from build_notebooks.py).

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
        week="Week 6",
        title="財務數學與選擇權定價",
        objectives=[
            "計算折現因子、現值與債券價格。",
            "繪製 call、put 與簡單組合的 payoff 圖。",
            "用 binomial tree 為歐式選擇權定價。",
            "對 strike、波動度、到期、利率做敏感度分析。",
        ],
        hours="8–10 小時",
        prereqs=["基本代數與指數", "Week 1 的報酬概念"],
        resources=[
            (
                "NTU OpenCourseWare 基礎財金素養",
                "https://ocw.aca.ntu.edu.tw/courses/110S204",
            ),
        ],
    )
    cells += [
        md(
            "## 概念說明\n\n"
            "### 貨幣的時間價值\n\n"
            "未來的現金流要先**折現**才能和今天的錢比較。年利率 $r$、$t$ 年後、"
            "每年複利 $m$ 次的折現因子為 $(1 + r/m)^{-mt}$。現值是各期現金流"
            "乘上折現因子後的總和。\n\n"
            "### 選擇權 payoff 與 binomial 定價\n\n"
            "歐式 call/put 到期 payoff 為 $\\max(S-K,0)$、$\\max(K-S,0)$。\n\n"
            "本路線圖**刻意只用 binomial tree**：它只需要算術與 no-arbitrage 概念，"
            "**不需要** stochastic calculus，也**不要求** Black-Scholes 推導。"
            "選擇權價值是其到期 payoff 在 risk-neutral 機率下的折現期望值。\n\n"
            "> 提醒：模型價格**不應**被解讀為對真實市場價格的預測。"
        ),
        code(
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "from quant_math_roadmap.finance.fixed_income import (\n"
            "    bond_price, discount_factor, present_value, zero_coupon_bond_price,\n"
            ")\n"
            "from quant_math_roadmap.finance.derivatives import (\n"
            "    binomial_european_option, call_payoff, put_payoff,\n"
            "    long_straddle_payoff, put_call_parity_gap,\n"
            ")"
        ),
        md("### 現值計算器"),
        code(
            "rate = 0.04\n"
            "cash_flows = [100, 100, 100, 1100]  # 4 年期、年付息\n"
            "times = [1, 2, 3, 4]\n"
            "pv = present_value(cash_flows, times, rate)\n"
            "print(f'折現率 {rate:.0%} 下，現金流現值 = {pv:.2f}')\n"
            "for t in times:\n"
            "    print(f'  t={t}: 折現因子 = {discount_factor(rate, t):.4f}')"
        ),
        md("### 債券定價：價格隨殖利率下降"),
        code(
            "yields = np.linspace(0.01, 0.10, 50)\n"
            "prices = [bond_price(1000, 0.05, 10, y, coupons_per_year=2) for y in yields]\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(8, 4.5))\n"
            "ax.plot(yields, prices, label='10 年期、5% 票息債券')\n"
            "ax.axhline(1000, linestyle='--', label='面額 = 1000')\n"
            "ax.set_title('債券價格 vs 殖利率')\n"
            "ax.set_xlabel('殖利率 (yield to maturity)')\n"
            "ax.set_ylabel('債券價格')\n"
            "ax.legend()\n"
            "plt.show()\n"
            "zcb = zero_coupon_bond_price(1000, 10, 0.05)\n"
            "print(f'10 年期零息債券（殖利率 5%）價格 = {zcb:.2f}')"
        ),
        md("殖利率上升，債券價格下降；票息率等於殖利率時，債券以面額（par）定價。"),
        md("### Payoff 圖"),
        code(
            "spot_grid = np.linspace(50, 150, 200)\n"
            "strike = 100.0\n"
            "fig, axes = plt.subplots(1, 3, figsize=(13, 4))\n"
            "axes[0].plot(spot_grid, call_payoff(spot_grid, strike))\n"
            "axes[0].set_title('Call payoff (K=100)')\n"
            "axes[1].plot(spot_grid, put_payoff(spot_grid, strike))\n"
            "axes[1].set_title('Put payoff (K=100)')\n"
            "axes[2].plot(spot_grid, long_straddle_payoff(spot_grid, strike))\n"
            "axes[2].set_title('Long straddle payoff (K=100)')\n"
            "for ax in axes:\n"
            "    ax.set_xlabel('到期標的價格 S')\n"
            "    ax.set_ylabel('payoff')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        md("### Binomial 歐式選擇權定價"),
        code(
            "params = {'spot': 100.0, 'strike': 100.0, 'rate': 0.05,\n"
            "          'volatility': 0.20, 'maturity': 1.0}\n"
            "call = binomial_european_option(**params, n_steps=300, option_type='call')\n"
            "put = binomial_european_option(**params, n_steps=300, option_type='put')\n"
            "print(f'歐式 call 價格 = {call:.4f}')\n"
            "print(f'歐式 put  價格 = {put:.4f}')\n"
            "gap = put_call_parity_gap(call, put, params['spot'], params['strike'],\n"
            "                          params['rate'], params['maturity'])\n"
            "print(f'put-call parity 殘差 = {gap:.6f}  (應接近 0)')"
        ),
        md("### 敏感度分析"),
        code(
            "vols = np.linspace(0.05, 0.6, 40)\n"
            "call_by_vol = [binomial_european_option(100, 100, 0.05, v, 1.0,\n"
            "               n_steps=200) for v in vols]\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(8, 4.5))\n"
            "ax.plot(vols, call_by_vol, label='ATM call (S=K=100)')\n"
            "ax.set_title('歐式 call 價格 vs 波動度')\n"
            "ax.set_xlabel('波動度代理值 sigma')\n"
            "ax.set_ylabel('call 價格')\n"
            "ax.legend()\n"
            "plt.show()\n"
            "print('波動度越高，選擇權越貴 — 因為更大的不確定性對買方有利。')"
        ),
        exercises_intro(),
        md(
            "### 基礎練習\n\n"
            "1. 用一句話解釋為什麼未來的錢要折現。\n"
            "2. 為什麼債券價格與殖利率反向變動？\n"
            "3. 解釋 long straddle 的 payoff 形狀，以及它在押注什麼。"
        ),
        md("### 應用練習"),
        ex_code(
            solution,
            prompt=(
                "# 應用練習 1：計算 binomial call 價格隨 strike 變化的曲線（其他參數固定），\n"
                "# 並確認 strike 越高、call 越便宜。"
            ),
            starter=(
                "strikes = np.linspace(80, 120, 20)\n"
                "call_by_strike = None  # TODO: [binomial_european_option(100, k, 0.05, 0.2, 1.0, n_steps=150) for k in strikes]\n"
                "if call_by_strike is not None:\n"
                "    print('遞減?', all(np.diff(call_by_strike) < 0))"
            ),
            answer=(
                "strikes = np.linspace(80, 120, 20)\n"
                "call_by_strike = [binomial_european_option(100, k, 0.05, 0.2, 1.0,\n"
                "                  n_steps=150) for k in strikes]\n"
                "print('strike 越高 call 越便宜?', all(np.diff(call_by_strike) < 0))"
            ),
        ),
        ex_code(
            solution,
            prompt=("# 應用練習 2：驗證 binomial 步數增加時 call 價格收斂（穩定下來）。"),
            starter=(
                "for steps in [10, 50, 200, 800]:\n"
                "    price = None  # TODO: binomial_european_option(100, 100, 0.05, 0.2, 1.0, n_steps=steps)\n"
                "    print(steps, price)"
            ),
            answer=(
                "for steps in [10, 50, 200, 800]:\n"
                "    price = binomial_european_option(100, 100, 0.05, 0.2, 1.0,\n"
                "                                     n_steps=steps)\n"
                "    print(f'n_steps={steps:>3}: call = {price:.4f}')\n"
                "print('步數越多，價格越穩定（收斂）。')"
            ),
        ),
        md(
            "### 反思問題\n\n"
            "1. binomial 模型價格與真實市場價格幾乎不會完全相同。"
            "這對「用模型價格設計交易策略」有什麼提醒？"
        ),
        mistakes(
            [
                "折現時搞錯複利頻率（年複利 vs 半年複利）。",
                "把選擇權 payoff（到期才實現）與選擇權現價混為一談。",
                "binomial 步數太少就把價格當精確值。",
                "宣稱模型價格等於真實市場價格。",
            ]
        ),
        checklist(
            [
                "能計算現值與債券價格。",
                "能繪製並解讀 call/put/straddle 的 payoff 圖。",
                "能用 binomial tree 為歐式選擇權定價並解釋每一步。",
                "能對主要參數做敏感度分析。",
            ]
        ),
        footer_references(solution),
    ]
    return cells
