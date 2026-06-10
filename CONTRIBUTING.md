# 貢獻指南 / Contributing Guide

感謝你願意為 **quant-math-roadmap** 貢獻！本專案是一個公開、教育取向的開源
專案，歡迎修正錯誤、改善解說、新增習題與測試。

請先閱讀 [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) 與
[`docs/open_source_and_data_policy.md`](docs/open_source_and_data_policy.md)。

---

## 1. 建立開發環境（uv）

本專案使用 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync --extra dev            # 依 uv.lock 建立 .venv 並安裝開發相依套件
uv run pre-commit install      # 安裝 git pre-commit hooks
```

驗證環境：

```bash
uv run pytest
uv run python scripts/generate_synthetic_dataset.py
```

## 2. 程式碼品質檢查

提交前，所有檢查都必須通過：

```bash
uv run ruff check .            # lint
uv run ruff format --check .   # 格式
uv run mypy                    # 型別檢查
uv run pytest                  # 測試
uv run python scripts/run_all_notebooks.py   # notebook 驗證
```

或使用 `Makefile` 捷徑：`make lint`、`make test`、`make notebooks`。

## 3. 程式碼風格

- **Python 3.12+**，使用 `src/` layout。
- 可重用邏輯放在 `src/quant_math_roadmap/`，**不要**把核心邏輯只寫在 notebook。
- 公開函式需有 **type annotations** 與 **docstring**。
- 函式應**小而可測試**。
- 圖表只用 **matplotlib**（不使用 seaborn）；每張圖一個 figure，需有標題、
  軸標籤、必要時的圖例，以及一段說明用的 markdown。
- 不要寫只描述「程式做什麼」的註解；只在「為什麼」不明顯時才加註解。

## 4. 如何新增或修改 notebook

本專案的 notebook 由 `scripts/build_notebooks.py` 產生（內容在
`scripts/_notebook_lib/`，一週一檔），以確保主 notebook、解答 notebook 與
英文版（`notebooks/en/`）永遠同步。**請勿直接編輯 `.ipynb`**——CI 的
`--check` 會偵測出與產生器不一致的 drift。

1. 修改（或新增）`scripts/_notebook_lib/weekN.py` 的 `week(solution)` 建構函式；
   新週次需同時提供 `weekN_en.py` 英文版，並登記進
   `scripts/_notebook_lib/__init__.py` 的 `NOTEBOOKS` / `NOTEBOOKS_EN`。
2. 執行 `uv run python scripts/build_notebooks.py`（可用 `--only NN` 只重建一週）。
3. 用 `uv run python scripts/build_notebooks.py --check` 確認產生器與
   committed `.ipynb` 一致。
4. 每本 notebook 必須包含：標題與學習目標、預估時間、先備概念、外部資源連結、
   概念說明、LaTeX 數學式、可重現的程式碼、明確標示的練習
   （基礎／應用／反思）、小測驗、「常見錯誤」、「完成本週後…」檢查清單、參考與致謝。
5. notebook 必須能**離線、由上到下**執行完畢，且預設使用合成資料。

## 5. 如何新增測試

- 測試放在 `tests/`，檔名 `test_*.py`。
- 對應的可重用邏輯應實作在 `src/` 中。
- 使用固定的隨機種子確保可重現。
- 與回測完整性相關的邏輯（look-ahead、交易成本、年化、baseline）**務必**
  附上測試。

## 6. 文件風格

- 教育文件以**繁體中文**為主，保留標準英文技術名詞。
- 數學式使用 Markdown LaTeX。
- 概念筆記應包含：動機、定義、核心公式、直覺、小範例、常見錯誤、檢查清單、
  延伸連結。

## 7. 嚴格政策（務必遵守）

提交的變更**絕對不可**包含：

- ❌ 任何**真實個人資訊**（人名、就學狀態、成績、email、學號、個人背景等）。
- ❌ 任何**下載的第三方市場資料**（`data/raw/` 已被 Git 忽略）。
- ❌ 任何**投資獲利宣稱**或把結果說成可投資策略。
- ❌ 任何**受版權保護的教育材料**（影片、投影片、教科書、外部習題集）的
  重製、轉錄或抓取——只能以官方標題與網址**連結**。

## 8. Pull Request 流程

1. Fork 並建立功能分支。
2. 進行變更，確保第 2 節的所有檢查通過。
3. 撰寫清楚的 commit 訊息（說明「為什麼」）。
4. 開啟 Pull Request，描述變更內容與動機。

---

## English summary

Contributions are welcome. Set up with `uv` (`uv venv --python 3.12` then
`uv pip install -e ".[dev]"`), install pre-commit hooks, and ensure `ruff`,
`mypy`, `pytest` and notebook validation all pass before submitting. Put
reusable logic in `src/` with type annotations and docstrings; keep functions
small and tested. Notebooks are generated from `scripts/build_notebooks.py` and
must run offline top-to-bottom on synthetic data. **Never commit** real
personal information, downloaded third-party market data, investment-profit
claims, or copyrighted educational material — link to official resources only.
