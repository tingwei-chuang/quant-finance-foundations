"""Builder for the Week 5 notebook (auto-extracted from build_notebooks.py).

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
        week="Week 5",
        title="迴歸與因子模型",
        objectives=[
            "用矩陣形式推導並實作 OLS。",
            "估計 CAPM 式市場 beta 並解讀。",
            "配適多因子模型並檢視殘差。",
            "計算 rolling beta 並理解 omitted variable bias。",
        ],
        hours="9–11 小時",
        prereqs=["Week 1 的矩陣運算", "Week 4 的標準誤"],
        resources=[
            (
                "NTU OpenCourseWare 統計學一上與計量導論",
                "https://ocw.aca.ntu.edu.tw/courses/112S103",
            ),
            (
                "MIT OpenCourseWare 18.06SC Linear Algebra",
                "https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/",
            ),
        ],
    )
    cells += [
        md(
            "## 概念說明\n\n"
            "### OLS 的矩陣形式\n\n"
            "模型 $y = X\\beta + \\varepsilon$ 的最小平方解為\n\n"
            "$$ \\hat\\beta = (X^\\top X)^{-1} X^\\top y. $$\n\n"
            "幾何上，$X\\hat\\beta$ 是把 $y$ **投影**到 $X$ 各欄所張成的子空間；"
            "殘差 $y - X\\hat\\beta$ 與該子空間正交。\n\n"
            "### 財務意義\n\n"
            "CAPM 式迴歸 $r_{\\text{asset}} = \\alpha + \\beta\\, r_{\\text{market}} + \\varepsilon$ 中，"
            "$\\beta$ 衡量資產對市場的曝險。**但要切記：迴歸係數不會自動變成可交易"
            "的訊號**——它只是描述歷史共變關係。"
        ),
        code(
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import statsmodels.api as sm\n"
            "from quant_math_roadmap.math.statistics import ols_fit\n"
            "from quant_math_roadmap.math.linear_algebra import add_intercept, ols_beta\n"
            "\n"
            "rng = np.random.default_rng(2024)\n"
            "n = 600\n"
            "market = rng.normal(0.0003, 0.011, n)\n"
            "true_beta, true_alpha = 1.2, 0.0001\n"
            "idiosyncratic = rng.normal(0.0, 0.008, n)\n"
            "asset = true_alpha + true_beta * market + idiosyncratic\n"
            "print('已產生合成市場與資產報酬，n =', n)"
        ),
        md("### 手刻 OLS vs statsmodels"),
        code(
            "fit = ols_fit(market, asset, add_const=True, feature_names=['market'])\n"
            "print(fit.summary())\n"
            "print()\n"
            "sm_fit = sm.OLS(asset, sm.add_constant(market)).fit()\n"
            "print('statsmodels 係數:', np.round(sm_fit.params, 6))\n"
            "print('我們的係數    :', np.round(fit.params, 6))\n"
            "assert np.allclose(fit.params, sm_fit.params)"
        ),
        md(
            "估計的 beta 應接近真實值 1.2。手刻 OLS 與 `statsmodels` 完全吻合，"
            "印證 $\\hat\\beta = (X^\\top X)^{-1}X^\\top y$。"
        ),
        code(
            "fig, ax = plt.subplots(figsize=(6.5, 5))\n"
            "ax.scatter(market, asset, s=8, alpha=0.4, label='觀測值')\n"
            "grid = np.linspace(market.min(), market.max(), 100)\n"
            "ax.plot(grid, fit.params[0] + fit.params[1] * grid,\n"
            "        label=f'OLS 配適線 (beta={fit.params[1]:.3f})')\n"
            "ax.set_title('CAPM 式迴歸：資產報酬 vs 市場報酬')\n"
            "ax.set_xlabel('市場報酬')\n"
            "ax.set_ylabel('資產報酬')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md("### 多因子模型"),
        code(
            "value_factor = rng.normal(0.0, 0.007, n)\n"
            "size_factor = rng.normal(0.0, 0.006, n)\n"
            "asset_multi = (0.0001 + 1.1 * market + 0.6 * value_factor\n"
            "               - 0.3 * size_factor + rng.normal(0, 0.005, n))\n"
            "X = np.column_stack([market, value_factor, size_factor])\n"
            "multi_fit = ols_fit(X, asset_multi, add_const=True,\n"
            "                    feature_names=['market', 'value', 'size'])\n"
            "print(multi_fit.summary())"
        ),
        md(
            "每個係數是「在其他因子固定下」該因子的曝險。$R^2$ 衡量模型解釋了"
            "多少報酬變異——但高 $R^2$ **不**代表可獲利。"
        ),
        md("### Rolling beta"),
        code(
            "asset_s = pd.Series(asset)\n"
            "market_s = pd.Series(market)\n"
            "window = 120\n"
            "rolling_beta = []\n"
            "for end in range(window, n + 1):\n"
            "    sl = slice(end - window, end)\n"
            "    b = ols_beta(add_intercept(market_s.iloc[sl].to_numpy()),\n"
            "                 asset_s.iloc[sl].to_numpy())\n"
            "    rolling_beta.append(b[1])\n"
            "rolling_beta = pd.Series(rolling_beta, index=range(window, n + 1))\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(rolling_beta.index, rolling_beta.values, label=f'{window} 期 rolling beta')\n"
            "ax.axhline(true_beta, linestyle='--', label=f'真實 beta = {true_beta}')\n"
            "ax.set_title('Rolling beta 隨時間的估計')\n"
            "ax.set_xlabel('視窗結束位置')\n"
            "ax.set_ylabel('估計 beta')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md(
            "即使真實 beta 固定，rolling 估計仍會在其周圍震盪——這就是估計的"
            "抽樣不確定性。真實資料的 beta 還會**真的隨時間改變**。"
        ),
        md(
            "### Heteroskedasticity 與穩健標準誤（HC0 / HC1）\n\n"
            "金融資料常見**異質變異**：誤差的變異數不是常數（例如隨市場波動放大）。"
            "此時 OLS 的**係數估計仍然不偏**，但古典標準誤失準——顯著性檢定會被誤導。"
            "White (1980) 的 **sandwich 估計**只用「實際殘差的平方」重新估計係數的"
            "共變異數，不需要假設誤差結構：\n\n"
            "$$ \\widehat{\\mathrm{Var}}(\\hat\\beta)_{HC0} = (X^\\top X)^{-1}"
            " X^\\top \\mathrm{diag}(e_i^2)\\, X (X^\\top X)^{-1} $$\n\n"
            "下面刻意製造一組誤差變異隨 $|x|$ 放大的資料，比較古典與穩健標準誤。"
        ),
        code(
            "# 誤差標準差 = 0.5 + |x| -> 教科書級的 heteroskedasticity\n"
            "x_het = rng.standard_normal(800)\n"
            "y_het = 1.0 + 2.0 * x_het + rng.standard_normal(800) * (0.5 + np.abs(x_het))\n"
            "\n"
            "classic = ols_fit(x_het, y_het, feature_names=['x'])\n"
            "robust = ols_fit(x_het, y_het, feature_names=['x'], robust='HC1')\n"
            "print('係數完全相同:', np.allclose(classic.params, robust.params))\n"
            "print(f'斜率的古典標準誤   = {classic.std_errors[1]:.4f}')\n"
            "print(f'斜率的 HC1 穩健標準誤 = {robust.std_errors[1]:.4f}')\n"
            "print('異質變異下，古典標準誤明顯低估不確定性 -> t 統計量被高估。')"
        ),
        md(
            "**結論**：報告金融迴歸時，預設使用穩健標準誤是良好習慣。注意它只"
            "修推論（標準誤、t、p-value），不改變係數本身——模型的解釋力沒有變，"
            "變的是你對顯著性的信心。"
        ),
        md("### 殘差檢視與 omitted variable bias"),
        code(
            "fig, ax = plt.subplots(figsize=(9, 4))\n"
            "ax.scatter(range(len(multi_fit.residuals)), multi_fit.residuals, s=8, alpha=0.4)\n"
            "ax.axhline(0.0, linestyle='--')\n"
            "ax.set_title('多因子模型的殘差')\n"
            "ax.set_xlabel('觀測索引')\n"
            "ax.set_ylabel('殘差')\n"
            "plt.show()"
        ),
        code(
            "# 故意遺漏 value 因子，看 beta 如何被扭曲\n"
            "biased = ols_fit(market, asset_multi, add_const=True, feature_names=['market'])\n"
            "full = ols_fit(X, asset_multi, add_const=True,\n"
            "               feature_names=['market', 'value', 'size'])\n"
            "print('遺漏變數時 market 係數:', round(biased.params[1], 4))\n"
            "print('完整模型   market 係數:', round(full.params[1], 4))\n"
            "print('若遺漏變數與納入變數相關，估計係數就會有偏誤。')"
        ),
        exercises_intro(),
        md(
            "### 基礎練習\n\n"
            "1. 用幾何投影的語言解釋 OLS 在做什麼。\n"
            "2. 解釋截距、beta、殘差、$R^2$ 各自代表什麼。\n"
            "3. 為什麼「迴歸係數顯著」不等於「可以拿來交易」？"
        ),
        md("### 應用練習"),
        ex_code(
            solution,
            prompt=(
                "# 應用練習 1：不要用 ols_fit，直接用矩陣公式 (X^T X)^-1 X^T y 估計 beta，\n"
                "# 並與 ols_fit 比對（記得加截距欄）。"
            ),
            starter=(
                "Xc = add_intercept(market)\n"
                "my_beta = None  # TODO: np.linalg.solve(Xc.T @ Xc, Xc.T @ asset)\n"
                "if my_beta is not None:\n"
                "    print('手算 beta:', np.round(my_beta, 6))"
            ),
            answer=(
                "Xc = add_intercept(market)\n"
                "my_beta = np.linalg.solve(Xc.T @ Xc, Xc.T @ asset)\n"
                "print('手算 beta :', np.round(my_beta, 6))\n"
                "print('ols_fit   :', np.round(fit.params, 6))\n"
                "assert np.allclose(my_beta, fit.params)"
            ),
        ),
        ex_code(
            solution,
            prompt=("# 應用練習 2：把 rolling 視窗改成 60 期，觀察 rolling beta 的波動如何變化。"),
            starter=(
                "win = 60\n"
                "betas = []  # TODO: 仿照上面用 win 計算 rolling beta\n"
                "print('完成後比較 60 期與 120 期的波動度。')"
            ),
            answer=(
                "win = 60\n"
                "betas = []\n"
                "for end in range(win, n + 1):\n"
                "    sl = slice(end - win, end)\n"
                "    b = ols_beta(add_intercept(market_s.iloc[sl].to_numpy()),\n"
                "                 asset_s.iloc[sl].to_numpy())\n"
                "    betas.append(b[1])\n"
                "betas = pd.Series(betas)\n"
                "print('60 期 rolling beta 標準差 :', round(betas.std(), 4))\n"
                "print('120 期 rolling beta 標準差:', round(rolling_beta.std(), 4))\n"
                "print('視窗越短，估計越不穩定。')"
            ),
        ),
        md(
            "### 反思問題\n\n"
            "1. 假設你用迴歸發現某因子對下一期報酬「顯著」。在把它變成回測訊號之前，"
            "Week 4（多重檢定）與 Week 8（leakage）各提醒你要注意什麼？"
        ),
        *quiz_cells(
            solution,
            week=5,
            items=[
                (
                    "OLS 的矩陣解 β̂ 是？",
                    ["(XᵀX)⁻¹Xᵀy", "Xᵀy", "X⁻¹y", "(XXᵀ)⁻¹yX"],
                    "A",
                    "由 normal equations XᵀXβ = Xᵀy 解出——Week 5 的核心公式。",
                ),
                (
                    "R² 衡量的是？",
                    ["策略可獲利程度", "模型解釋的應變數變異比例", "係數的大小", "殘差的總和"],
                    "B",
                    "R² = 1 − SS_res/SS_tot；高 R² 不代表能獲利，也不代表因果。",
                ),
                (
                    "heteroskedasticity（異質變異）主要影響 OLS 的？",
                    ["係數估計值", "標準誤（以及 t 統計量）", "R²", "截距"],
                    "B",
                    "OLS 係數仍不偏，但古典標準誤失準——推論（顯著性）會被誤導。",
                ),
                (
                    "HC0/HC1 穩健標準誤改變的是？",
                    ["迴歸係數", "標準誤", "殘差", "R²"],
                    "B",
                    "sandwich 估計只修正係數共變異數矩陣的估計；點估計完全不變。",
                ),
            ],
        ),
        mistakes(
            [
                "忘記在設計矩陣加入截距欄。",
                "把高 $R^2$ 當成策略可獲利的證據。",
                "忽略 heteroskedasticity 使一般 OLS 標準誤失準。",
                "遺漏重要變數造成 omitted variable bias。",
                "把迴歸係數直接當成可交易訊號。",
            ]
        ),
        checklist(
            [
                "能推導並實作 $\\hat\\beta=(X^\\top X)^{-1}X^\\top y$。",
                "能解讀截距、beta、殘差與 $R^2$。",
                "能計算 rolling beta 並解釋其波動。",
                "能說明 omitted variable bias。",
            ]
        ),
        footer_references(solution),
    ]
    return cells
