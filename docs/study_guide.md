# 學習指南 / Study Guide

本指南把八週路線圖拆成可操作的每週計畫：**要學的概念**、**對應外部資源**、
**相關主題**、**要完成的 notebook 練習**、以及**就緒標準**。

> 概念路線總覽請見 [`roadmap.md`](roadmap.md)；資源連結請見
> [`resources.md`](resources.md)；數學概念筆記請見 `docs/math/` 與 `docs/finance/`。

## 每週建議節奏

每週約需 **8–12 小時**，建議分配如下：

1. **讀概念筆記**（`docs/math/` 或 `docs/finance/` 的對應 cheatsheet）。
2. **看／讀對應外部資源**（見每週的「外部資源」欄）。
3. **完成 notebook**：依序執行儲存格，動手填寫 TODO。
4. **解習題**：概念題、程式題、反思題。
5. **記錄錯誤**：把卡住或弄錯的地方寫進 [`progress_tracker.md`](progress_tracker.md)。
6. **通過就緒檢查清單**：誠實打勾。

---

## Week 0 — 環境設定與準備度診斷

| 項目 | 內容 |
|------|------|
| 概念 | 八大主題的自我評估 |
| 外部資源 | 無（環境設定週） |
| 相關主題 | uv 環境、`import quant_math_roadmap`、合成資料 |
| Notebook 練習 | `00_setup_and_readiness_diagnostic.ipynb`：自我評估清單、小概念題、小程式題、進度表 |
| 就緒標準 | 環境可運作；notebook 可從頭跑到尾；能列出自己最弱的 2–3 個主題 |

---

## Week 1 — 報酬、風險與線性代數

| 項目 | 內容 |
|------|------|
| 概念 | simple/log return、平均與波動度、共變異數與相關係數、共變異數矩陣、特徵值、PSD、quadratic form |
| 外部資源 | MIT 18.06SC（線性代數）；NTU 110S204（報酬與風險） |
| 相關主題 | 向量與矩陣、特徵分解、$\mathbf{w}^\top\Sigma\mathbf{w}$ |
| 概念筆記 | `docs/math/linear_algebra_cheatsheet.md`、`docs/finance/returns_and_risk.md` |
| Notebook 練習 | 產生相關資產價格、算報酬、算年化平均與波動度、算共變異數/相關矩陣、手算與函式算投組變異數、檢視特徵值 |
| 就緒標準 | 能正確算 simple/log return；能解釋 PSD；能計算投組變異數 |

---

## Week 2 — 多變數微積分與最小變異投資組合

| 項目 | 內容 |
|------|------|
| 概念 | 偏微分、梯度、Hessian、Taylor 近似、Lagrange multiplier、最小變異投資組合 |
| 外部資源 | MIT 18.02SC（多變數微積分）；NTU 110S204（投資組合） |
| 相關主題 | 約束最佳化、凸性、共變異數估計 |
| 概念筆記 | `docs/math/multivariable_calculus_cheatsheet.md`、`docs/finance/portfolio_construction.md` |
| Notebook 練習 | 算 quadratic 目標的梯度、實作最小變異投組、比較 equal-weight、比較 in-sample/out-of-sample 變異數、展示噪音造成的不穩定 |
| 就緒標準 | 能寫出 Lagrangian；能解釋為何 in-sample 低變異數不保證 out-of-sample |

---

## Week 3 — 機率複習：模擬、LLN 與 CLT

| 項目 | 內容 |
|------|------|
| 概念 | 隨機變數、常見分布、期望值與變異數、條件機率與 Bayes、LLN、CLT |
| 外部資源 | MIT 18.05（機率與統計） |
| 相關主題 | 模擬、抽樣不確定性 |
| 概念筆記 | `docs/math/probability_cheatsheet.md` |
| Notebook 練習 | 模擬各分布、由樣本估計動差、視覺化 LLN 收斂、視覺化 CLT 抽樣分布、連結到「估計平均策略報酬」 |
| 就緒標準 | 能用模擬區分 LLN 與 CLT；能解釋樣本平均本身的不確定性 |

---

## Week 4 — 策略報酬的統計推論

| 項目 | 內容 |
|------|------|
| 概念 | 估計量、bias/variance、標準誤、信賴區間、假設檢定、p-value 誤用、bootstrap、多重檢定 |
| 外部資源 | MIT 18.05；NTU 112S103（統計與計量導論） |
| 相關主題 | selection bias、統計顯著 vs 經濟顯著 |
| 概念筆記 | `docs/math/statistical_inference_cheatsheet.md` |
| Notebook 練習 | 估計平均報酬信賴區間、比較兩個合成策略、bootstrap 平均報酬、展示測試大量隨機策略造成的假陽性 |
| 就緒標準 | 能正確解讀 p-value；能說明多重檢定的危險 |

---

## Week 5 — 迴歸與因子模型

| 項目 | 內容 |
|------|------|
| 概念 | 簡單/多元迴歸、OLS 矩陣形式、截距/beta/殘差、R-squared、標準誤、heteroskedasticity、rolling beta |
| 外部資源 | NTU 112S103；MIT 18.06SC（OLS 作為投影） |
| 相關主題 | 因子曝險、omitted variable bias |
| 概念筆記 | `docs/math/regression_cheatsheet.md` |
| Notebook 練習 | 估計 CAPM beta、配適多因子模型、手刻 OLS 對照 statsmodels、rolling beta、檢視殘差、展示 omitted variable bias |
| 就緒標準 | 能推導 $\hat{\beta}=(X^\top X)^{-1}X^\top y$；能說明「係數 ≠ 訊號」 |

---

## Week 6 — 財務數學與選擇權定價

| 項目 | 內容 |
|------|------|
| 概念 | 貨幣時間價值、折現因子、現值、債券定價、forward/futures、call/put payoff、no-arbitrage、binomial tree |
| 外部資源 | NTU 110S204（財金基礎） |
| 相關主題 | 一期與多期 binomial、敏感度分析 |
| 概念筆記 | `docs/finance/discounting_and_bonds.md`、`docs/finance/derivatives_payoffs.md` |
| Notebook 練習 | 現值計算器、債券定價、payoff 圖、binomial 歐式 call 定價、對 strike/波動度/到期/利率做敏感度實驗 |
| 就緒標準 | 能用 binomial tree 為歐式選擇權定價並解釋每一步 |

---

## Week 7 — 時間序列診斷

| 項目 | 內容 |
|------|------|
| 概念 | 價格 vs 報酬序列、定態性、ACF、white noise、rolling 統計、波動度叢聚 |
| 外部資源 | FPP（otexts.com/fpppy）；STAT 510（選用） |
| 相關主題 | AR(1)、隨機切分為何不適用 |
| 概念筆記 | `docs/math/time_series_cheatsheet.md` |
| Notebook 練習 | 繪價格與報酬、ACF、rolling volatility、產生 AR(1)、比較定態與非定態序列 |
| 就緒標準 | 能解釋定態性；能說明隨機 train/test 切分為何錯誤 |

---

## Week 8 — 走動式預測與回測完整性

| 項目 | 內容 |
|------|------|
| 概念 | 時間式切分、expanding/rolling window、走動式預測、baseline、交易成本、turnover、look-ahead、leakage、survivorship bias |
| 外部資源 | FPP；STAT 510（選用） |
| 相關主題 | gross vs net、benchmark、策略失敗分析 |
| 概念筆記 | `docs/finance/evaluation_methodology.md`、`docs/common_backtesting_mistakes.md` |
| Notebook 練習 | 時間式切分、最小 AR 式預測器、與 naive baseline 比較、套用交易成本、比較 gross/net、刻意展示 leaked 模型並說明其無效 |
| 就緒標準 | 能完成一個無 leakage、含成本、可重現的小型回測流程 |

---

## English summary

This study guide turns each roadmap week into an actionable plan: the concepts
to learn, the matching official resource, related topics, the notebook
exercises to complete, and explicit readiness criteria. The suggested weekly
rhythm is: read the concept note → study the linked resource → work the
notebook → solve the exercises → log mistakes in the progress tracker → pass
the readiness checklist. Budget roughly 8–12 hours per week.
