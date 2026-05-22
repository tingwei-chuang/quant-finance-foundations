# 迴歸分析速查表 (Regression Cheatsheet)

本速查表服務於具備程式設計經驗、準備量化金融與系統化研究課程的學習者。內容皆為原創撰寫，不轉載任何課程教材。

---

## 1. 動機 (Motivation)

迴歸是量化金融中最常用的工具，沒有之一。**factor model（因子模型）** 用迴歸把資產報酬分解成市場、規模、價值等系統性來源；**market beta（市場貝它）** 是一個迴歸係數；對沖比率、風險歸因、估計風險敞口——全部都是迴歸。

理解 **OLS（Ordinary Least Squares，普通最小平方法）** 不只是「會呼叫 `fit()`」。你需要知道它的矩陣形式、它作為一個 **projection（投影）** 的幾何意義、係數的標準誤差何時不可信，以及一個關鍵觀念：**迴歸係數本身並不是可交易的訊號**。

---

## 2. 定義 (Definitions)

- **simple linear regression（簡單線性迴歸）**：單一解釋變數，$y = \alpha + \beta x + \varepsilon$。
- **multiple regression（多元迴歸）**：多個解釋變數，$y = X\beta + \varepsilon$。
- **intercept / alpha（截距）** $\alpha$：所有解釋變數為 0 時的預期 $y$；在因子模型中常解讀為超額報酬。
- **slope / beta（斜率）** $\beta$：解釋變數每增加一單位，$y$ 的預期變化。
- **residual（殘差）** $e = y - \hat y$：模型未能解釋的部分。
- **$R^2$（判定係數）**：被模型解釋的變異比例。
- **heteroskedasticity（異質變異）**：殘差變異數隨解釋變數而改變。
- **rolling beta（滾動貝它）**：在移動視窗上重複估計的 $\beta$，用以觀察其時變性。

---

## 3. 核心公式 (Core equations)

簡單線性迴歸模型：

$$y_i = \alpha + \beta x_i + \varepsilon_i$$

簡單迴歸的閉式解：

$$\hat\beta = \frac{\operatorname{Cov}(x,y)}{\operatorname{Var}(x)}, \qquad \hat\alpha = \bar y - \hat\beta\,\bar x$$

OLS 的矩陣形式（$X$ 含一欄常數 1 代表截距）：

$$\boxed{\;\hat\beta = (X^\top X)^{-1} X^\top y\;}$$

擬合值與投影：$\hat y = X\hat\beta = Hy$，其中 hat 矩陣 $H = X(X^\top X)^{-1}X^\top$。

$R^2$（$\text{SS}$ 為平方和，total / residual）：

$$R^2 = 1 - \frac{\text{SS}_{\text{res}}}{\text{SS}_{\text{tot}}} = 1 - \frac{\sum e_i^2}{\sum (y_i - \bar y)^2}$$

同方差假設下係數的共變異數矩陣：

$$\widehat{\operatorname{Var}}(\hat\beta) = \hat\sigma^2 (X^\top X)^{-1}, \qquad \hat\sigma^2 = \frac{\sum e_i^2}{n - k}$$

---

## 4. 直覺解釋 (Plain-language intuition)

把 OLS 想成 **投影**：你的目標向量 $y$ 活在 $n$ 維空間中，而解釋變數張成一個低維子空間。OLS 找的就是子空間中「離 $y$ 最近」的那個點 $\hat y$。殘差 $e = y - \hat y$ 垂直於該子空間——這正是「正規方程式 $X^\top e = 0$」的幾何意義：殘差與每個解釋變數都不相關。

**market beta** 的金融意義：把某資產報酬對市場報酬迴歸，斜率 $\beta$ 衡量該資產相對市場的敏感度。$\beta=1.3$ 表示市場漲 1% 時，該資產平均漲 1.3%；$\beta$ 也是系統性風險敞口的度量。

**$R^2$** 是「模型解釋了多少變異」。但高 $R^2$ 不代表模型有用於預測，更不代表能賺錢。

**最關鍵的觀念**：迴歸告訴你的是「同期的關聯」（contemporaneous association），不是「未來的可預測性」。把某資產對市場的 $\beta$ 算出來，並不會給你一個進出場訊號。**迴歸係數不會自動成為可交易訊號**——要拿來預測，必須讓解釋變數嚴格早於被解釋變數（lagged features），並用 walk-forward 方式驗證。

---

## 5. 一個小範例 (A small example)

某股票與市場的 5 個月超額報酬（%）：

| 月 | 市場 $x$ | 股票 $y$ |
|----|---------|---------|
| 1  | 2.0     | 3.0     |
| 2  | -1.0    | -1.5    |
| 3  | 1.0     | 2.0     |
| 4  | -2.0    | -2.5    |
| 5  | 0.0     | 1.0     |

$\bar x = 0$，$\bar y = 0.4$。$\operatorname{Cov}(x,y) = \tfrac{1}{4}\sum (x_i-\bar x)(y_i-\bar y)$：

$$\sum (x_i)(y_i - 0.4) = 2(2.6) + (-1)(-1.9) + 1(1.6) + (-2)(-2.9) + 0 = 13.9$$
$$\operatorname{Cov}(x,y) = 13.9/4 = 3.475, \qquad \operatorname{Var}(x) = 10/4 = 2.5$$

$$\hat\beta = 3.475 / 2.5 = 1.39, \qquad \hat\alpha = 0.4 - 1.39\cdot 0 = 0.4$$

該股票 $\beta\approx1.39$（比市場波動大），月 $\alpha\approx0.4\%$。但樣本僅 5 筆，$\alpha$ 的標準誤差會很大——它的統計顯著性需另行檢定，且即使顯著也不等於未來可獲利。

```python
import numpy as np
from quant_math_roadmap.math.linear_algebra import ols_beta, add_intercept
from quant_math_roadmap.math.statistics import ols_fit

x = np.array([2.0, -1.0, 1.0, -2.0, 0.0])
y = np.array([3.0, -1.5, 2.0, -2.5, 1.0])
X = add_intercept(x.reshape(-1, 1))
beta = ols_beta(X, y)            # [alpha, beta] ≈ [0.4, 1.39]
result = ols_fit(X, y)           # 含係數、標準誤差、R^2
```

---

## 6. 常見實作錯誤 (Typical implementation mistakes)

- **忘記加截距欄**：少了常數欄，模型被迫通過原點，$\beta$ 估計偏誤。
- **把同期迴歸當預測模型**：用「今天的市場報酬」解釋「今天的股票報酬」毫無預測力；預測必須用 lagged features。
- **無視 heteroskedasticity 與自相關**：金融殘差幾乎總是異質變異且自相關，樸素標準誤差會低估，t 值灌水；應改用 robust（HAC / White）標準誤差。
- **誤判 $R^2$**：高 $R^2$ 不等於可獲利；過擬合的模型樣本內 $R^2$ 很高、樣本外崩潰。
- **多重共線性**：解釋變數高度相關時 $X^\top X$ 病態，個別係數不穩定且不可解讀。
- **直接對 $X^\top X$ 求逆**：數值上應用 QR 或 `lstsq`（`ols_beta` 內部即如此），避免病態矩陣放大誤差。
- **把係數當訊號**：估出 $\beta$ 後直接拿去下單——係數是描述性的，不是經過樣本外驗證的交易訊號。

---

## 7. 完成度檢查清單 (Readiness checklist)

- [ ] 我能寫出 OLS 的矩陣解 $\hat\beta = (X^\top X)^{-1}X^\top y$ 並說明每一項。
- [ ] 我能解釋 OLS 作為投影的幾何意義，以及殘差為何與解釋變數正交。
- [ ] 我能說明 market beta 的金融意義。
- [ ] 我知道 heteroskedasticity 與自相關如何影響標準誤差，以及如何校正。
- [ ] 我能正確解讀 $R^2$，並知道它不保證可獲利。
- [ ] 我能用滾動視窗估計 rolling beta 並解讀其時變性。
- [ ] 我清楚迴歸係數不是可直接交易的訊號，並知道把它轉成預測需要哪些前提。

---

## 8. 延伸連結 (Links)

- 課程 notebook：[`notebooks/05_regression_and_factor_models.ipynb`](../../notebooks/05_regression_and_factor_models.ipynb)
- 可重用程式碼：`quant_math_roadmap.math.linear_algebra`（`ols_beta`、`add_intercept`）、`quant_math_roadmap.math.statistics`（`ols_fit`）
- 官方學習資源：國立臺灣大學開放式課程 統計學一上與計量導論，<https://ocw.aca.ntu.edu.tw/courses/112S103>
