# 數學符號參考表 (Mathematical Notation Reference)

本文件整理本倉庫各週筆記、程式碼與測試中使用的數學符號慣例。
目標讀者為具備程式設計經驗、準備量化金融與系統化研究課程的學習者。
此處的符號約定刻意與課程程式碼 (`src/quant_math_roadmap`) 保持一致,
讓讀者能在「白板上的公式」與「Python 實作」之間無縫對照。

> 教育與研究方法用途。本文件僅說明符號慣例,不構成任何投資建議。

慣例摘要:純量以斜體小寫表示 ($x$),向量以**粗體小寫**表示 ($\mathbf{x}$),
矩陣以**粗體大寫**表示 ($\mathbf{X}$)。下標通常表示時間或元素索引,
上標 $\top$ 表示轉置。估計量 (estimator) 一律加上 hat 符號 (例如 $\hat{\mu}$)。

---

## 1. 一般符號 (General Symbols)

| 符號 (Symbol) | 意義 (Meaning) | 備註 (Notes) |
|---|---|---|
| $x,\ y,\ \alpha$ | 純量 (scalar) | 斜體小寫;希臘字母常用於參數 |
| $\mathbf{x},\ \mathbf{w}$ | 向量 (vector) | 粗體小寫,預設為行向量 (column vector) |
| $\mathbf{X},\ \mathbf{\Sigma}$ | 矩陣 (matrix) | 粗體大寫 |
| $x_i$ | 向量第 $i$ 個元素 | 索引從 1 起算 (數學);程式碼從 0 起算 |
| $X_{ij}$ | 矩陣第 $i$ 列第 $j$ 行元素 | 列在前、行在後 |
| $\mathbf{x}^{\top},\ \mathbf{X}^{\top}$ | 轉置 (transpose) | 行列互換 |
| $\mathbf{X}^{-1}$ | 反矩陣 (inverse) | 僅對非奇異方陣存在 |
| $\sum_{i=1}^{n} x_i$ | 對 $i=1$ 到 $n$ 求和 | 索引範圍標於上下 |
| $\prod_{t=1}^{T}(1+r_t)$ | 連乘 (product) | 報酬複利常用 |
| $n,\ T$ | 樣本數 / 時間長度 | $n$ 多指觀測數,$T$ 多指期數 |
| $\mathbb{R},\ \mathbb{R}^{n}$ | 實數集 / $n$ 維實向量空間 | |
| $\triangleq,\ :=$ | 定義為 | 引入新符號時使用 |
| $\approx$ | 近似等於 | |

---

## 2. 價格與報酬 (Prices & Returns)

| 符號 (Symbol) | 意義 (Meaning) | 備註 (Notes) |
|---|---|---|
| $P_t$ | 第 $t$ 期資產價格 (price) | 期末收盤價 |
| $r_t$ | 第 $t$ 期簡單報酬 (simple return) | $r_t = \dfrac{P_t - P_{t-1}}{P_{t-1}}$ |
| $R_t$ | 第 $t$ 期毛報酬 (gross return) | $R_t = 1 + r_t = \dfrac{P_t}{P_{t-1}}$ |
| $\ell_t$ | 第 $t$ 期對數報酬 (log return) | $\ell_t = \ln R_t = \ln\dfrac{P_t}{P_{t-1}}$ |
| $\sum_t \ell_t$ | 多期對數報酬 | 對數報酬可直接相加 |
| $\prod_t R_t$ | 多期累積毛報酬 | 簡單報酬須以連乘複利 |
| $r_f$ | 無風險利率 (risk-free rate) | 用於超額報酬與 Sharpe 比率 |
| $V_t$ | 投組權益曲線 (equity curve) | 參見 `backtesting.baselines` |

備註:對數報酬與簡單報酬在小幅變動下近似相等 ($\ell_t \approx r_t$),
但加總性質不同。本倉庫於 `finance.returns` 明確區分兩者。

---

## 3. 統計與機率 (Statistics & Probability)

| 符號 (Symbol) | 意義 (Meaning) | 備註 (Notes) |
|---|---|---|
| $\mathbb{E}[X]$ | 期望值 (expectation) | 母體層級的平均 |
| $\operatorname{Var}(X)$ | 變異數 (variance) | $\operatorname{Var}(X)=\mathbb{E}[(X-\mu)^2]$ |
| $\operatorname{Cov}(X,Y)$ | 共變異數 (covariance) | 衡量同向變動程度 |
| $\sigma$ | 標準差 / 波動率 (volatility) | $\sigma=\sqrt{\operatorname{Var}(X)}$ |
| $\sigma^2$ | 變異數 | |
| $\rho$ | 相關係數 (correlation) | $\rho_{XY}=\dfrac{\operatorname{Cov}(X,Y)}{\sigma_X \sigma_Y}\in[-1,1]$ |
| $\mu$ | 母體平均 (population mean) | $\mu=\mathbb{E}[X]$ |
| $\bar{x}$ | 樣本平均 (sample mean) | $\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i$ |
| $s,\ s^2$ | 樣本標準差 / 樣本變異數 | 通常使用 $n-1$ 自由度 |
| $\hat{\theta}$ | 參數 $\theta$ 的估計量 (estimator) | hat 表示「由資料估計」 |
| $\hat{\mu},\ \hat{\sigma}$ | 平均 / 波動率的估計量 | 與母體量 $\mu,\sigma$ 區分 |
| $X \sim \mathcal{D}$ | $X$ 服從分配 $\mathcal{D}$ | $\sim$ 讀作「distributed as」 |
| $\mathcal{N}(\mu,\sigma^2)$ | 常態分配 (normal distribution) | 參數為平均與變異數 |
| $\operatorname{SE}(\hat{\theta})$ | 估計量的標準誤 (standard error) | 估計量本身的標準差 |
| $H_0,\ H_1$ | 虛無假設 / 對立假設 | 假設檢定用 |
| $p$ | p 值 (p-value) | 參見 `math.statistics.one_sample_ttest` |
| $\alpha$ | 顯著水準 (significance level) | 例如 $0.05$ |

---

## 4. 線性代數 (Linear Algebra)

| 符號 (Symbol) | 意義 (Meaning) | 備註 (Notes) |
|---|---|---|
| $\mathbf{\Sigma}$ | 共變異數矩陣 (covariance matrix) | 對稱、半正定 (PSD) |
| $\mathbf{w}$ | 權重向量 (weight vector) | 投組配置;常要求 $\mathbf{1}^{\top}\mathbf{w}=1$ |
| $\mathbf{1}$ | 全為 1 的向量 (vector of ones) | 用於加總約束 |
| $\mathbf{I}$ | 單位矩陣 (identity matrix) | |
| $\mathbf{w}^{\top}\mathbf{\Sigma}\,\mathbf{w}$ | 二次型 (quadratic form) | 投組變異數;PSD 保證 $\geq 0$ |
| $\lambda$ | 特徵值 (eigenvalue) | $\mathbf{A}\mathbf{v}=\lambda\mathbf{v}$ |
| $\mathbf{v}$ | 特徵向量 (eigenvector) | |
| $\mathbf{X}$ | 設計矩陣 (design matrix) | 列為觀測、行為特徵 |
| $\boldsymbol{\beta}$ | 迴歸係數向量 (coefficient vector) | 參見 `math.statistics.ols_fit` |
| $\|\mathbf{x}\|$ | 向量範數 (norm) | 預設為 $L^2$ 範數 |
| $\mathbf{x}^{\top}\mathbf{y}$ | 內積 (dot product) | $\sum_i x_i y_i$ |
| $\operatorname{tr}(\mathbf{A})$ | 跡 (trace) | 對角元素之和 |

備註:任何合法的共變異數矩陣必為半正定,因此 $\mathbf{w}^{\top}\mathbf{\Sigma}\,\mathbf{w}\geq 0$
對所有 $\mathbf{w}$ 成立 — 投組變異數不可能為負。

---

## 5. 微積分與最佳化 (Calculus & Optimization)

| 符號 (Symbol) | 意義 (Meaning) | 備註 (Notes) |
|---|---|---|
| $\dfrac{df}{dx}$ | 一階導數 | 單變數 |
| $\dfrac{\partial f}{\partial x_i}$ | 偏導數 (partial derivative) | 固定其他變數 |
| $\nabla f$ | 梯度 (gradient) | 偏導數組成的向量 |
| $\mathbf{H},\ \nabla^2 f$ | Hessian 矩陣 | 二階偏導數構成 |
| $\arg\min_{\mathbf{w}} f(\mathbf{w})$ | 使 $f$ 最小的 $\mathbf{w}$ | |
| $\text{s.t.}$ | 受限於 (subject to) | 標示最佳化約束條件 |
| $\lambda,\ \boldsymbol{\lambda}$ | Lagrange 乘子 (multiplier) | 每個等式約束對應一個乘子 |
| $\mathcal{L}$ | Lagrangian 函數 | $\mathcal{L}=f+\boldsymbol{\lambda}^{\top}\mathbf{g}$ |
| $\eta$ | 學習率 / 步長 (step size) | 梯度下降用 |

備註:同一字母 $\lambda$ 在不同章節分別代表特徵值與 Lagrange 乘子;
請以上下文判讀。本倉庫 `math.optimization` 以最小變異投組示範 Lagrange 法。

---

## 6. 時間序列 (Time Series)

| 符號 (Symbol) | 意義 (Meaning) | 備註 (Notes) |
|---|---|---|
| $x_t$ | 第 $t$ 期觀測值 | $t$ 為時間索引 |
| $L$ | 落後算子 (lag operator) | $L\,x_t = x_{t-1}$ |
| $\phi$ | AR 係數 (autoregressive coefficient) | $|\phi|<1$ 為定態必要條件 |
| $\text{AR}(1)$ | 一階自迴歸 | $x_t = \phi\,x_{t-1} + \varepsilon_t$ |
| $\varepsilon_t$ | 白噪音 (white noise) | 平均為 0、無自相關 |
| $\gamma_k$ | 落後 $k$ 期自共變異數 | |
| $\text{ACF}(k),\ \rho_k$ | 自相關函數 (autocorrelation) | $\rho_k=\gamma_k/\gamma_0$ |
| $\Delta x_t$ | 一階差分 | $\Delta x_t = x_t - x_{t-1}$ |

備註:`time_series.splits` 的所有切分皆尊重時間箭頭,
訓練區間恆早於對應的測試區間。

---

## 7. 金融 (Finance)

| 符號 (Symbol) | 意義 (Meaning) | 備註 (Notes) |
|---|---|---|
| $\text{DF}(t)$ | 折現因子 (discount factor) | $\text{DF}(t)=(1+y)^{-t}$ |
| $\text{PV}$ | 現值 (present value) | 未來現金流折現後之和 |
| $y$ | 殖利率 / 折現率 (yield) | 參見 `finance.fixed_income` |
| $C_t$ | 第 $t$ 期現金流 (cash flow) | |
| $S,\ S_t$ | 標的現貨價格 (spot price) | 衍生品定價用 |
| $K$ | 履約價 (strike price) | 選擇權合約參數 |
| $\tau,\ T$ | 到期時間 (time to maturity) | |
| 買權 payoff | $\max(S_T-K,\ 0)$ | call option 到期收益 |
| 賣權 payoff | $\max(K-S_T,\ 0)$ | put option 到期收益 |
| $\text{SR}$ | Sharpe 比率 (Sharpe ratio) | $\text{SR}=\dfrac{\bar{r}-r_f}{\sigma}$ |
| $\text{MDD}$ | 最大回撤 (maximum drawdown) | 權益曲線最深跌幅 |

備註:衍生品定價以無套利 (no-arbitrage) 為核心原則;
本倉庫 `finance.derivatives` 以二項樹示範 put-call parity。
