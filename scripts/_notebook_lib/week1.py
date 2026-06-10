"""Builder for the Week 1 notebook (auto-extracted from build_notebooks.py).

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
        week="Week 1",
        title="報酬、風險與線性代數",
        objectives=[
            "正確計算 simple return、log return 與累積報酬。",
            "計算年化平均、年化波動度、共變異數與相關矩陣。",
            "用 quadratic form $w^\\top\\Sigma w$ 計算投資組合變異數。",
            "理解特徵值、特徵向量與 positive semidefinite (PSD)。",
        ],
        hours="8–10 小時",
        prereqs=["向量與矩陣運算", "平均與變異數的定義"],
        resources=[
            (
                "MIT OpenCourseWare 18.06SC Linear Algebra",
                "https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/",
            ),
            (
                "NTU OpenCourseWare 基礎財金素養",
                "https://ocw.aca.ntu.edu.tw/courses/110S204",
            ),
        ],
    )
    cells += [
        md(
            "## 概念說明\n\n"
            "### 報酬\n\n"
            "給定價格 $P_t$，**simple return** 與 **log return** 定義為：\n\n"
            "$$ r_t = \\frac{P_t - P_{t-1}}{P_{t-1}}, \\qquad "
            "\\ell_t = \\ln\\!\\left(\\frac{P_t}{P_{t-1}}\\right). $$\n\n"
            "log return 是**時間可加**的：多期 log return 等於各期之和。\n\n"
            "### 投資組合變異數\n\n"
            "設權重向量 $w$、共變異數矩陣 $\\Sigma$，投資組合變異數為 quadratic form：\n\n"
            "$$ \\operatorname{Var}(r_p) = w^\\top \\Sigma\\, w. $$\n\n"
            "因為變異數不可能為負，對任意 $w$ 都有 $w^\\top\\Sigma w \\ge 0$，"
            "這正是「$\\Sigma$ 必須是 **positive semidefinite (PSD)**」的意義——"
            "等價於它所有特徵值 $\\ge 0$。"
        ),
        code(
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "from quant_math_roadmap.data import SyntheticConfig, generate_correlated_prices\n"
            "from quant_math_roadmap.finance.returns import simple_returns, log_returns\n"
            "from quant_math_roadmap.finance.metrics import (\n"
            "    annualized_mean, annualized_volatility,\n"
            "    covariance_matrix, correlation_matrix,\n"
            ")\n"
            "from quant_math_roadmap.finance.portfolio import equal_weights, portfolio_variance\n"
            "from quant_math_roadmap.math.linear_algebra import (\n"
            "    eigendecomposition, is_positive_semidefinite,\n"
            ")\n"
            "\n"
            "config = SyntheticConfig(n_assets=4, n_periods=756, seed=11,\n"
            "                         average_correlation=0.4)\n"
            "prices = generate_correlated_prices(config)\n"
            "prices.tail()"
        ),
        md("### 計算報酬並比較 simple vs log"),
        code(
            "simple = simple_returns(prices)\n"
            "log = log_returns(prices)\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(simple.index, simple.iloc[:, 0], label='simple return')\n"
            "ax.plot(log.index, log.iloc[:, 0], label='log return')\n"
            "ax.set_title(f'{prices.columns[0]}：simple vs log return')\n"
            "ax.set_xlabel('日期')\n"
            "ax.set_ylabel('每日報酬')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md(
            "兩者在日報酬尺度上幾乎重疊；差異在報酬較大時才明顯。"
            "log return 的好處是可加性，對後面的迴歸與時間序列模型很方便。"
        ),
        md("### 年化平均與波動度（注意：年化是一個明示的假設）"),
        code(
            "ann_mean = annualized_mean(simple, frequency='daily')\n"
            "ann_vol = annualized_volatility(simple, frequency='daily')\n"
            "summary = ann_mean.to_frame('年化平均').join(ann_vol.to_frame('年化波動度'))\n"
            "summary"
        ),
        md(
            "我們**明示**把 `frequency='daily'`（每年 252 個交易日）傳進去。"
            "若資料其實是週資料卻用 252 年化，波動度會被高估約 $\\sqrt{252/52}\\approx 2.2$ 倍。"
        ),
        md("### 共變異數、相關矩陣與 quadratic form"),
        code(
            "cov = covariance_matrix(simple)\n"
            "corr = correlation_matrix(simple)\n"
            "print('共變異數矩陣:')\n"
            "print(cov.round(6))\n"
            "print('\\n相關矩陣:')\n"
            "print(corr.round(3))"
        ),
        code(
            "weights = equal_weights(prices.shape[1])\n"
            "# 手算 quadratic form w^T Sigma w\n"
            "manual = float(weights @ cov.to_numpy() @ weights)\n"
            "# 用可重用函式\n"
            "via_function = portfolio_variance(weights, cov.to_numpy())\n"
            "print(f'手算投組變異數     = {manual:.8f}')\n"
            "print(f'函式計算投組變異數 = {via_function:.8f}')\n"
            "assert np.isclose(manual, via_function)"
        ),
        md("### 特徵值與 PSD 驗證"),
        code(
            "eigenvalues, eigenvectors = eigendecomposition(cov.to_numpy())\n"
            "print('共變異數矩陣特徵值:', np.round(eigenvalues, 8))\n"
            "print('是否 PSD（所有特徵值 >= 0）:', is_positive_semidefinite(cov.to_numpy()))\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(7, 4))\n"
            "ax.bar(range(1, len(eigenvalues) + 1), eigenvalues)\n"
            "ax.set_title('共變異數矩陣的特徵值')\n"
            "ax.set_xlabel('特徵值索引')\n"
            "ax.set_ylabel('特徵值')\n"
            "plt.show()"
        ),
        md(
            "所有特徵值都 $\\ge 0$，因此共變異數矩陣是 PSD。最大的特徵值對應的"
            "特徵向量，常被解讀為資產間最主要的共同變動方向（與 PCA 相關）。"
        ),
        md(
            "### 若估計矩陣不是 PSD 怎麼辦？\n\n"
            "有時雜訊或浮點誤差會讓共變異數估計出現極小的負特徵值。"
            "`nearest_psd()` 會把負特徵值截斷到 0（或某個下界 epsilon），"
            "投影到最近的 PSD 矩陣。這是教學級的修補，不是 shrinkage 的替代方案。"
        ),
        code(
            "from quant_math_roadmap.math.linear_algebra import nearest_psd\n"
            "\n"
            "# 故意把一個小的負特徵值灌進共變異數矩陣\n"
            "noisy = cov.to_numpy().copy()\n"
            "noisy[0, 0] -= 2 * eigenvalues.max()  # 強迫產生負特徵值\n"
            "print('修補前最小特徵值:', round(float(np.linalg.eigvalsh(noisy).min()), 6))\n"
            "repaired = nearest_psd(noisy, epsilon=1e-8)\n"
            "print('修補後最小特徵值:', round(float(np.linalg.eigvalsh(repaired).min()), 8))"
        ),
        exercises_intro(),
        md(
            "### 基礎練習\n\n"
            "1. 用文字說明為什麼 log return 可加、而 simple return 不可加。\n"
            "2. 解釋若某個共變異數矩陣有一個負的特徵值，會代表什麼不合理的情況。\n"
            "3. 為什麼相關矩陣的對角線一定是 1？"
        ),
        md("### 應用練習"),
        ex_code(
            solution,
            prompt=(
                "# 應用練習 1：不要用 pct_change，從頭用 numpy 實作 simple return，\n"
                "# 並與 simple_returns() 的結果比對。"
            ),
            starter=(
                "p = prices.iloc[:, 0].to_numpy()\n"
                "my_simple = None  # TODO: (p[1:] - p[:-1]) / p[:-1]\n"
                "if my_simple is not None:\n"
                "    print('最大誤差:', np.max(np.abs(my_simple - simple.iloc[:, 0].to_numpy())))"
            ),
            answer=(
                "p = prices.iloc[:, 0].to_numpy()\n"
                "my_simple = (p[1:] - p[:-1]) / p[:-1]\n"
                "print('最大誤差:', np.max(np.abs(my_simple - simple.iloc[:, 0].to_numpy())))"
            ),
        ),
        ex_code(
            solution,
            prompt=(
                "# 應用練習 2：比較 equal-weight 投組變異數 與「只買波動度最低資產」的變異數。\n"
                "# 哪一個比較低？為什麼分散投資通常有幫助？"
            ),
            starter=(
                "eq_var = portfolio_variance(equal_weights(prices.shape[1]), cov.to_numpy())\n"
                "lowest_vol_idx = None  # TODO: int(np.argmin(np.diag(cov.to_numpy())))\n"
                "print('equal-weight 變異數:', eq_var)\n"
                "print('（完成 TODO 後印出單一資產變異數）')"
            ),
            answer=(
                "eq_var = portfolio_variance(equal_weights(prices.shape[1]), cov.to_numpy())\n"
                "lowest_vol_idx = int(np.argmin(np.diag(cov.to_numpy())))\n"
                "single_var = cov.to_numpy()[lowest_vol_idx, lowest_vol_idx]\n"
                "print(f'equal-weight 變異數 = {eq_var:.8f}')\n"
                "print(f'最低波動單一資產變異數 = {single_var:.8f}')\n"
                "print('分散投資利用了資產間 < 1 的相關性來降低整體變異數。')"
            ),
        ),
        md(
            "### 反思問題\n\n"
            "1. 共變異數矩陣是用**歷史**資料估計的。若把它直接用來預測**未來**的"
            "投組風險，可能出什麼問題？這對回測有什麼啟示？"
        ),
        mistakes(
            [
                "忘記報酬序列比價格序列少一個觀測值（第一天沒有報酬）。",
                "年化時沒有明示資料頻率，預設所有資料都是日資料。",
                "對非對稱或非方陣呼叫特徵分解。",
                "用樣本共變異數矩陣時忽略它只是估計值、本身有誤差。",
            ]
        ),
        checklist(
            [
                "能正確計算 simple/log return 並解釋差異。",
                "能計算年化平均與波動度，並說明年化假設。",
                "能用 $w^\\top\\Sigma w$ 計算投組變異數。",
                "能檢查一個矩陣是否為 PSD 並解釋其意義。",
            ]
        ),
        footer_references(solution),
    ]
    return cells
