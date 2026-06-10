"""Builder for the Week 2 notebook (auto-extracted from build_notebooks.py).

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
        week="Week 2",
        title="多變數微積分與最小變異投資組合",
        objectives=[
            "計算 quadratic 目標函數的梯度與 Hessian。",
            "用 Lagrange multiplier 推導等式約束最佳化。",
            "實作並解讀最小變異投資組合。",
            "觀察噪音共變異數估計如何造成權重不穩定。",
        ],
        hours="9–11 小時",
        prereqs=["偏微分與梯度", "Week 1 的共變異數與 quadratic form"],
        resources=[
            (
                "MIT OpenCourseWare 18.02SC Multivariable Calculus",
                "https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/",
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
            "### 梯度與 Hessian\n\n"
            "對 $f(w) = w^\\top\\Sigma w$（$\\Sigma$ 對稱），有\n\n"
            "$$ \\nabla f(w) = 2\\Sigma w, \\qquad \\nabla^2 f(w) = 2\\Sigma. $$\n\n"
            "若 $\\Sigma$ 是 PSD，則 Hessian 是 PSD，$f$ 為**凸函數**——"
            "這保證最小化問題有良好、唯一的解。\n\n"
            "### 最小變異投資組合\n\n"
            "問題為：\n\n"
            "$$ \\min_w\\ w^\\top\\Sigma w \\quad \\text{s.t.}\\quad \\mathbf{1}^\\top w = 1. $$\n\n"
            "用 Lagrangian $L(w,\\lambda) = w^\\top\\Sigma w - \\lambda(\\mathbf{1}^\\top w - 1)$，"
            "對 $w$ 求導並令其為零，可得封閉解\n\n"
            "$$ w^\\* = \\frac{\\Sigma^{-1}\\mathbf{1}}{\\mathbf{1}^\\top\\Sigma^{-1}\\mathbf{1}}. $$"
        ),
        code(
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "from quant_math_roadmap.data import SyntheticConfig, generate_correlated_returns\n"
            "from quant_math_roadmap.finance.metrics import covariance_matrix\n"
            "from quant_math_roadmap.finance.portfolio import (\n"
            "    equal_weights, minimum_variance_portfolio,\n"
            "    portfolio_variance, shrinkage_covariance,\n"
            ")\n"
            "from quant_math_roadmap.math.optimization import (\n"
            "    quadratic_gradient, quadratic_hessian,\n"
            ")\n"
            "\n"
            "config = SyntheticConfig(n_assets=6, n_periods=504, seed=7,\n"
            "                         average_correlation=0.45)\n"
            "returns = generate_correlated_returns(config)\n"
            "cov = covariance_matrix(returns).to_numpy()\n"
            "cov.shape"
        ),
        md("### 數值梯度 vs 解析梯度"),
        code(
            "w0 = equal_weights(6)\n"
            "analytic = quadratic_gradient(cov, w0)\n"
            "\n"
            "# 用有限差分驗證解析梯度\n"
            "eps = 1e-6\n"
            "numeric = np.zeros_like(w0)\n"
            "for i in range(len(w0)):\n"
            "    step = np.zeros_like(w0)\n"
            "    step[i] = eps\n"
            "    f_plus = portfolio_variance(w0 + step, cov)\n"
            "    f_minus = portfolio_variance(w0 - step, cov)\n"
            "    numeric[i] = (f_plus - f_minus) / (2 * eps)\n"
            "\n"
            "print('解析梯度:', np.round(analytic, 6))\n"
            "print('數值梯度:', np.round(numeric, 6))\n"
            "print('最大誤差:', np.max(np.abs(analytic - numeric)))"
        ),
        md("解析梯度 $2\\Sigma w$ 與有限差分高度吻合。Hessian 是常數矩陣 $2\\Sigma$："),
        code(
            "hessian = quadratic_hessian(cov)\n"
            "print('Hessian 是否對稱:', np.allclose(hessian, hessian.T))\n"
            "print('Hessian 最小特徵值:', np.linalg.eigvalsh(hessian).min())\n"
            "print('-> 非負特徵值代表目標函數為凸函數。')"
        ),
        md(
            "### Taylor 二階近似：在某點 *附近* 函數長什麼樣\n\n"
            "對 quadratic 目標而言，Taylor 二階近似在任何展開點都**精確**地"
            "等於原函數（因為函數本身就是 quadratic）。下面以 equal-weight 為展開點，"
            "驗證 $f(w_0) + g^\\top (w-w_0) + \\tfrac12 (w-w_0)^\\top H (w-w_0)$ 與真值一致。"
        ),
        code(
            "from quant_math_roadmap.math.optimization import taylor_quadratic_approximation\n"
            "\n"
            "w0 = equal_weights(6)\n"
            "f0 = portfolio_variance(w0, cov)\n"
            "g0 = quadratic_gradient(cov, w0)\n"
            "H0 = quadratic_hessian(cov)\n"
            "# 取一個方向上的偏移作為待近似點\n"
            "w_far = w0 + np.array([0.1, -0.05, 0.0, -0.05, 0.0, 0.0])\n"
            "approx = taylor_quadratic_approximation(f0, g0, H0, w0, w_far)\n"
            "true = portfolio_variance(w_far, cov)\n"
            "print(f'Taylor 二階近似 = {approx:.10f}')\n"
            "print(f'真值           = {true:.10f}')\n"
            "print('quadratic 函數的 Taylor 二階近似 = 真值（無誤差）。')"
        ),
        md("### 最小變異 vs equal-weight"),
        code(
            "mvp = minimum_variance_portfolio(cov)\n"
            "eq = equal_weights(6)\n"
            "print('最小變異權重:', np.round(mvp, 4), ' 總和=', round(mvp.sum(), 6))\n"
            "print('equal-weight  :', np.round(eq, 4))\n"
            "print()\n"
            "print(f'最小變異投組變異數 = {portfolio_variance(mvp, cov):.8f}')\n"
            "print(f'equal-weight 變異數 = {portfolio_variance(eq, cov):.8f}')"
        ),
        md(
            "在**樣本內**（in-sample），最小變異投組的變異數依定義必然 $\\le$ equal-weight。"
            "但這不保證**樣本外**也較好——下一段就來檢驗。"
        ),
        md("### In-sample vs out-of-sample：噪音造成的不穩定"),
        code(
            "# 用前半段估計權重，後半段檢驗\n"
            "half = len(returns) // 2\n"
            "train, test = returns.iloc[:half], returns.iloc[half:]\n"
            "cov_train = covariance_matrix(train).to_numpy()\n"
            "cov_test = covariance_matrix(test).to_numpy()\n"
            "\n"
            "mvp_train = minimum_variance_portfolio(cov_train)\n"
            "in_sample = portfolio_variance(mvp_train, cov_train)\n"
            "out_sample = portfolio_variance(mvp_train, cov_test)\n"
            "eq_out = portfolio_variance(eq, cov_test)\n"
            "print(f'最小變異  in-sample 變異數 = {in_sample:.8f}')\n"
            "print(f'最小變異 out-of-sample 變異數 = {out_sample:.8f}')\n"
            "print(f'equal-weight out-of-sample 變異數 = {eq_out:.8f}')\n"
            "print('觀察：out-of-sample 通常比 in-sample 差，有時甚至輸給 equal-weight。')"
        ),
        md("### Shrinkage：對抗噪音的共變異數估計"),
        code(
            "weights_by_shrinkage = {}\n"
            "for delta in [0.0, 0.2, 0.5, 0.8]:\n"
            "    cov_shrunk = shrinkage_covariance(train, shrinkage=delta).to_numpy()\n"
            "    w = minimum_variance_portfolio(cov_shrunk)\n"
            "    weights_by_shrinkage[delta] = w\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(8, 4.5))\n"
            "for delta, w in weights_by_shrinkage.items():\n"
            "    ax.plot(range(1, 7), w, marker='o', label=f'shrinkage={delta}')\n"
            "ax.axhline(1 / 6, linestyle='--', label='equal weight')\n"
            "ax.set_title('shrinkage 強度對最小變異權重的影響')\n"
            "ax.set_xlabel('資產索引')\n"
            "ax.set_ylabel('權重')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md(
            "shrinkage 越強，權重越被拉向 equal-weight、越不極端。這以一點偏誤"
            "換取大幅的穩定度，往往改善樣本外表現。"
        ),
        exercises_intro(),
        md(
            "### 基礎練習\n\n"
            "1. 寫出最小變異問題的 Lagrangian，並說明每一項的意義。\n"
            "2. 為什麼「Hessian 為 PSD」能保證問題有良好解？\n"
            "3. 用一句話解釋 shrinkage 是在做什麼取捨。"
        ),
        md("### 應用練習"),
        ex_code(
            solution,
            prompt=(
                "# 應用練習 1：用封閉解公式 w* = (Σ^-1 1)/(1^T Σ^-1 1) 自行計算最小變異權重，\n"
                "# 並與 minimum_variance_portfolio() 比對。"
            ),
            starter=(
                "ones = np.ones(6)\n"
                "my_mvp = None  # TODO: inv = np.linalg.solve(cov, ones); my_mvp = inv / (ones @ inv)\n"
                "if my_mvp is not None:\n"
                "    print('最大誤差:', np.max(np.abs(my_mvp - minimum_variance_portfolio(cov))))"
            ),
            answer=(
                "ones = np.ones(6)\n"
                "inv_dot_ones = np.linalg.solve(cov, ones)\n"
                "my_mvp = inv_dot_ones / (ones @ inv_dot_ones)\n"
                "print('最大誤差:', np.max(np.abs(my_mvp - minimum_variance_portfolio(cov))))"
            ),
        ),
        ex_code(
            solution,
            prompt=(
                "# 應用練習 2：計算 long-only（不可放空）的最小變異投組，\n# 並確認沒有負權重。"
            ),
            starter=(
                "long_only = None  # TODO: minimum_variance_portfolio(cov, long_only=True)\n"
                "if long_only is not None:\n"
                "    print('最小權重:', long_only.min(), '| 總和:', long_only.sum())"
            ),
            answer=(
                "long_only = minimum_variance_portfolio(cov, long_only=True)\n"
                "print('最小權重:', round(long_only.min(), 6), '| 總和:', round(long_only.sum(), 6))\n"
                "assert (long_only >= -1e-9).all()"
            ),
        ),
        md(
            "### 反思問題\n\n"
            "1. 最小變異投組在樣本內一定贏 equal-weight，樣本外卻不一定。"
            "這個現象和 Week 8 的「過度配適 in-sample 期間」有什麼關聯？"
        ),
        mistakes(
            [
                "對噪音很大的共變異數矩陣求逆，得到極端且不穩定的權重。",
                "把 in-sample 的低變異數誤認為樣本外保證。",
                "忘記約束 $\\mathbf{1}^\\top w = 1$，得到沒有意義的權重。",
                "忽略最佳化結果對共變異數估計誤差非常敏感。",
            ]
        ),
        checklist(
            [
                "能寫出並解釋最小變異問題的 Lagrangian。",
                "能用封閉解計算最小變異權重。",
                "能比較 in-sample 與 out-of-sample 變異數。",
                "能說明 shrinkage 如何穩定權重。",
            ]
        ),
        footer_references(solution),
    ]
    return cells
