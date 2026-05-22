# 八週路線圖 / The 8-Week Roadmap

本文件詳述本專案的八週學習路線圖（外加 Week 0 診斷週）。

> **適用對象**：具備程式設計與基礎機器學習經驗、且過去學過微積分、線性代數與
> 機率，但需要重新複習並建立更紮實統計、迴歸、財務數學、投資組合、時間序列與
> 回測方法論基礎的學習者。
>
> **本路線圖不是**：投資建議、可獲利策略、進階數理金融教科書。

---

## 設計原則

本路線圖貫徹以下教學原則（詳見 README 與各 notebook）：

1. **先理解，再複雜化**（Understanding before complexity）。
2. **先應用統計推理，再進階數理金融**。
3. **先正確評估，再精緻模型**（Correct evaluation before sophisticated models）。
4. **先可重現，再談績效宣稱**（Reproducibility before performance claims）。
5. **先明示假設，再計算年化指標**。
6. **先排除 leakage，再討論任何結果**。
7. **先簡單 baseline，再預測型策略**。
8. **先教學清晰，再不必要的抽象**。

---

## 總覽表

| 週次 | 主題 | 核心數學 / 方法 | Notebook | 主要外部資源 |
|------|------|------------------|----------|---------------|
| 0 | 環境設定與準備度診斷 | 自我評估 | `00_setup_and_readiness_diagnostic.ipynb` | — |
| 1 | 報酬、風險與線性代數 | 共變異數矩陣、特徵值、quadratic form | `01_returns_covariance_and_linear_algebra.ipynb` | MIT 18.06SC |
| 2 | 多變數微積分與最小變異投資組合 | 梯度、Hessian、Lagrange multiplier | `02_multivariable_calculus_and_min_variance_portfolio.ipynb` | MIT 18.02SC |
| 3 | 機率複習：模擬、LLN 與 CLT | 隨機變數、LLN、CLT | `03_probability_simulation_lln_clt.ipynb` | MIT 18.05 |
| 4 | 策略報酬的統計推論 | 標準誤、信賴區間、bootstrap、多重檢定 | `04_statistical_inference_for_strategy_returns.ipynb` | MIT 18.05、NTU 112S103 |
| 5 | 迴歸與因子模型 | OLS、矩陣形式、rolling beta | `05_regression_and_factor_models.ipynb` | NTU 112S103 |
| 6 | 財務數學與選擇權定價 | 折現、債券、binomial tree | `06_financial_mathematics_and_option_pricing.ipynb` | NTU 110S204 |
| 7 | 時間序列診斷 | 定態性、ACF、AR(1)、rolling 統計 | `07_time_series_diagnostics.ipynb` | FPP、STAT 510 |
| 8 | 走動式預測與回測完整性 | 時間切分、leakage、交易成本 | `08_walk_forward_forecasting_and_backtesting_integrity.ipynb` | FPP、STAT 510 |

外部資源完整清單與連結請見 [`resources.md`](resources.md)。

---

## Week 0 — 環境設定與準備度診斷

**目標**：確認 Python 環境可運作、產生（或載入）合成價格資料、診斷自己在八個
主題上的熟悉度。

**交付成果**：
- 完成 `notebooks/00_setup_and_readiness_diagnostic.ipynb`。
- 一份「依弱項排序的建議學習路徑」。
- 一個可編輯的個人進度表（見 [`progress_tracker.md`](progress_tracker.md)）。

**就緒標準**：能成功 `import quant_math_roadmap`、能執行 notebook 到底、能誠實
標出自己最不熟悉的 2–3 個主題。

---

## Week 1 — 報酬、風險與線性代數

**概念**：simple return、log return、複利報酬、平均與波動度、共變異數與相關係數、
多資產報酬的矩陣表示、共變異數矩陣、特徵值與特徵向量、positive semidefinite (PSD)、
quadratic form。

**核心數學**：
- $r_t = (P_t - P_{t-1}) / P_{t-1}$；log return $= \ln(P_t / P_{t-1})$。
- 投資組合變異數 $= \mathbf{w}^\top \Sigma \mathbf{w}$。
- 共變異數矩陣為何必須是 PSD。

**交付成果**：完成 Notebook 01；通過 `tests/test_returns.py` 與
`tests/test_portfolio.py` 的相關概念；完成至少 3 題概念題、2 題程式題、1 題反思題。

**就緒標準**：能正確計算 simple/log return、能手算與用函式計算
$\mathbf{w}^\top\Sigma\mathbf{w}$、能解釋特徵值與 PSD 的意義。

---

## Week 2 — 多變數微積分與最小變異投資組合

**概念**：偏微分、梯度、Hessian、Taylor 近似、Lagrange multiplier、等式約束最佳化、
最小變異投資組合。

**核心數學**：
- 目標：minimize $\mathbf{w}^\top\Sigma\mathbf{w}$ subject to $\mathbf{1}^\top\mathbf{w}=1$。
- 封閉解 $\mathbf{w}^\* = \dfrac{\Sigma^{-1}\mathbf{1}}{\mathbf{1}^\top\Sigma^{-1}\mathbf{1}}$。
- 凸性的直覺、共變異數估計品質為何重要。

**交付成果**：完成 Notebook 02；實作最小變異投資組合並比較 equal-weight；
展示噪音共變異數造成的權重不穩定；（選用）展示 shrinkage 估計。

**就緒標準**：能寫出並解釋 Lagrangian、能說明為何 in-sample 變異數低不代表
out-of-sample 也低。

---

## Week 3 — 機率複習：模擬、LLN 與 CLT

**概念**：隨機變數、Bernoulli/Binomial/Normal/Exponential、期望值與變異數、共變異數、
條件機率與 Bayes 規則、大數法則 (LLN)、中央極限定理 (CLT)、抽樣不確定性。

**交付成果**：完成 Notebook 03；以模擬視覺化 LLN 收斂與 CLT 的抽樣分布；
把抽樣不確定性連結到「估計平均策略報酬」這件事。

**就緒標準**：能用模擬說明 LLN 與 CLT 的差別、能解釋為什麼樣本平均本身有
不確定性。

---

## Week 4 — 策略報酬的統計推論

**概念**：樣本與估計量、bias 與 variance、標準誤、信賴區間、假設檢定、
p-value 及其誤用、bootstrap 信賴區間、策略研究中的多重檢定警訊。

**教學重點**：
- 漂亮的權益曲線不能證明策略有效。
- 統計顯著 ≠ 經濟顯著。
- 反覆搜尋策略會造成 selection bias。

**交付成果**：完成 Notebook 04；估計平均報酬的信賴區間、bootstrap 平均報酬、
展示「測試大量隨機策略」如何產生假陽性。

**就緒標準**：能正確解讀 p-value、能說明多重檢定為何危險。

---

## Week 5 — 迴歸與因子模型

**概念**：簡單與多元線性迴歸、OLS 的矩陣形式、截距/beta/殘差、R-squared、標準誤、
heteroskedasticity、rolling beta、因子曝險。

**核心數學**：$\hat{\boldsymbol{\beta}} = (X^\top X)^{-1} X^\top \mathbf{y}$；
OLS 作為線性代數的投影；市場 beta 的財務意義。

**交付成果**：完成 Notebook 05；估計 CAPM 式 beta、配適多因子模型、
手刻 OLS 與 `statsmodels` 對照、計算 rolling beta、檢視殘差。

**就緒標準**：能推導 OLS 矩陣解、能說明「迴歸係數不等於可交易訊號」。

---

## Week 6 — 財務數學與選擇權定價

**概念**：貨幣時間價值、折現因子、現值、債券現金流與定價、forward/futures 直覺、
call/put payoff、no-arbitrage 直覺、一期與多期 binomial tree、用 binomial model
為歐式選擇權定價。

**刻意排除**：stochastic calculus、Black-Scholes 推導、宣稱模型價格貼近真實市場。

**交付成果**：完成 Notebook 06；現值計算器、債券定價、payoff 圖、binomial 歐式
call 定價、對 strike/波動度/到期/利率做敏感度實驗。

**就緒標準**：能用 binomial tree 為歐式選擇權定價並解釋每一步。

---

## Week 7 — 時間序列診斷

**概念**：價格 vs 報酬序列、趨勢與非定態、定態性直覺、落後關係、autocorrelation
function (ACF)、white noise、rolling mean/volatility、波動度叢聚、為何隨機切分
不適用於時間性預測。

**交付成果**：完成 Notebook 07；繪製價格與報酬、ACF、rolling volatility、
產生 AR(1) 過程、比較定態與非定態序列。

**就緒標準**：能解釋定態性、能說明隨機 train/test 切分為何錯誤。

---

## Week 8 — 走動式預測與回測完整性

**概念**：時間式切分、expanding vs rolling window、走動式預測、預測 baseline、
交易成本、turnover、look-ahead bias、data leakage、survivorship bias（概念警示）、
benchmark 選擇、策略失敗分析。

**交付成果**：完成 Notebook 08；實作時間式 train/test 切分、最小 AR 式預測器、
與 naive baseline 比較、套用交易成本、比較 gross vs net、刻意展示一個 leaked
模型並說明為何其結果無效。

**就緒標準**：能從頭到尾跑出一個無 leakage、含成本、可重現的小型回測流程，
並誠實說明它「不是可投資策略」。

---

## 完課後的下一步

完成八週後，學習者應能自信地進入：
- 應用量化金融、系統化量化研究專案；
- 財務演算法課程；
- 計量經濟 / 時間序列課程。

關於「證明導向最佳化課程」的準備度，請見 [`progress_tracker.md`](progress_tracker.md)
的明確說明：本路線圖只提供初步診斷，**不取代**正式的證明訓練。

---

## English summary

This roadmap spans a Week 0 readiness diagnostic plus eight themed weeks:
(1) returns, risk & linear algebra; (2) multivariable calculus & the
minimum-variance portfolio; (3) a probability refresh with LLN/CLT;
(4) statistical inference for strategy returns; (5) regression & factor models;
(6) financial mathematics & binomial option pricing; (7) time-series
diagnostics; (8) walk-forward forecasting & backtesting integrity. Each week
pairs original concept notes, a runnable notebook, exercises, and a readiness
checklist. It is an educational methodology course — not investment advice and
not a claim of any profitable strategy.
