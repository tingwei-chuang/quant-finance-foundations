# quant-math-roadmap — 量化金融數學八週路線圖

> 一套**自學取向、可重現、嚴謹**的八週路線圖，協助具備程式設計經驗的學習者，
> 從複習數學基礎，前進到一個小而正確、防 leakage 的量化研究流程。

[![CI](https://github.com/quant-math-roadmap/quant-math-roadmap/actions/workflows/ci.yml/badge.svg)](https://github.com/quant-math-roadmap/quant-math-roadmap/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)

---

## 1. 專案目的

本專案是一份**八週準備計畫**（外加 Week 0 診斷週），目標是把一位技術底子不錯的
學習者，準備好去面對：

- 應用量化金融與系統化量化研究；
- 財務演算法課程；
- 計量經濟 / 時間序列課程；
- 嚴謹的回測專案。

專案聚焦於 **數學理解、可重現實驗、正確的評估方法論、實用的 Python 實作，
以及預防常見回測錯誤**。

## 2. 適合誰

本專案適合：

> 「具備程式設計與基礎機器學習經驗、過去學過微積分、線性代數與機率，
> 但需要重新複習並建立更紮實統計、迴歸、財務數學、投資組合、時間序列與
> leakage 控制回測基礎的學習者。」

教學語言以**繁體中文**為主；標準的英文技術名詞（statistics、regression、
backtesting…）予以保留。國際讀者請見 [`README_en.md`](README_en.md)。

## 3. 這個專案「不是」什麼

- ❌ **不是投資建議。** 本專案僅供教育與研究方法論用途。
- ❌ **不宣稱任何可獲利策略。** 所有 notebook 的結果都不代表實際可投資性。
- ❌ **不是進階數理金融教科書。** 本專案刻意**避開** high-frequency trading、
  進階 stochastic calculus、測度論機率，以及深度強化學習交易系統。

本專案聚焦於**理解、正確性與方法論**，而非追求績效。

## 4. 八週路線圖

| 週次 | 主題 | Notebook |
|------|------|----------|
| 0 | 環境設定與準備度診斷 | `00_setup_and_readiness_diagnostic.ipynb` |
| 1 | 報酬、風險與線性代數 | `01_returns_covariance_and_linear_algebra.ipynb` |
| 2 | 多變數微積分與最小變異投資組合 | `02_multivariable_calculus_and_min_variance_portfolio.ipynb` |
| 3 | 機率複習：模擬、LLN 與 CLT | `03_probability_simulation_lln_clt.ipynb` |
| 4 | 策略報酬的統計推論 | `04_statistical_inference_for_strategy_returns.ipynb` |
| 5 | 迴歸與因子模型 | `05_regression_and_factor_models.ipynb` |
| 6 | 財務數學與選擇權定價 | `06_financial_mathematics_and_option_pricing.ipynb` |
| 7 | 時間序列診斷 | `07_time_series_diagnostics.ipynb` |
| 8 | 走動式預測與回測完整性 | `08_walk_forward_forecasting_and_backtesting_integrity.ipynb` |

完整路線圖請見 [`docs/roadmap.md`](docs/roadmap.md)；每週詳細計畫請見
[`docs/study_guide.md`](docs/study_guide.md)。

## 5. 環境設定（使用 uv）

本專案使用 [uv](https://docs.astral.sh/uv/) 管理環境與相依套件。

```bash
# 1. 安裝 uv（見官方文件，支援 Windows / macOS / Linux / WSL）
#    https://docs.astral.sh/uv/getting-started/installation/

# 2. 建立並同步環境（含開發相依套件）
uv venv --python 3.12
uv pip install -e ".[dev]"

# 3. 產生合成範例資料集
uv run python scripts/generate_synthetic_dataset.py

# 4. 啟動 JupyterLab
uv run jupyter lab

# 5. 執行測試
uv run pytest

# 6. 驗證所有 notebook 可從頭執行到底
uv run python scripts/run_all_notebooks.py
```

也可使用 `Makefile` 的捷徑（見下方「貢獻」一節）。

## 6. 倉庫結構

```
quant-math-roadmap/
├── README.md / README_en.md      # 中／英文說明
├── docs/                         # 路線圖、概念筆記、政策文件
│   ├── roadmap.md  study_guide.md  resources.md
│   ├── math/                     # 數學概念筆記（cheatsheets）
│   └── finance/                  # 財務概念筆記
├── notebooks/                    # Week 0–8 主 notebook
│   └── solutions/                # 完整參考解答 notebook
├── src/quant_math_roadmap/       # 可重用、可測試的 Python 套件
│   ├── data/  math/  finance/
│   ├── time_series/  backtesting/
├── scripts/                      # 資料產生、notebook 驗證等腳本
├── data/                         # 合成範例資料（raw/ 被 Git 忽略）
└── tests/                        # pytest 測試
```

數學邏輯實作於 `src/`，由 notebook 匯入使用——notebook 不重複造輪子。

## 7. 學習流程

每一週，建議依以下流程進行：

1. **讀概念筆記**（`docs/math/` 或 `docs/finance/` 的對應 cheatsheet）。
2. **看／讀連結的官方外部資源**（見 [`docs/resources.md`](docs/resources.md)）。
3. **完成 notebook**：依序執行，動手填寫 TODO 練習。
4. **解習題**：每本 notebook 含概念題、程式題與反思題。
5. **記錄錯誤**：把卡住或弄錯的地方寫進 [`docs/progress_tracker.md`](docs/progress_tracker.md)。
6. **通過就緒檢查清單**：誠實打勾後再前進。

## 8. 資料政策

- 預設的 notebook 與測試**完全使用合成資料**，不需網路連線。
- 合成資料由 `scripts/generate_synthetic_dataset.py` 以固定種子產生，可重現。
- **不**將下載的第三方市場資料提交進本倉庫；`data/raw/` 被 Git 忽略。
- 選用的真實資料工作流程僅以腳本／說明提供
  （`scripts/optional_download_market_data.py`）。
- **使用者須自行遵守各資料供應商的使用條款。**

詳見 [`docs/open_source_and_data_policy.md`](docs/open_source_and_data_policy.md)
與 [`data/README.md`](data/README.md)。

## 9. 貢獻

歡迎貢獻！請先閱讀 [`CONTRIBUTING.md`](CONTRIBUTING.md)。提交前請確認：

```bash
uv run ruff check .      # 程式碼風格與 lint
uv run ruff format --check .
uv run mypy              # 型別檢查
uv run pytest            # 測試
```

貢獻時請遵守 [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)；安全性問題請見
[`SECURITY.md`](SECURITY.md)。

## 10. 授權與引用

- 本專案採用 **MIT License**（見 [`LICENSE`](LICENSE)）。
- 引用本專案請見 [`CITATION.cff`](CITATION.cff)。

---

## 免責聲明

本專案僅供**教育與研究方法論**用途，**不構成投資建議**。任何 notebook 的結果
都**不應**被解讀為實際可獲利、可投資或經過驗證的策略。使用真實市場資料時，
使用者須自行遵守各資料供應商的使用條款。

英文版說明請見 **[README_en.md](README_en.md)**。
