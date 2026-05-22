# 多變數微積分速查表 (Multivariable Calculus Cheatsheet)

本速查表服務於具備程式設計經驗、準備量化金融與系統化研究課程的學習者。內容皆為原創撰寫，不轉載任何課程教材。

---

## 1. 動機 (Motivation)

量化金融中的「最佳化」幾乎都是多變數問題：找出讓投資組合風險最小、或讓效用最大的權重向量。要理解最佳化器如何運作、何時會失敗，你需要 **gradient（梯度）**、**Hessian（黑塞矩陣）** 與 **Lagrange multipliers（拉格朗日乘數）**。

最具代表性的例子是 **minimum-variance portfolio（最小變異數投資組合）**：在「權重總和為 1」的等式限制下，最小化 $w^\top \Sigma w$。這正是「等式約束下的二次最佳化」，而它的解可以用一條閉式公式寫出來——前提是你懂多變數微積分。

---

## 2. 定義 (Definitions)

- **partial derivative（偏導數）** $\partial f/\partial x_i$：固定其他變數，只看 $f$ 對 $x_i$ 的變化率。
- **gradient（梯度）** $\nabla f$：所有偏導數組成的向量，指向函數上升最快的方向。
- **Hessian（黑塞矩陣）** $H$：二階偏導數構成的對稱矩陣，描述曲率。
- **Taylor approximation（泰勒近似）**：用多項式在某點附近近似一個函數。
- **convex function（凸函數）**：函數圖形「碗形朝上」，任意兩點連線都在圖形之上方；等價於 Hessian 處處 PSD。
- **Lagrange multiplier（拉格朗日乘數）** $\lambda$：把等式約束併入目標函數的輔助變數。
- **equality-constrained optimization（等式約束最佳化）**：在 $g(x)=0$ 之下求 $f(x)$ 的極值。

---

## 3. 核心公式 (Core equations)

二次函數 $f(w) = \tfrac12 w^\top A w + b^\top w + c$ 的梯度與 Hessian：

$$\nabla f(w) = A w + b, \qquad H = \nabla^2 f(w) = A$$

二階泰勒展開（在 $w_0$ 附近）：

$$f(w) \approx f(w_0) + \nabla f(w_0)^\top (w - w_0) + \tfrac12 (w - w_0)^\top H (w - w_0)$$

無約束極小值的一階條件 (first-order condition)：

$$\nabla f(w^\star) = 0$$

拉格朗日函數與最小變異數問題（限制 $\mathbf{1}^\top w = 1$）：

$$\mathcal{L}(w, \lambda) = w^\top \Sigma w - \lambda(\mathbf{1}^\top w - 1)$$

求偏導並令其為零，得到閉式解：

$$w^\star = \frac{\Sigma^{-1}\mathbf{1}}{\mathbf{1}^\top \Sigma^{-1}\mathbf{1}}$$

---

## 4. 直覺解釋 (Plain-language intuition)

把目標函數想成一片地形：梯度是「最陡上坡方向」，最佳化就是沿著下坡走到谷底。在谷底，地面是平的，所以梯度為零。

Hessian 描述谷底的形狀：若它 PSD（碗形朝上），這個零梯度點就是真正的最小值。**convexity（凸性）** 的好處在此——凸函數只有一個谷底，沒有騙人的局部極小值，最佳化器一定找得到全域解。$w^\top \Sigma w$ 因為 $\Sigma$ 是 PSD，所以是凸函數，這是組合最佳化能可靠求解的關鍵。

拉格朗日乘數的直覺：你不能走到地形的任何地方，只能待在「$\mathbf{1}^\top w = 1$」這條限制曲面上。最佳點是限制曲面上目標函數的等高線與曲面相切之處——此時目標函數的梯度與約束的梯度平行，比例係數就是 $\lambda$。

---

## 5. 一個小範例 (A small example)

兩檔資產，共變異數矩陣：

$$\Sigma = \begin{pmatrix} 0.04 & 0.00 \\ 0.00 & 0.09 \end{pmatrix}$$

（為簡化取零相關）。最小變異數權重：

$$\Sigma^{-1}\mathbf{1} = \begin{pmatrix} 25 \\ 11.11 \end{pmatrix}, \qquad \mathbf{1}^\top\Sigma^{-1}\mathbf{1} = 36.11$$

$$w^\star = \frac{1}{36.11}\begin{pmatrix} 25 \\ 11.11 \end{pmatrix} \approx \begin{pmatrix} 0.692 \\ 0.308 \end{pmatrix}$$

直覺正確：波動較低的資產（變異數 0.04）拿到較高權重。組合變異數 $w^{\star\top}\Sigma w^\star \approx 0.0277$，波動率 $\approx 16.6\%$，低於兩檔個別資產。

```python
import numpy as np
from quant_math_roadmap.math.optimization import (
    min_variance_weights, quadratic_gradient, quadratic_hessian,
)

Sigma = np.array([[0.04, 0.0], [0.0, 0.09]])
w = min_variance_weights(Sigma)          # ~[0.692, 0.308]
g = quadratic_gradient(w, Sigma)         # 在最佳點接近相等（受約束）
H = quadratic_hessian(Sigma)             # 等於 2*Sigma
```

---

## 6. 常見實作錯誤 (Typical implementation mistakes)

- **忘記 $\tfrac12$ 因子**：$\tfrac12 w^\top A w$ 的 Hessian 是 $A$，但 $w^\top A w$ 的 Hessian 是 $2A$；微分時係數要算對。
- **忽略約束**：直接對 $w^\top\Sigma w$ 求無約束最小值會得到 $w=0$（毫無意義）；必須加上 $\mathbf{1}^\top w = 1$。
- **誤判極值類型**：梯度為零只代表「臨界點」；要靠 Hessian 才知道是極小、極大還是鞍點 (saddle point)。
- **對奇異矩陣求逆**：$w^\star$ 公式需要 $\Sigma^{-1}$；若 $\Sigma$ 不可逆，閉式解失效，須先正則化。
- **泰勒近似用得太遠**：二階泰勒只在 $w_0$ 鄰近準確；遠離後誤差迅速放大。
- **未檢查凸性就信任最佳化結果**：若目標函數非凸，找到的可能只是局部解。

---

## 7. 完成度檢查清單 (Readiness checklist)

- [ ] 我能寫出二次函數的梯度與 Hessian。
- [ ] 我能解釋為何 $\Sigma$ 為 PSD 使組合最佳化問題為凸。
- [ ] 我能用拉格朗日乘數推導最小變異數權重的閉式解。
- [ ] 我能用一階條件 $\nabla f = 0$ 找臨界點，並用 Hessian 分類。
- [ ] 我理解凸性如何排除局部極小值的困擾。
- [ ] 我能用二階泰勒近似一個函數並說明其有效範圍。
- [ ] 我能用 `min_variance_weights` 驗證手算結果。

---

## 8. 延伸連結 (Links)

- 課程 notebook：[`notebooks/02_multivariable_calculus_and_min_variance_portfolio.ipynb`](../../notebooks/02_multivariable_calculus_and_min_variance_portfolio.ipynb)
- 可重用程式碼：`quant_math_roadmap.math.optimization`（`quadratic_gradient`、`quadratic_hessian`、`min_variance_weights`、`taylor_quadratic_approximation`）
- 官方學習資源：MIT OpenCourseWare 18.02SC Multivariable Calculus，<https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/>
