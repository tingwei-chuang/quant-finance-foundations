# 線性代數速查表 (Linear Algebra Cheatsheet)

本速查表服務於具備程式設計經驗、準備量化金融與系統化研究課程的學習者。內容皆為原創撰寫，不轉載任何課程教材。

---

## 1. 動機 (Motivation)

在量化金融中，幾乎所有「多資產」的問題都是線性代數問題。一個投資組合不是單一數字，而是一個權重向量 (weight vector)；資產之間的共同波動由 **covariance matrix（共變異數矩陣）** 描述；投資組合風險是一個 **quadratic form（二次型）**；以歷史資料配適因子模型則是一個 **least squares（最小平方）** 問題。

掌握線性代數讓你能：

- 把「N 檔股票的組合風險」寫成一行 $w^\top \Sigma w$，而非 N 重迴圈。
- 用 **eigenvalues（特徵值）** 判斷一個估計出來的共變異數矩陣是否「物理上合理」（風險不可為負）。
- 理解 PCA、因子模型、風險平價等技術背後共用的同一套數學。

---

## 2. 定義 (Definitions)

- **向量 (vector)**：$w \in \mathbb{R}^N$，例如各資產的權重，$\sum_i w_i = 1$ 表示資金全數配置。
- **矩陣 (matrix)**：$A \in \mathbb{R}^{m\times n}$，把向量做線性變換。
- **共變異數矩陣 (covariance matrix)** $\Sigma$：$N\times N$ 對稱矩陣，$\Sigma_{ij} = \operatorname{Cov}(r_i, r_j)$，對角線為各資產變異數。
- **eigenvalue / eigenvector（特徵值／特徵向量）**：滿足 $A v = \lambda v$ 的純量 $\lambda$ 與非零向量 $v$。
- **positive semidefinite, PSD（半正定）**：對稱矩陣 $A$ 若對所有 $x$ 皆有 $x^\top A x \ge 0$，則稱 PSD；等價於所有特徵值 $\lambda_i \ge 0$。
- **quadratic form（二次型）**：純量函數 $q(x) = x^\top A x$。
- **least squares（最小平方）**：求 $\beta$ 使 $\lVert y - X\beta \rVert^2$ 最小。

---

## 3. 核心公式 (Core equations)

投資組合報酬與變異數（$\Sigma$ 為共變異數矩陣）：

$$r_p = w^\top r, \qquad \operatorname{Var}(r_p) = w^\top \Sigma w$$

特徵分解（spectral decomposition，對稱矩陣）：

$$\Sigma = Q \Lambda Q^\top, \qquad Q^\top Q = I, \quad \Lambda = \operatorname{diag}(\lambda_1,\dots,\lambda_N)$$

二次型用特徵值表示，令 $z = Q^\top x$：

$$x^\top \Sigma x = \sum_{i=1}^{N} \lambda_i z_i^2 \;\ge\; 0 \quad\Longleftrightarrow\quad \text{所有 } \lambda_i \ge 0$$

正規方程式 (normal equations) 與最小平方解：

$$X^\top X \,\hat\beta = X^\top y \quad\Longrightarrow\quad \hat\beta = (X^\top X)^{-1} X^\top y$$

共變異數矩陣的估計（$T$ 期報酬、$\bar r$ 為樣本均值）：

$$\hat\Sigma = \frac{1}{T-1} \sum_{t=1}^{T} (r_t - \bar r)(r_t - \bar r)^\top$$

---

## 4. 直覺解釋 (Plain-language intuition)

把矩陣想成「對空間做的操作」：旋轉、拉伸、壓扁。特徵向量是那些「方向不變、只被縮放」的特殊方向，特徵值就是縮放倍率。

對共變異數矩陣 $\Sigma$ 而言，最大特徵值對應的特徵向量是「市場一起漲跌」的主要方向（常解讀為市場因子）；很小或接近零的特徵值代表幾乎沒有獨立波動的方向。

二次型 $w^\top \Sigma w$ 就是投資組合變異數。它必須 $\ge 0$，因為變異數不可能是負的——這正是 $\Sigma$ 必須 PSD 的原因。若你估出的矩陣有負特徵值，數學會允許「負風險」這種荒謬結果，最佳化器會去鑽這個漏洞。

---

## 5. 一個小範例 (A small example)

兩檔資產，年化共變異數矩陣（變異數與共變異數，單位為 $\text{報酬}^2$）：

$$\Sigma = \begin{pmatrix} 0.04 & 0.012 \\ 0.012 & 0.09 \end{pmatrix}$$

各資產年化波動率為 $\sqrt{0.04}=20\%$ 與 $\sqrt{0.09}=30\%$，相關係數 $\rho = 0.012/(0.2\cdot0.3)=0.2$。

等權重組合 $w = (0.5, 0.5)$：

$$w^\top \Sigma w = 0.25(0.04) + 0.25(0.09) + 2(0.5)(0.5)(0.012) = 0.0385$$

組合波動率 $= \sqrt{0.0385} \approx 19.6\%$——低於兩檔個別資產，這就是分散化效果。

Python 對照：

```python
import numpy as np
from quant_math_roadmap.math.linear_algebra import (
    quadratic_form, is_positive_semidefinite, eigendecomposition,
)

Sigma = np.array([[0.04, 0.012], [0.012, 0.09]])
w = np.array([0.5, 0.5])
print(quadratic_form(w, Sigma))          # 0.0385
print(is_positive_semidefinite(Sigma))   # True
vals, vecs = eigendecomposition(Sigma)   # 特徵值皆 > 0
```

---

## 6. 常見實作錯誤 (Typical implementation mistakes)

- **維度不匹配**：把 $w^\top \Sigma w$ 寫成 `w @ Sigma @ w` 沒問題，但若 `w` 是 $(N,1)$ 而非 $(N,)$，結果會變成 $1\times1$ 矩陣而非純量。
- **混淆相關與共變異數矩陣**：相關矩陣對角線為 1，共變異數矩陣對角線為變異數；最佳化用的是共變異數矩陣。
- **使用非 PSD 的估計矩陣**：樣本數少於資產數時 $\hat\Sigma$ 必為奇異 (singular) 或含負特徵值；先用 `nearest_psd` 修正再交給最佳化器。
- **直接對 $X^\top X$ 求逆**：當特徵共線時 $X^\top X$ 病態 (ill-conditioned)；數值上應改用 `numpy.linalg.lstsq` 或 QR 分解（`ols_beta` 內部即採此法），而非 `inv`。
- **忘記中心化**：估計共變異數前未減去均值，會把均值資訊污染進變異數。
- **行列混淆**：報酬矩陣每一列是一個時間點、每一欄是一檔資產；轉置錯誤會算出完全不同的矩陣。

---

## 7. 完成度檢查清單 (Readiness checklist)

- [ ] 我能說明為何 $w^\top \Sigma w$ 必須非負，並連結到 PSD 性質。
- [ ] 我能手算 $2\times2$ 矩陣的特徵值與特徵向量。
- [ ] 我能解釋特徵分解 $\Sigma = Q\Lambda Q^\top$ 各項的意義。
- [ ] 我知道何時 $X^\top X$ 不可逆，以及應改用哪種數值方法。
- [ ] 我能用 `is_positive_semidefinite` 檢查並用 `nearest_psd` 修復共變異數矩陣。
- [ ] 我能由共變異數矩陣推回波動率與相關係數。
- [ ] 我能用 `quadratic_form` 算出任意權重下的組合變異數。

---

## 8. 延伸連結 (Links)

- 課程 notebook：[`notebooks/01_returns_covariance_and_linear_algebra.ipynb`](../../notebooks/01_returns_covariance_and_linear_algebra.ipynb)
- 可重用程式碼：`quant_math_roadmap.math.linear_algebra`（`quadratic_form`、`is_positive_semidefinite`、`eigendecomposition`、`nearest_psd`、`ols_beta`、`add_intercept`）
- 官方學習資源：MIT OpenCourseWare 18.06SC Linear Algebra，<https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/>
