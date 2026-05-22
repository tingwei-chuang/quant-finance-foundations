# 機率速查表 (Probability Cheatsheet)

本速查表服務於具備程式設計經驗、準備量化金融與系統化研究課程的學習者。內容皆為原創撰寫，不轉載任何課程教材。

---

## 1. 動機 (Motivation)

市場報酬本質上是隨機的。任何交易策略的績效都是一個 **random variable（隨機變數）** 的實現值——你看到的回測夏普比率，只是「在許多可能的歷史中」抽到的一個樣本。

機率提供描述不確定性的語言：用 **expectation（期望值）** 描述「平均會發生什麼」、用 **variance（變異數）** 描述「波動有多大」、用 **distribution（分布）** 描述「各種結果的可能性」。而 **Law of Large Numbers, LLN（大數法則）** 與 **Central Limit Theorem, CLT（中央極限定理）** 是後續所有統計推論的地基：它們告訴你樣本平均何時會收斂、以及估計誤差長什麼樣子。

---

## 2. 定義 (Definitions)

- **random variable（隨機變數）**：把隨機結果映射到數值的函數，例如「明日報酬」。
- **Bernoulli 分布**：單次成敗試驗，$X\in\{0,1\}$，成功機率 $p$。
- **Binomial 分布**：$n$ 次獨立 Bernoulli 試驗的成功總數。
- **Normal 分布（常態／高斯分布）**：鐘形連續分布，由均值 $\mu$ 與變異數 $\sigma^2$ 決定。
- **Exponential 分布**：描述「事件間隔等待時間」的連續分布，參數 $\lambda$。
- **expectation（期望值）** $\mathbb{E}[X]$：機率加權的平均。
- **variance（變異數）** $\operatorname{Var}(X)$：偏離均值的平方期望。
- **covariance（共變異數）** $\operatorname{Cov}(X,Y)$：兩變數共同變動的程度。
- **conditional probability（條件機率）** $P(A\mid B)$：已知 $B$ 發生後 $A$ 的機率。

---

## 3. 核心公式 (Core equations)

期望值與變異數：

$$\mathbb{E}[X] = \sum_x x\,P(x) \;\;\text{或}\;\; \int x\,f(x)\,dx, \qquad \operatorname{Var}(X) = \mathbb{E}[(X-\mathbb{E}[X])^2]$$

共變異數與線性組合的變異數：

$$\operatorname{Cov}(X,Y) = \mathbb{E}[XY] - \mathbb{E}[X]\mathbb{E}[Y]$$

$$\operatorname{Var}(aX + bY) = a^2\operatorname{Var}(X) + b^2\operatorname{Var}(Y) + 2ab\operatorname{Cov}(X,Y)$$

常見分布的均值與變異數：

$$\text{Bernoulli}(p):\; \mu=p,\;\sigma^2=p(1-p) \qquad \text{Binomial}(n,p):\; \mu=np,\;\sigma^2=np(1-p)$$

$$\text{Normal}(\mu,\sigma^2) \qquad \text{Exponential}(\lambda):\; \mu=1/\lambda,\;\sigma^2=1/\lambda^2$$

Bayes 規則 (Bayes rule)：

$$P(A\mid B) = \frac{P(B\mid A)\,P(A)}{P(B)}$$

LLN 與 CLT（$X_i$ iid，均值 $\mu$、變異數 $\sigma^2$，$\bar X_n$ 為樣本平均）：

$$\bar X_n \xrightarrow{n\to\infty} \mu \quad(\text{LLN}), \qquad \frac{\bar X_n - \mu}{\sigma/\sqrt{n}} \xrightarrow{d} \mathcal{N}(0,1) \quad(\text{CLT})$$

---

## 4. 直覺解釋 (Plain-language intuition)

**期望值**是「重複無限多次後的長期平均」，不是「最可能的單次結果」。一個賭局可以期望值為正卻幾乎每次都輸——這正是肥尾交易策略的形態。

**LLN** 說：樣本愈多，樣本平均愈貼近真實均值。它保證估計「最終會對」，但沒說「要多久」。

**CLT** 補上了速度與形狀：不論原始分布長相如何（只要變異數有限），許多獨立樣本的平均，其分布會趨近常態，且離散程度以 $1/\sqrt{n}$ 縮小。這就是為什麼「標準誤差」總是出現 $\sqrt{n}$——要把不確定性減半，需要 4 倍的資料。

**Bayes 規則**是「拿到新證據後如何更新信念」的公式：先驗 $P(A)$ 經由似然 $P(B\mid A)$ 調整成後驗 $P(A\mid B)$。

---

## 5. 一個小範例 (A small example)

某策略每日要嘛「贏 +1%」、要嘛「輸 −0.8%」，贏的機率 $p=0.52$（一個 Bernoulli 結構）。

單日期望報酬：

$$\mathbb{E}[r] = 0.52(0.01) + 0.48(-0.008) = 0.0052 - 0.00384 = 0.00136$$

即每日約 +0.14%。單日變異數：

$$\mathbb{E}[r^2] = 0.52(0.0001) + 0.48(0.000064) = 0.00008272$$
$$\operatorname{Var}(r) = 0.00008272 - (0.00136)^2 \approx 0.0000809$$

標準差約 0.90%。期望雖正，單日波動卻是期望的 6 倍以上——任何單日結果幾乎傳達不了訊息，必須累積大量樣本（LLN）才看得出優勢，而 252 個交易日的平均報酬其分布近似常態（CLT）。

```python
import numpy as np
from quant_math_roadmap.math.probability import (
    running_mean, sampling_distribution_of_mean, simulate_normal, empirical_moments,
)

draws = simulate_normal(mu=0.00136, sigma=0.0090, size=10_000, seed=0)
print(empirical_moments(draws))                 # 均值、變異數、偏態、峰態
rm = running_mean(draws)                         # 觀察樣本平均收斂（LLN）
dist = sampling_distribution_of_mean(draws, sample_size=252)  # 近似常態（CLT）
```

---

## 6. 常見實作錯誤 (Typical implementation mistakes)

- **混淆 $\sigma$ 與 $\sigma/\sqrt{n}$**：母體標準差 $\sigma$ 不隨樣本數變；樣本平均的標準差（標準誤差）才是 $\sigma/\sqrt{n}$。
- **誤以為 CLT 讓資料變常態**：CLT 講的是「樣本平均」的分布，不是原始資料；單日報酬可以嚴重肥尾。
- **假設獨立性卻不成立**：報酬有波動率叢聚 (volatility clustering)，並非真正 iid；LLN/CLT 的收斂會變慢。
- **以為期望值就是典型結果**：偏態分布下，期望值可能離眾數很遠。
- **顛倒 Bayes 中的條件**：$P(A\mid B)\ne P(B\mid A)$，混淆會導致檢驗結果的嚴重誤判（base rate fallacy）。
- **小樣本就下結論**：LLN 是漸近性質，少數幾筆觀測的樣本平均仍可能離真值很遠。

---

## 7. 完成度檢查清單 (Readiness checklist)

- [ ] 我能由機率分布算出期望值與變異數。
- [ ] 我能寫出 $\operatorname{Var}(aX+bY)$ 並解釋共變異數項的角色。
- [ ] 我能說明 LLN 與 CLT 各自保證了什麼、又沒保證什麼。
- [ ] 我理解標準誤差中 $\sqrt{n}$ 的來源。
- [ ] 我能正確套用 Bayes 規則並避免顛倒條件。
- [ ] 我知道 Bernoulli、Binomial、Normal、Exponential 各自的均值與變異數。
- [ ] 我能用 `running_mean` 與 `sampling_distribution_of_mean` 觀察 LLN 與 CLT。

---

## 8. 延伸連結 (Links)

- 課程 notebook：[`notebooks/03_probability_simulation_lln_clt.ipynb`](../../notebooks/03_probability_simulation_lln_clt.ipynb)
- 可重用程式碼：`quant_math_roadmap.math.probability`（`running_mean`、`sampling_distribution_of_mean`、`simulate_normal`、`empirical_moments`）
- 官方學習資源：MIT OpenCourseWare 18.05 Introduction to Probability and Statistics，<https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/>
