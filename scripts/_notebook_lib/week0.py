"""Builder for the Week 0 notebook (auto-extracted from build_notebooks.py).

Per-week modules let one week be edited (and merged) independently of the
others. See scripts/_notebook_lib/__init__.py for the dispatch table.
"""

from __future__ import annotations

import nbformat as nbf

from .cells import code, ex_code, md
from .parts import (
    checklist,
    docs_prefix,
    exercises_intro,
    footer_references,
    header,
    mistakes,
)


def week(solution: bool) -> list[nbf.NotebookNode]:
    cells = header(
        solution=solution,
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
            f"把分數同步填到 [`docs/progress_tracker.md`]({docs_prefix(solution)}progress_tracker.md)。"
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
        footer_references(solution),
    ]
    return cells
