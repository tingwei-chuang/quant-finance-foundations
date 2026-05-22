# 時間序列速查表 (Time Series Cheatsheet)

本速查表服務於具備程式設計經驗、準備量化金融與系統化研究課程的學習者。內容皆為原創撰寫，不轉載任何課程教材。

---

## 1. 動機 (Motivation)

金融資料有一個其他資料沒有的特性：**時間順序**。觀測值不是可任意交換的獨立樣本，它們前後相依、依時間排列。忽視這一點，是量化研究中最常見、也最致命的錯誤來源。

時間序列分析教你：區分 **price series（價格序列）** 與 **return series（報酬序列）**、判斷一個序列是否 **stationary（定態）**、用 **autocorrelation（自相關）** 檢查可預測性、用 **AR(1)** 等模型描述動態，以及——最重要的——用 **walk-forward evaluation（前進式驗證）** 設計不會「偷看未來」的回測。隨機切分 train/test 在時間序列上是錯的，本表會解釋為什麼。

---

## 2. 定義 (Definitions)

- **price series（價格序列）**：資產價格隨時間的序列；通常非定態、有趨勢。
- **return series（報酬序列）**：價格的相對變化，$r_t = P_t/P_{t-1}-1$ 或 $\log(P_t/P_{t-1})$；通常較接近定態。
- **stationarity（定態性）**：序列的統計性質（均值、變異數、自相關）不隨時間改變。
- **autocorrelation（自相關）** $\rho_k$：序列與其自身落後 $k$ 期版本的相關係數。
- **ACF（autocorrelation function，自相關函數）**：$\rho_k$ 對所有落後階數 $k$ 的函數。
- **white noise（白噪音）**：均值為 0、變異數固定、各期不相關的序列；不可預測。
- **AR(1)（一階自迴歸）**：$x_t = c + \phi x_{t-1} + \varepsilon_t$。
- **walk-forward evaluation（前進式驗證）**：永遠用過去資料訓練、未來資料測試，並隨時間向前推進。

---

## 3. 核心公式 (Core equations)

對數報酬：

$$r_t = \ln P_t - \ln P_{t-1}$$

落後 $k$ 期的自相關：

$$\rho_k = \frac{\sum_{t=k+1}^{T}(x_t - \bar x)(x_{t-k} - \bar x)}{\sum_{t=1}^{T}(x_t - \bar x)^2}$$

AR(1) 模型：

$$x_t = c + \phi\,x_{t-1} + \varepsilon_t, \qquad \varepsilon_t \sim \text{white noise}$$

AR(1) 在 $|\phi|<1$（定態條件）下的長期均值與變異數：

$$\mathbb{E}[x_t] = \frac{c}{1-\phi}, \qquad \operatorname{Var}(x_t) = \frac{\sigma_\varepsilon^2}{1-\phi^2}$$

AR(1) 的自相關函數呈幾何衰減：

$$\rho_k = \phi^k$$

白噪音的 ACF（除 $k=0$ 外全為 0）：

$$\rho_0 = 1, \qquad \rho_k = 0 \;\; (k\neq 0)$$

---

## 4. 直覺解釋 (Plain-language intuition)

**為何要先轉成報酬**：價格會持續漂移，去年的價格水準與今年無從比較——非定態。報酬則大致圍繞一個穩定均值上下波動，統計工具才適用。

**定態性**的意思是「遊戲規則不隨時間改變」。若序列非定態，在前半段學到的規律到後半段可能完全失效，任何模型都站不住腳。

**ACF** 是可預測性的快速體檢。報酬序列的 ACF 若幾乎全部落在信賴帶內，它就接近白噪音——過去無法預測未來。$\phi$ 接近 1 的 AR(1) 高度持續（趨勢），$\phi$ 為負則代表均值回歸（mean reversion）。

**為何不能隨機切分 train/test**：隨機切分會把未來的觀測放進訓練集、過去的放進測試集，模型於是「看過了答案」。即使逐筆獨立、不顯式洩漏，特徵工程（移動平均、波動率）也會跨越切分邊界造成 **lookahead bias（前視偏誤）**。正確做法是 **walk-forward**：固定一個時間切點，只用切點之前訓練、之後測試，再讓切點向前滾動。如此回測出的績效，才反映「在當下、只憑當時可得資訊」能達成的結果。

---

## 5. 一個小範例 (A small example)

模擬一個 AR(1)：$x_t = 0 + 0.6\,x_{t-1} + \varepsilon_t$，$\varepsilon_t\sim\mathcal N(0, 1)$。

理論性質：長期均值 $c/(1-\phi)=0$；變異數 $1/(1-0.36)\approx1.563$；ACF 為 $\rho_1=0.6$、$\rho_2=0.36$、$\rho_3=0.216$——幾何衰減。

對照之下，真正的日報酬序列其 $\rho_1$ 通常很接近 0（接近白噪音），這也是為何「明天漲跌」如此難以預測。

train/test 設計：1000 個交易日，**不要**隨機抽 800 訓練 / 200 測試。正確做法是用前 800 日訓練、後 200 日測試；要更穩健就用 expanding window——先用 1–400 日訓練、預測第 401 日起一段；再用 1–500 日訓練……逐步向前推進。

```python
import numpy as np, pandas as pd
from quant_math_roadmap.time_series.diagnostics import (
    autocorrelation_function, adf_stationarity_test, rolling_volatility,
)
from quant_math_roadmap.time_series.forecasting import make_lag_features, fit_ar1
from quant_math_roadmap.time_series.splits import (
    train_test_split_time, expanding_window_splits,
)

rng = np.random.default_rng(0)
x = np.zeros(1000)
for t in range(1, 1000):
    x[t] = 0.6 * x[t - 1] + rng.standard_normal()
s = pd.Series(x)

print(autocorrelation_function(s, max_lag=5))   # ≈ 0.6, 0.36, 0.22, ...
print(adf_stationarity_test(s))                  # 定態檢定
model = fit_ar1(s)                               # 估計 phi ≈ 0.6
train, test = train_test_split_time(s, test_size=0.2)   # 依時間切分，不打亂
for tr, te in expanding_window_splits(s, n_splits=5):
    ...                                          # walk-forward 評估
```

---

## 6. 常見實作錯誤 (Typical implementation mistakes)

- **隨機 train/test split**：在時間序列上打亂順序會造成前視偏誤；務必依時間切分。
- **直接對價格建模**：價格非定態，應先轉成報酬（或先做差分）。
- **特徵跨越切分邊界**：移動平均、滾動波動率等若在切分前對整段資料計算，測試集會吸收未來資訊；特徵須在每個視窗內、僅用過去資料計算。
- **以同期變數預測**：用 $x_t$ 預測 $r_t$ 不是預測；預測必須用 $x_{t-1}$ 或更早的落後特徵。
- **誤把白噪音當訊號**：報酬 ACF 的小幅波動多在信賴帶內，屬雜訊；過度解讀會挖出假規律。
- **忽略非定態漂移**：波動率叢聚與結構轉變使「定態」只是近似；長視窗模型可能已失效。
- **未對齊落後特徵**：`shift` 方向錯誤會把未來值當成特徵，造成嚴重洩漏。

---

## 7. 完成度檢查清單 (Readiness checklist)

- [ ] 我能說明價格序列與報酬序列的差異，以及為何先轉成報酬。
- [ ] 我能定義定態性並用 `adf_stationarity_test` 檢驗。
- [ ] 我能計算並解讀 ACF，並辨認白噪音。
- [ ] 我能寫出 AR(1) 模型並說明 $\phi$ 的意義與定態條件。
- [ ] 我能解釋為何隨機 train/test split 不適用於時間序列。
- [ ] 我能用 `train_test_split_time` 與 `expanding_window_splits` 設計 walk-forward 評估。
- [ ] 我能正確建構落後特徵，避免前視偏誤。

---

## 8. 延伸連結 (Links)

- 課程 notebook：
  - [`notebooks/07_time_series_diagnostics.ipynb`](../../notebooks/07_time_series_diagnostics.ipynb)
  - [`notebooks/08_walk_forward_forecasting_and_backtesting_integrity.ipynb`](../../notebooks/08_walk_forward_forecasting_and_backtesting_integrity.ipynb)
- 可重用程式碼：`quant_math_roadmap.time_series.diagnostics`（`autocorrelation`、`autocorrelation_function`、`rolling_mean`、`rolling_volatility`、`adf_stationarity_test`）、`quant_math_roadmap.time_series.forecasting`（`make_lag_features`、`fit_ar1`）、`quant_math_roadmap.time_series.splits`（`train_test_split_time`、`expanding_window_splits`、`rolling_window_splits`）
- 官方學習資源：
  - Forecasting: Principles and Practice, the Pythonic Way，<https://otexts.com/fpppy/>
  - Penn State STAT 510 Applied Time Series Analysis，<https://online.stat.psu.edu/stat510/>
