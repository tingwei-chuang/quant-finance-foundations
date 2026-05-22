"""Build the course notebooks (Week 0-8) and their solution counterparts.

The notebooks are *generated* from this single script so that the main and
solution versions stay perfectly in sync: they share all explanatory and setup
cells, and differ only in the exercise cells (a runnable starter in the main
notebook, a full reference answer in the solution notebook).

The generated ``.ipynb`` files are the artefacts learners actually open and
edit. Re-run this script to regenerate the scaffold::

    uv run python scripts/build_notebooks.py

Every generated notebook:

* runs top-to-bottom offline using synthetic data only;
* uses deterministic seeds;
* imports reusable logic from the ``quant_math_roadmap`` package;
* contains the pedagogical structure required by the roadmap.
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

REPO_ROOT = Path(__file__).resolve().parents[1]
NB_DIR = REPO_ROOT / "notebooks"
SOL_DIR = NB_DIR / "solutions"

KERNELSPEC = {"display_name": "Python 3", "language": "python", "name": "python3"}
LANGUAGE_INFO = {"name": "python", "version": "3.12"}


# --------------------------------------------------------------------------
# Cell helpers
# --------------------------------------------------------------------------
def md(text: str) -> nbf.NotebookNode:
    """Return a markdown cell from a (dedented) string."""
    return nbf.v4.new_markdown_cell(text.strip("\n"))


def code(text: str) -> nbf.NotebookNode:
    """Return a code cell from a (dedented) string."""
    return nbf.v4.new_code_cell(text.strip("\n"))


def ex_code(solution: bool, prompt: str, starter: str, answer: str) -> nbf.NotebookNode:
    """Return an exercise code cell.

    The main notebook gets a runnable ``starter``; the solution notebook gets
    the full ``answer``. Both keep the notebook executable end-to-end.
    """
    body = answer if solution else starter
    return code(prompt.strip("\n") + "\n" + body.strip("\n"))


def build(cells: list[nbf.NotebookNode]) -> nbf.NotebookNode:
    """Assemble cells into a notebook node with a pinned kernelspec."""
    notebook = nbf.v4.new_notebook()
    notebook.cells = cells
    notebook.metadata = {"kernelspec": KERNELSPEC, "language_info": LANGUAGE_INFO}
    return notebook


def header(
    *,
    week: str,
    title: str,
    objectives: list[str],
    hours: str,
    prereqs: list[str],
    resources: list[tuple[str, str]],
) -> list[nbf.NotebookNode]:
    """Return the standard opening cells shared by every notebook."""
    obj = "\n".join(f"- {o}" for o in objectives)
    pre = "\n".join(f"- {p}" for p in prereqs)
    res = "\n".join(f"- [{name}]({url})" for name, url in resources)
    res_block = res if resources else "- （本週為環境設定，無外部資源）"
    return [
        md(
            f"# {week} — {title}\n\n"
            "> 本 notebook 屬於「量化數學路線圖」（quant-math-roadmap）開源教學專案。\n"
            "> 僅供**教育與研究方法論**用途，**不構成投資建議**，任何結果都不代表"
            "實際可獲利或可投資的策略。"
        ),
        md(
            "## 學習目標\n\n"
            f"{obj}\n\n"
            "## 預估學習時間\n\n"
            f"約 {hours}。\n\n"
            "## 先備概念\n\n"
            f"{pre}\n\n"
            "## 外部學習資源\n\n"
            f"{res_block}\n\n"
            "> 外部資源僅供參考連結；本專案不重製任何受版權保護的課程材料。"
        ),
    ]


FOOTER_REFERENCES = md(
    "## 參考與致謝\n\n"
    "- 本 notebook 的所有解說、範例與習題皆為本專案**原創**撰寫。\n"
    "- 推薦的外部學習資源請見 [`docs/resources.md`](../docs/resources.md)。\n"
    "- 數學與財務概念筆記請見 [`docs/math/`](../docs/math/) 與 "
    "[`docs/finance/`](../docs/finance/)。\n\n"
    "### 隱私與免責聲明\n\n"
    "- 本 notebook 不含任何真實個人資訊。\n"
    "- 本 notebook 僅使用可重現的合成資料，不需要網路連線。\n"
    "- 本 notebook 不對任何策略做出實際投資獲利的宣稱。"
)


def checklist(items: list[str]) -> nbf.NotebookNode:
    """Return the 'what you should be able to do' checklist cell."""
    body = "\n".join(f"- [ ] {i}" for i in items)
    return md("## 完成本週後，你應該能做到什麼\n\n" + body)


def mistakes(items: list[str]) -> nbf.NotebookNode:
    """Return the common-mistakes cell."""
    body = "\n".join(f"- **{i}**" for i in items)
    return md("## 常見錯誤\n\n" + body)


def exercises_intro() -> nbf.NotebookNode:
    """Return the exercises section heading."""
    return md(
        "## 練習\n\n"
        "請依序完成以下練習。**基礎練習**鞏固定義，**應用練習**動手寫程式，"
        "**反思問題**把數學連結到回測與研究方法論。\n\n"
        "> 主 notebook 的程式練習提供可執行的起始碼（starter）。完整參考解答請見 "
        "`notebooks/solutions/` 對應的 `_solution` notebook。"
    )


# --------------------------------------------------------------------------
# Week 0 — Setup and readiness diagnostic
# --------------------------------------------------------------------------
def week0(solution: bool) -> list[nbf.NotebookNode]:
    cells = header(
        week="Week 0",
        title="環境設定與準備度診斷",
        objectives=[
            "確認 Python 環境與 `quant_math_roadmap` 套件可正常運作。",
            "產生並載入可重現的合成價格資料。",
            "對八個主題做誠實的自我診斷，並得到建議學習路徑。",
        ],
        hours="1.5–2.5 小時",
        prereqs=["基本 Python", "已依 README 用 uv 建立環境"],
        resources=[],
    )
    cells += [
        md("## 1. 環境檢查\n\n先確認 Python 版本（本專案需要 3.12+）與核心套件可匯入。"),
        code(
            "import sys\n"
            "print('Python', sys.version.split()[0])\n"
            "assert sys.version_info >= (3, 12), '請使用 Python 3.12 以上版本'\n"
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
            "print('quant_math_roadmap 版本:', qmr.__version__)\n"
            "print('套件匯入成功 — 環境設定完成。')"
        ),
        md(
            "## 2. 產生與載入合成資料\n\n"
            "本專案的所有 notebook **預設只使用合成資料**，完全可重現、不需網路。\n\n"
            "下面先用 `SyntheticConfig` 產生一組相關資產價格，再示範如何載入"
            "專案內建的範例資料集 `data/sample/synthetic_prices.csv`。"
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
            "ax.set_title('合成資產價格（Week 0 範例）')\n"
            "ax.set_xlabel('日期')\n"
            "ax.set_ylabel('價格')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md(
            "上圖每條線是一個合成資產的價格路徑。它們**不是**真實資產，只是教學工具。"
            "因為使用固定亂數種子，你每次執行都會得到相同結果。"
        ),
        code(
            "sample_prices = load_sample_prices()\n"
            "print('範例資料集形狀:', sample_prices.shape)\n"
            "print('日期範圍:', sample_prices.index[0].date(), '~', "
            "sample_prices.index[-1].date())\n"
            "sample_prices.head()"
        ),
        md(
            "## 3. 自我診斷清單\n\n"
            "對以下每個主題誠實評分（**1 = 完全不熟悉，5 = 能對他人清楚解釋**）。"
            "本診斷**不**依個人身分評分，只幫助你規劃學習。\n\n"
            "| 主題 | 對應週次 | 你的評分 (1–5) |\n"
            "|------|:--------:|:--------------:|\n"
            "| 線性代數（特徵值、PSD、quadratic form） | Week 1 |  |\n"
            "| 多變數微積分（梯度、Hessian、Lagrange） | Week 2 |  |\n"
            "| 機率（LLN、CLT、條件機率） | Week 3 |  |\n"
            "| 統計推論（信賴區間、p-value、bootstrap） | Week 4 |  |\n"
            "| 迴歸（OLS、beta、殘差） | Week 5 |  |\n"
            "| 財務數學（折現、債券、選擇權 payoff） | Week 6 |  |\n"
            "| 時間序列（定態性、ACF、AR） | Week 7 |  |\n"
            "| 回測完整性（leakage、交易成本） | Week 8 |  |\n\n"
            "把分數同步填到 [`docs/progress_tracker.md`](../docs/progress_tracker.md)。"
        ),
        md(
            "## 4. 小概念題\n\n"
            "先**不要**寫程式，用紙筆或心算回答（解答在 notebook 末段）：\n\n"
            "1. 若某資產價格從 100 漲到 110，simple return 與 log return 各是多少？\n"
            "2. 「樣本平均」本身是不是一個隨機變數？為什麼？\n"
            "3. 為什麼用隨機方式切分時間序列資料來做 train/test 是危險的？"
        ),
        exercises_intro(),
        md(
            "### 基礎練習\n\n"
            "1. 用一句話分別定義 simple return 與 log return。\n"
            "2. 解釋為什麼合成資料對「可重現性」很重要。\n"
            "3. 列出你自評分數 ≤ 2 的主題。"
        ),
        md("### 應用練習"),
        ex_code(
            solution,
            prompt=(
                "# 應用練習 1：計算 prices 第一個資產的 simple return 序列。\n"
                "# 提示：可用 quant_math_roadmap.finance.returns.simple_returns"
            ),
            starter=(
                "from quant_math_roadmap.finance.returns import simple_returns\n"
                "first_asset = prices.iloc[:, 0]\n"
                "asset_returns = None  # TODO: 換成 simple_returns(first_asset)\n"
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
                "# 應用練習 2：計算該資產報酬的平均值與標準差。\n"
                "# 思考：這兩個數字各自有多少不確定性？（Week 3、4 會回答）"
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
            "### 反思問題\n\n"
            "1. 在你看過任何「漂亮的權益曲線」後，應該先問哪三個問題才決定要不要相信它？"
        ),
        mistakes(
            [
                "把 simple return 與 log return 混用而不自知。",
                "用沒有固定種子的隨機資料，導致結果無法重現。",
                "看到一條上升的權益曲線就相信策略有效。",
            ]
        ),
        checklist(
            [
                "能成功匯入 `quant_math_roadmap` 並執行整本 notebook。",
                "能產生並載入可重現的合成資料。",
                "能誠實列出自己最弱的 2–3 個主題並規劃學習路徑。",
            ]
        ),
        md(
            "## 建議學習路徑\n\n"
            "根據第 3 節的自評：\n\n"
            "- **某主題評分 ≤ 2**：先讀對應的 `docs/math/` 或 `docs/finance/` 概念筆記，"
            "再做該週 notebook，並預留額外時間看外部資源。\n"
            "- **評分為 3**：照正常節奏進行，但在 notebook 練習多花時間。\n"
            "- **評分 ≥ 4**：可較快通過該週，但仍務必完成回測完整性（Week 8）。\n\n"
            "無論自評如何，**Week 8（回測完整性）對所有人都是必修**。"
        ),
        md(
            "## 小概念題解答\n\n"
            "1. simple return = 110/100 − 1 = **0.10（10%）**；"
            "log return = ln(110/100) ≈ **0.0953**。漲幅越大，兩者差越多。\n"
            "2. **是**。樣本平均是資料的函數，而資料是隨機抽樣的結果，"
            "所以樣本平均本身是隨機變數，會隨樣本不同而變動（Week 3、4 主題）。\n"
            "3. 因為隨機切分會讓模型用到「未來」的資料來預測「過去」，"
            "造成 look-ahead bias，使回測結果過度樂觀（Week 7、8 主題）。"
        ),
        FOOTER_REFERENCES,
    ]
    return cells


# --------------------------------------------------------------------------
# Week 1 — Returns, covariance, and linear algebra
# --------------------------------------------------------------------------
def week1(solution: bool) -> list[nbf.NotebookNode]:
    cells = header(
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
            "    eigendecomposition, is_positive_semidefinite, quadratic_form,\n"
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
        FOOTER_REFERENCES,
    ]
    return cells


# --------------------------------------------------------------------------
# Week 2 — Multivariable calculus and the minimum-variance portfolio
# --------------------------------------------------------------------------
def week2(solution: bool) -> list[nbf.NotebookNode]:
    cells = header(
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
        FOOTER_REFERENCES,
    ]
    return cells


# --------------------------------------------------------------------------
# Week 3 — Probability: simulation, LLN, CLT
# --------------------------------------------------------------------------
def week3(solution: bool) -> list[nbf.NotebookNode]:
    cells = header(
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
            "    sampling_distribution_of_mean, simulate_normal,\n"
            ")\n"
            "\n"
            "rng = np.random.default_rng(2024)"
        ),
        md("### 模擬分布並估計動差"),
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
        FOOTER_REFERENCES,
    ]
    return cells


# --------------------------------------------------------------------------
# Week 4 — Statistical inference for strategy returns
# --------------------------------------------------------------------------
def week4(solution: bool) -> list[nbf.NotebookNode]:
    cells = header(
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
        FOOTER_REFERENCES,
    ]
    return cells


# --------------------------------------------------------------------------
# Week 5 — Regression and factor models
# --------------------------------------------------------------------------
def week5(solution: bool) -> list[nbf.NotebookNode]:
    cells = header(
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
        FOOTER_REFERENCES,
    ]
    return cells


# --------------------------------------------------------------------------
# Week 6 — Financial mathematics and option pricing
# --------------------------------------------------------------------------
def week6(solution: bool) -> list[nbf.NotebookNode]:
    cells = header(
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
        FOOTER_REFERENCES,
    ]
    return cells


# --------------------------------------------------------------------------
# Week 7 — Time-series diagnostics
# --------------------------------------------------------------------------
def week7(solution: bool) -> list[nbf.NotebookNode]:
    cells = header(
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
            "    rolling_mean, rolling_volatility,\n"
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
            "roll_mean = rolling_mean(returns, window=40)\n"
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
        FOOTER_REFERENCES,
    ]
    return cells


# --------------------------------------------------------------------------
# Week 8 — Walk-forward forecasting and backtesting integrity
# --------------------------------------------------------------------------
def week8(solution: bool) -> list[nbf.NotebookNode]:
    cells = header(
        week="Week 8",
        title="走動式預測與回測完整性",
        objectives=[
            "實作時間式 train/test 切分與走動式評估。",
            "建立預測模型並與 naive baseline 比較。",
            "套用交易成本，比較 gross 與 net 績效。",
            "刻意展示一個 leaked 模型，並說明為何其結果無效。",
        ],
        hours="10–12 小時",
        prereqs=["Week 7 的時間序列", "Week 5 的迴歸"],
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
            "本週把前七週整合成一個**正確的**研究流程。核心原則：\n\n"
            "1. **時間式切分**：訓練集一定在測試集之前。\n"
            "2. **走動式評估**：expanding（錨定起點、視窗變長）或 rolling"
            "（固定長度、向前滑動）。\n"
            "3. **無 leakage**：時間 $t$ 的特徵只能用 $t$ 以前的資訊；"
            "由訊號決定的部位必須**正確地往後位移**才能對應未來報酬。\n"
            "4. **交易成本**：比較 gross 與 net；net 才是誠實的結果。\n"
            "5. **baseline**：贏不過 naive baseline 的模型沒有價值。\n\n"
            "> 本 notebook 是**方法論訓練**，不是可投資策略。所有結果都不代表"
            "真實可獲利性。"
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
            "    forecast_error_metrics, historical_mean_forecast, zero_forecast,\n"
            ")\n"
            "from quant_math_roadmap.backtesting.engine import run_backtest, buy_and_hold_benchmark\n"
            "from quant_math_roadmap.backtesting.leakage_checks import (\n"
            "    assert_no_lookahead, leaked_strategy_returns, signal_to_positions,\n"
            ")\n"
            "from quant_math_roadmap.backtesting.costs import cost_summary\n"
            "\n"
            "config = SyntheticConfig(n_assets=1, n_periods=900, seed=33)\n"
            "prices = generate_correlated_prices(config).iloc[:, 0]\n"
            "returns = simple_returns(prices)\n"
            "print('報酬序列長度:', len(returns))"
        ),
        md("### 時間式 train/test 切分"),
        code(
            "split = train_test_split_time(len(returns), test_size=0.3)\n"
            "train = returns.iloc[split.train_index]\n"
            "test = returns.iloc[split.test_index]\n"
            "print(f'訓練集: {len(train)} 期 | 測試集: {len(test)} 期')\n"
            "print('訓練集最後一天 <', '測試集第一天:',\n"
            "      train.index[-1] < test.index[0])"
        ),
        md("### 預測模型 vs naive baseline"),
        code(
            "# 用走動式 expanding window 做誠實的逐期預測\n"
            "predictions, actuals, baseline_mean, baseline_zero = [], [], [], []\n"
            "for sp in expanding_window_splits(len(returns), initial_train_size=400,\n"
            "                                  test_size=1):\n"
            "    tr = returns.iloc[sp.train_index]\n"
            "    te = returns.iloc[sp.test_index]\n"
            "    # 簡單線性 lag 預測：用最近一期報酬乘上訓練集的 lag-1 自相關\n"
            "    lag1 = tr.autocorr(lag=1)\n"
            "    pred = lag1 * tr.iloc[-1]\n"
            "    predictions.append(pred)\n"
            "    actuals.append(te.iloc[0])\n"
            "    baseline_mean.append(historical_mean_forecast(tr))\n"
            "    baseline_zero.append(zero_forecast(tr))\n"
            "\n"
            "actual_s = pd.Series(actuals)\n"
            "print('lag 預測   :', forecast_error_metrics(actual_s, pd.Series(predictions)))\n"
            "print('歷史均值   :', forecast_error_metrics(actual_s, pd.Series(baseline_mean)))\n"
            "print('naive 零   :', forecast_error_metrics(actual_s, pd.Series(baseline_zero)))"
        ),
        md(
            "在合成的（近乎白噪音）報酬上，預測模型**通常贏不過** naive baseline。"
            "這是健康的結果：它誠實反映了「報酬很難預測」。"
        ),
        md("### 把訊號轉成部位（正確位移以避免 leakage）"),
        code(
            "# 訊號：昨天報酬的正負號。部位必須往後位移 1 期才能交易。\n"
            "raw_signal = np.sign(returns)\n"
            "positions = signal_to_positions(raw_signal, lag=1)\n"
            "print('前 5 個訊號:', raw_signal.head().to_list())\n"
            "print('前 5 個部位:', positions.head().to_list())\n"
            "print('部位是位移後的訊號 — 第一天為 0（沒有可用資訊）。')"
        ),
        md("### Gross vs net：交易成本的影響"),
        code(
            "result = run_backtest(raw_signal, returns, signal_lag=1,\n"
            "                      cost_per_unit_turnover=0.0005)\n"
            "summary = result.summary()\n"
            "for k, v in summary.items():\n"
            "    print(f'{k}: {v:.6f}')\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(result.gross_equity.index, result.gross_equity.values,\n"
            "        label='gross（未計成本）')\n"
            "ax.plot(result.net_equity.index, result.net_equity.values,\n"
            "        label='net（已計成本）')\n"
            "bnh = buy_and_hold_benchmark(returns)\n"
            "ax.plot(bnh.index, bnh.values, label='buy-and-hold 基準', linestyle='--')\n"
            "ax.set_title('回測權益曲線：gross vs net vs 基準')\n"
            "ax.set_xlabel('日期')\n"
            "ax.set_ylabel('權益（起始 = 1）')\n"
            "ax.legend()\n"
            "plt.show()"
        ),
        md("交易成本把 gross 與 net 拉開明顯差距。**只看 gross 的回測是不誠實的。**"),
        md(
            "### 刻意展示 data leakage（無效示範）\n\n"
            "下面這個實驗**故意作弊**：它用「**當期**報酬的正負號」當部位——"
            "這需要知道未來。它必然每期都賺，績效荒謬地好。\n\n"
            "> **這個結果絕對不能被當成策略。** 它存在的唯一目的，是讓你認得"
            "leakage 長什麼樣子。"
        ),
        code(
            "leaked = leaked_strategy_returns(returns)\n"
            "leaked_equity = (1 + leaked).cumprod()\n"
            "honest_equity = result.net_equity\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.plot(leaked_equity.index, leaked_equity.values,\n"
            "        label='【無效】leaked 模型（偷看未來）')\n"
            "ax.plot(honest_equity.index, honest_equity.values,\n"
            "        label='誠實回測（net）')\n"
            "ax.set_title('Leakage 示範：荒謬的曲線 = 警訊，不是策略')\n"
            "ax.set_xlabel('日期')\n"
            "ax.set_ylabel('權益（起始 = 1）')\n"
            "ax.legend()\n"
            "plt.show()\n"
            "print(f'leaked 總報酬 = {(leaked_equity.iloc[-1] - 1):.2%}  <-- 不可能、無效')\n"
            "print(f'誠實 net 總報酬 = {(honest_equity.iloc[-1] - 1):.2%}')"
        ),
        code(
            "# leakage 自動檢查：把當期報酬當特徵會被偵測出來\n"
            "try:\n"
            "    assert_no_lookahead(returns, returns, name='當期報酬當特徵')\n"
            "    print('未偵測到 leakage')\n"
            "except ValueError as exc:\n"
            "    print('偵測到 leakage:', exc)"
        ),
        exercises_intro(),
        md(
            "### 基礎練習\n\n"
            "1. 用自己的話解釋 expanding window 與 rolling window 的差別。\n"
            "2. 為什麼由訊號決定的部位一定要往後位移？\n"
            "3. 什麼是 survivorship bias？它為何會讓回測過度樂觀？"
        ),
        md("### 應用練習"),
        ex_code(
            solution,
            prompt=("# 應用練習 1：把交易成本從 5 bps 提高到 20 bps，比較 net 總報酬。"),
            starter=(
                "high_cost = None  # TODO: run_backtest(raw_signal, returns, cost_per_unit_turnover=0.002)\n"
                "if high_cost is not None:\n"
                "    print('20 bps net 總報酬:', high_cost.summary()['total_net_return'])"
            ),
            answer=(
                "high_cost = run_backtest(raw_signal, returns, signal_lag=1,\n"
                "                         cost_per_unit_turnover=0.002)\n"
                "print('5 bps  net 總報酬:', round(summary['total_net_return'], 4))\n"
                "print('20 bps net 總報酬:', round(high_cost.summary()['total_net_return'], 4))\n"
                "print('成本越高，net 績效越差 — 高週轉策略對成本特別敏感。')"
            ),
        ),
        ex_code(
            solution,
            prompt=("# 應用練習 2：用 cost_summary 比較 gross 與 net 的總報酬與成本拖累。"),
            starter=(
                "cs = None  # TODO: cost_summary(result.gross_returns, result.net_returns)\n"
                "if cs is not None:\n"
                "    print(cs)"
            ),
            answer=(
                "cs = cost_summary(result.gross_returns, result.net_returns)\n"
                "for k, v in cs.items():\n"
                "    print(f'{k}: {v:.6f}')\n"
                "print('cost_drag 一定 >= 0：成本只會拖累績效。')"
            ),
        ),
        md(
            "### 反思問題\n\n"
            "1. 回顧 Week 1–7。一個看起來很賺的回測，可能在哪些環節偷偷"
            "引入了 leakage、過度配適或多重檢定的問題？請至少列出三點，"
            "並對照 [`docs/common_backtesting_mistakes.md`](../docs/common_backtesting_mistakes.md)。"
        ),
        mistakes(
            [
                "用隨機切分而非時間式切分。",
                "部位沒有往後位移，等於偷看未來（look-ahead bias）。",
                "只報告 gross 績效，忽略交易成本與週轉。",
                "沒有和 naive baseline（零報酬、歷史均值、buy-and-hold）比較。",
                "把刻意 leaked 的荒謬結果誤當成真實策略。",
                "把 rolling 特徵前期不足的 NaN 用未來資訊回填。",
            ]
        ),
        checklist(
            [
                "能實作時間式切分與走動式評估。",
                "能把預測模型和 naive baseline 做誠實比較。",
                "能套用交易成本並比較 gross vs net。",
                "能辨識 leakage，並說明為何其結果無效。",
                "能完成一個無 leakage、含成本、可重現的小型回測流程。",
            ]
        ),
        md(
            "## 結語\n\n"
            "完成八週後，你已經能從「複習數學基礎」走到「一個小而正確、"
            "防 leakage 的量化研究流程」。請記得本路線圖的核心信念：\n\n"
            "**先正確評估，再追求精緻模型；先可重現，再談績效。**\n\n"
            "本專案是教育與研究方法論訓練，**不是投資建議**，也**不宣稱**任何"
            "可獲利策略。"
        ),
        FOOTER_REFERENCES,
    ]
    return cells


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
NOTEBOOKS = {
    "00_setup_and_readiness_diagnostic": week0,
    "01_returns_covariance_and_linear_algebra": week1,
    "02_multivariable_calculus_and_min_variance_portfolio": week2,
    "03_probability_simulation_lln_clt": week3,
    "04_statistical_inference_for_strategy_returns": week4,
    "05_regression_and_factor_models": week5,
    "06_financial_mathematics_and_option_pricing": week6,
    "07_time_series_diagnostics": week7,
    "08_walk_forward_forecasting_and_backtesting_integrity": week8,
}


def main() -> None:
    """Generate all main and solution notebooks."""
    NB_DIR.mkdir(parents=True, exist_ok=True)
    SOL_DIR.mkdir(parents=True, exist_ok=True)

    for stem, builder in NOTEBOOKS.items():
        main_nb = build(builder(solution=False))
        nbf.write(main_nb, NB_DIR / f"{stem}.ipynb")

        sol_cells = [
            md(
                f"# （參考解答）{stem}\n\n"
                "> 這是對應主 notebook 的**完整參考解答版**。建議先自己完成主"
                "notebook 的練習，再對照本檔。所有解說與解答皆為本專案原創。"
            ),
            *builder(solution=True),
        ]
        sol_nb = build(sol_cells)
        nbf.write(sol_nb, SOL_DIR / f"{stem}_solution.ipynb")
        print(f"generated {stem}.ipynb  (+ solution)")

    print(f"\nDone: {len(NOTEBOOKS)} main + {len(NOTEBOOKS)} solution notebooks.")


if __name__ == "__main__":
    main()
