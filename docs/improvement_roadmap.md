# 工程改進路線圖 / Engineering Improvement Roadmap

> 本文件是對整個倉庫的一次**深度 code review** 的產出：列出所有已確認的問題、
> 測試與工具鏈缺口、以及建議新增的功能，並依優先級包裝成可執行的路線圖。
>
> - **Review 日期**：2026-06-10
> - **Review 範圍**：`src/`（19 個模組）、`tests/`（8 個檔案）、`scripts/`（4 個）、
>   `notebooks/` 產生器、`index.html`、`docs/`、`pyproject.toml`、CI、pre-commit、Makefile。
> - **方法**：人工逐模組審查 + 邊界條件實測（標註「已實測」的項目都在
>   Python 3.12 環境中重現過）+ 文件連結與 API 引用的程式化交叉檢查。
> - 注意：本文件與課程內容的 [`roadmap.md`](roadmap.md) 無關；那是給學習者的
>   八週路線圖，這份是給**維護者**的工程路線圖。
>
> **狀態更新（2026-06-10 後續）**：P0–P3 全部已修並合併
> （測試 96 → 168、覆蓋率 66% → 84%、CI matrix 3 OS × 2 Python、加上
> `--check` notebook drift gate、`py.typed`、GitHub Pages workflow、pip-audit）。
> P4 feature backlog 仍未動工，按需取捨。

---

## 總覽

| 優先級 | 主題 | 項目數 | 預估工作量 |
|--------|------|:------:|------------|
| **P0** | 正確性錯誤（已實測重現） | 8 | ~1 天 |
| **P1** | 測試覆蓋與測試品質 | 9 | ~2 天 |
| **P2** | 工具鏈、CI 與發布基礎設施 | 11 | ~2 天 |
| **P3** | 文件、`index.html` 與 notebook 產生器 | 13 | ~2–3 天 |
| **P4** | 新功能（feature backlog） | 18 | 視取捨 |

目前測試覆蓋率：**整體 66%**。最弱模組：`data/validation.py` **18%**、
`data/loaders.py` **33%**、`data/synthetic.py` **33%**、
`time_series/forecasting.py` **48%**、`math/probability.py` **55%**。

---

## P0 — 正確性錯誤（應立即修復）

### P0-1. 佔位 URL 導致所有對外連結 404【已確認】
- **位置**：`pyproject.toml:55-56`、`README.md`（CI badge）、`CITATION.cff`
- **問題**：`Homepage`/`Repository`/badge 全部指向佔位組織
  `quant-math-roadmap/quant-math-roadmap`，實際倉庫是
  `tingwei-chuang/quant-finance-foundations`。badge 顯示 broken，發佈後所有連結 404。
- **修法**：三處全部改為真實倉庫 URL；`README_en.md` 同步補上（修正後的）badge。

### P0-2. 時區 bug：排程器日期在 UTC+ 時區整體偏移一天【已確認】
- **位置**：`index.html`（`todayISO()` 與 `fmt()`）
- **問題**：對 local-midnight 的 `Date` 呼叫 `toISOString()`，在 UTC+8（本專案的
  主要受眾時區）所有日期—including 預設開始日—都會往前移一天。
- **修法**：改用 `getFullYear()/getMonth()/getDate()` 格式化本地日期，
  全面棄用 `toISOString()`。

### P0-3. `discount_factor` 對 rate ≤ −100% 行為錯誤【已實測】
- **位置**：`src/quant_math_roadmap/finance/fixed_income.py:34`
- **問題**：`discount_factor(-2.0, 2.0)` 默默回傳 `1.0`（負底數偶數次方）；
  `discount_factor(-1.5, 2.5)` 直接 `TypeError`（複數結果）。
- **修法**：當 `1 + rate/periods_per_year <= 0` 時 raise `ValueError`；
  另外補測「溫和負利率」（合法情境，折現因子 > 1）。

### P0-4. long-only 最佳化器對零矩陣 `ZeroDivisionError`【已實測】
- **位置**：`src/quant_math_roadmap/math/optimization.py`（Lipschitz 步長）
- **問題**：`min_variance_weights_long_only(np.zeros((3,3)), ridge=0.0)` 因
  Lipschitz 常數為 0 而 `step = 1/0` 崩潰。預設 `ridge=1e-10` 恰好掩蓋了這個洞。
- **修法**：`lipschitz <= 0` 時 raise 清楚的 `ValueError`（或直接回傳等權重），
  加 regression test。

### P0-5. 資料驗證放行 `inf` 價格【已實測】
- **位置**：`src/quant_math_roadmap/data/validation.py`
- **問題**：`validate_price_frame` 只查 `isna()` 與 `<= 0`，`np.inf` 通過驗證——
  之後算報酬會產生 `inf`/`nan` 而難以追查源頭。
- **修法**：加入 `np.isfinite` 檢查。

### P0-6. `assert_no_lookahead` docstring 與實作不符【已確認】
- **位置**：`src/quant_math_roadmap/backtesting/leakage_checks.py:45-49`
- **問題**：docstring 宣稱會檢查 feature 與「`target_{t+1}`」的相關性，
  但程式只算 contemporaneous 相關。對一個**以教學誠實為核心**的專案，
  文件與行為不一致特別傷。
- **修法**：補上 `target.shift(-1)` 的檢查，或修改 docstring 如實描述。

### P0-7. buy-and-hold「turnover」把權重漂移誤計為交易【已實測】
- **位置**：`src/quant_math_roadmap/backtesting/baselines.py`
  （`baseline_turnover_comparison`）
- **問題**：buy-and-hold 開倉後**零交易**，但函式對「漂移中的權重」做
  `|Δw|` 加總（實測 100 天 ≈ 1.30），把自然漂移當成 turnover——這恰好違背
  本專案自己教的「buy-and-hold 不再平衡、無 turnover」的課。測試只斷言
  `bah < rebalanced` 所以沒抓到。
- **修法**：buy-and-hold 的 turnover 應為開倉的 1.0（之後為 0）；
  重寫計算並在 docstring 講清楚「權重變化 ≠ 交易」。

### P0-8. `_repo_root()` 在非 editable 安裝下失效【已確認】
- **位置**：`src/quant_math_roadmap/data/loaders.py:23`
- **問題**：`Path(__file__).resolve().parents[3]` 假設套件位於
  `<root>/src/quant_math_roadmap/`；若以 wheel 安裝到 site-packages，
  `load_sample_prices()` 會指向錯誤路徑。
- **修法**：將 `synthetic_prices.csv` 以 `importlib.resources` 打包進套件，
  或在找不到時給出明確的錯誤訊息說明僅支援 repo checkout。

---

## P1 — 測試覆蓋與測試品質

### P1-1. `data/loaders.py` 與 `data/validation.py` 零測試
新增 `tests/test_data_validation.py`：以 `tmp_path` 寫 CSV，覆蓋重複時間戳、
非正價格、缺值、`require_business_days`、`raise_if_failed`、
sample 檔不存在的 `FileNotFoundError`，以及 P0-5 的 `inf` 案例。

### P1-2. 已匯出但完全未測試／未使用的 public API【已確認】
`information_coefficient`、`fit_linear_lag_model`、`nearest_psd`、
`taylor_quadratic_approximation`、`simulate_bernoulli` 在 notebooks、scripts、
tests 中**零使用**。逐一決定：(a) 補測試並在 notebook 中採用，或 (b) 從
`__all__` 移除。教學倉庫不該扛沒人用的 API。

### P1-3. 核心指標缺測試
`sharpe_ratio`（量化教學倉庫最不該漏的）、`annualized_mean`、`turnover`、
`buy_and_hold_benchmark`、`forecast_error_metrics`、binomial `p_up` 越界的
`ValueError`、`bond_price` 非整數期數、`yield_to_maturity` bracket 失敗路徑。

### P1-4. 無法失敗的斷言
- `tests/test_backtesting_costs.py:70`：`cost_drag >= 0.0` 在成本函式變成
  identity 時照樣通過 → 改 `> 0`。
- `tests/test_backtesting_costs.py:110`：`annualized_turnover` 測試名為
  "scales" 卻只驗 `> 0` → 驗證 `f(p, 252) == 2 * f(p, 126)`。

### P1-5. put-call parity 容差過鬆
`tests/test_derivatives.py:82` 用 `abs=1e-2`；CRR 樹上 parity 成立到機器精度，
1 分錢的違反都該抓到 → 收緊到 `abs=1e-9`，並對 `put_call_parity_gap` 補
known-value 直接測試。

### P1-6. 重複測試
`test_honest_backtest_is_not_clairvoyant` 重複了
`test_leaked_strategy_is_unrealistically_profitable` 的核心斷言 → 合併，
或改驗 engine 特有行為（如 net-of-cost）。

### P1-7. `ols_fit` 對共線設計矩陣丟出原始 `LinAlgError`【已實測】
包成帶解釋的 `ValueError`（「設計矩陣共線／奇異，請檢查特徵」），補測試。

### P1-8. NaN 政策不一致【已實測】
`autocorrelation` 對含 NaN 序列默默回傳 NaN；`adf_stationarity_test` 則 raise。
統一為「驗證輸入、含 NaN 即 raise」，全模組一致。

### P1-9. 覆蓋率門檻
`pyproject.toml` 的 coverage 設定無 `fail_under`，CI 也沒有 `--cov-fail-under`，
覆蓋率可以無聲崩落 → 設 `fail_under = 80`（完成 P1-1～P1-3 後再上調）。

---

## P2 — 工具鏈、CI 與發布基礎設施

| # | 項目 | 位置 | 修法 |
|---|------|------|------|
| P2-1 | pre-commit ruff `v0.6.9` vs lockfile `0.15.14`，hook 與 CI 格式化可能互相打架 | `.pre-commit-config.yaml:18` | 對齊版本；定期 `pre-commit autoupdate` |
| P2-2 | mypy 只在 CI 跑，不在 pre-commit | `.pre-commit-config.yaml` | 加 local `uv run mypy` hook |
| P2-3 | CI 無 OS／Python matrix（宣稱 `>=3.12` 卻只測 3.12 + ubuntu） | `ci.yml:13,19` | matrix：`{ubuntu, macos, windows} × {3.12, 3.13}`；notebooks job 可留 ubuntu |
| P2-4 | CI 無 `concurrency`、無 cache、無 `permissions:` 限制、無排程觸發 | `ci.yml` | 加 `concurrency` + `enable-cache: true` + `permissions: contents: read` + 每週 `schedule` |
| P2-5 | 無相依套件安全掃描 | `ci.yml` | 加 `pip-audit` step |
| P2-6 | `index.html` 是門面卻沒有 GitHub Pages 部署 | （缺 workflow） | 加 `pages.yml`（upload-pages-artifact + deploy-pages） |
| P2-7 | notebook 驗證雙軌：CI 用 `pytest --nbmake`、Makefile 用 `run_all_notebooks.py`，逾時／kernel 處理可能分歧 | `Makefile:32` vs `ci.yml:46` | 統一走 nbmake；`run_all_notebooks.py` 降級為開發便利工具或移除 |
| P2-8 | `make lint` 漏掉 `ruff format --check`，本地通過 CI 卻可能失敗 | `Makefile:22` | lint target 補上 format check |
| P2-9 | 全型別套件卻沒有 `py.typed`，下游 mypy 拿不到型別 | `src/quant_math_roadmap/` | 加 `py.typed` 標記檔 |
| P2-10 | 全域忽略 `DeprecationWarning`/`FutureWarning`，pandas/numpy 棄用警告被吞掉 | `pyproject.toml:73` | 改為針對特定模組／訊息的 scoped ignore |
| P2-11 | classifiers 只列 3.12、套件名 `quant-math-roadmap` 與 repo 名 `quant-finance-foundations` 不一致 | `pyproject.toml` | 補 3.13 classifier（配合 P2-3）；README 明寫別名關係 |

---

## P3 — 文件、`index.html` 與 notebook 產生器

### index.html
| # | 嚴重度 | 問題 | 修法 |
|---|--------|------|------|
| P3-1 | 中 | 週卡片內的 LaTeX（`$w^\top\Sigma w$` 等）沒有 KaTeX/MathJax，訪客看到原始 `$` 標記 | 載入 KaTeX 或改寫成 `w<sup>T</sup>Σw` |
| P3-2 | 中 | 主題切換按鈕忽略 `prefers-color-scheme`：深色系統第一次點擊「沒反應」 | 以 `matchMedia` 推斷目前主題再切換 |
| P3-3 | 中 | `.btn-primary:hover` 寫死 `#1f4cc0`，深色主題下 hover 顏色脫離 token 系統 | 新增 `--accent-hover` token |
| P3-4 | 中 | `localStorage` 存取大多無 try/catch；Safari 私密模式下整個 IIFE 崩潰，排程器與追蹤器全滅 | safe-storage helper 包一層 |
| P3-5 | 中 | `**不提交**` 的 Markdown 語法殘留在 HTML `<p>` 內，星號直接顯示 | 改 `<strong>` |
| P3-6 | 中 | 只給 Unix 的 `curl … | sh` 安裝指令，卻宣稱支援 Windows | 補 PowerShell `irm … | iex` |
| P3-7 | 中 | 指向 `.ipynb`/`.md` 的相對連結在 GitHub Pages 上會 404 或下載原始檔 | 改 GitHub blob URL／nbviewer 連結 |
| P3-8 | 低 | tracker 狀態未驗證型別（存了 `5` 會在 strict mode 崩潰）；首次載入就持久化 `qmr.start`；W0 stride 寫死 3 天；時數欄位單位不一致；`th` 無 `scope`、`--fg-muted` 對比度 ≈3.4:1 低於 AA | 各別小修 |

### scripts / notebooks
| # | 嚴重度 | 問題 | 修法 |
|---|--------|------|------|
| P3-9 | 中 | **solution notebooks 的 docs 連結全部斷裂**：`../docs/...` 從 `notebooks/solutions/` 出發少一層 | cell builder 把 docs 前綴參數化，`solution=True` 用 `../../docs/` |
| P3-10 | 中 | 所有圖表標題為中文，但沒有任何 cell 設定 CJK 字型 → 大多數環境出現豆腐字 + glyph 警告 | 產生器輸出共用 setup cell：`rcParams["font.sans-serif"]` fallback + `axes.unicode_minus=False` |
| P3-11 | 中 | `build_notebooks.py` 1,975 行的字串巨石：嵌入程式碼無 highlight、無 lint、無法單週重建、無 drift 偵測（直接改 `.ipynb` 不會被發現） | 拆成 per-week jupytext 來源 + 薄組裝器；加 `--only WEEK` 與 `--check`（重生成→diff）接入 CI |
| P3-12 | 低 | `run_all_notebooks.py` 的 `glob("*.ipynb")` 會誤抓學習者的草稿 notebook；純序列執行、無 fail-fast | 改 `[0-9][0-9]_*.ipynb` pattern；加 `--jobs`/`--fail-fast`（若 P2-7 保留此腳本） |
| P3-13 | 低 | 文件零碎錯誤：`common_backtesting_mistakes.md` §8 指錯測試檔（實際在 `test_backtesting_costs.py`）；Week 7 產生未使用的 `roll_mean`；Week 1 import 了未用的 `quadratic_form`；Week 8 練習 starter 與 answer 的 `signal_lag` 不一致（靠預設值才對）；兩個 script 的 argparse formatter 不一致；`language_info` 釘 3.12 造成 Jupyter 重存後的雜訊 diff；`optional_download_market_data.py` 的 `--acknowledge-terms` 沒有實際 gate 任何下載 | 各別小修 |

---

## P4 — 新功能 backlog

### 數值與統計（教學價值高）
1. **Robust standard errors（HC/HAC）**：Week 5 講了 heteroskedasticity 概念，
   `ols_fit(robust="HC1")` 讓學習者親手比較標準誤差異。
2. **Block bootstrap**：報酬有自相關時 plain bootstrap 低估不確定性——
   加 `block_bootstrap_mean_ci` 並在 Week 4 對比。
3. **Deflated Sharpe Ratio／PSR**：多重檢定章節的天然延伸，把
   `false_discovery_demo` 的教訓變成可計算的校正指標。
4. **Ledoit–Wolf shrinkage**（經 scikit-learn）：與現有 ad-hoc shrinkage 對照。
5. **債券 duration 與 convexity**：Week 6 自然延伸，公式簡單、教學價值高。
6. **American option binomial pricer + 有限差分 Greeks**：CRR 樹已就位，
   增量成本低。
7. **Sortino／Calmar ratio**：補齊風險調整指標家族，並沿用 Sharpe 的警語風格。

### 回測方法論
8. **Purged / embargoed walk-forward splits**：時間切分的進階版，
   防止訓練測試邊界的資訊滲漏。
9. **多資產回測 engine**：現在的 engine 單資產；以權重矩陣 + 成本推廣，
   與 Week 2 的投組構建銜接。
10. **參數掃描 + 過擬合視覺化**：掃 lookback 參數、畫 in-sample vs
    out-of-sample 熱圖，把「curve-fitting」上成一課。

### 教學與內容
11. **Hypothesis property-based tests**：put-call parity ∀(S,K,r,σ,T)、
    simple↔log 來回轉換、simplex 投影不變量、`Split` 排序——既是測試也是教材。
12. **每週自我測驗（quiz）**：notebook 末加 5 題選擇題 + 程式化對答案。
13. **英文版 notebooks**：i18n 第二語言軌，擴大受眾。
14. **`.ics` 行事曆匯出**：排程器把九個截止日匯出成 iCal。
15. **排程器智慧提示**：依保存的開始日 highlight 當前週；
    每週時數低於該週預估區間時提出警告。

### 基礎設施
16. **GitHub Pages 自動部署 + link checker**：`lychee` 離線查相對連結、
    排程查八個外部 OCW 連結的 rot（會直接抓到 P0-1 這類問題）。
17. **`generate_synthetic_dataset.py --verify`**：重新產生並 byte-compare
    committed CSV，CI 取得可重現性保證。
18. **Codecov 上傳 + coverage badge**：搭配 P1-9 的門檻。

---

## 建議執行順序

| 階段 | 內容 | 出貨判準 |
|------|------|----------|
| **第 1 批** | P0 全部（8 項） | 所有已實測 bug 修復 + regression tests；URL 全部指向真實 repo |
| **第 2 批** | P1-1～P1-9 | 覆蓋率 ≥ 80% 且 CI 設門檻；無「無法失敗」的斷言 |
| **第 3 批** | P2-1～P2-11 | CI matrix 綠燈；Pages 上線；pre-commit 與 CI 完全一致 |
| **第 4 批** | P3（HTML 與產生器重構） | solution notebooks 連結可用；`build_notebooks.py --check` 進 CI |
| **第 5 批** | P4 按教學價值排序逐項取捨 | 每項各自附 notebook 章節 + 測試 |

---

## 附註

- 所有相對連結（`docs/*.md`、`README*.md`）已程式化驗證可解析；
  cheatsheets 中引用的套件符號全部存在；`mathematical_notation.md` 與
  `glossary_zh_en.md` 未發現數學事實錯誤。
- kernel 名稱（`python3`）與 600 秒逾時設定在產生器、驗證腳本與 CI 之間
  目前是一致的——P2-7 統一機制時請保持。
- 本文件本身屬於工程文件，不影響課程內容；學習者請從
  [`roadmap.md`](roadmap.md) 開始。
