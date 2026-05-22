# 統計推論速查表 (Statistical Inference Cheatsheet)

本速查表服務於具備程式設計經驗、準備量化金融與系統化研究課程的學習者。內容皆為原創撰寫，不轉載任何課程教材。

---

## 1. 動機 (Motivation)

策略研究的核心問題只有一個：**「我看到的績效是真本事，還是運氣？」** 統計推論就是回答這個問題的工具。

回測夏普比率、平均報酬、勝率——這些都是 **estimator（估計量）**，每一個都帶有 **sampling error（抽樣誤差）**。本速查表幫助你量化這份不確定性（**standard error（標準誤差）**、**confidence interval（信賴區間）**），並用 **hypothesis testing（假設檢定）** 評估證據強度。同等重要的是它的「警示」面向：在系統化研究中，反覆搜尋大量策略會製造 **selection bias（選擇偏誤）**，使 **p-value（p 值）** 嚴重失真。

---

## 2. 定義 (Definitions)

- **estimator（估計量）**：由樣本計算、用來逼近某母體參數的量，例如樣本平均。
- **bias（偏誤）**：$\operatorname{Bias}(\hat\theta) = \mathbb{E}[\hat\theta] - \theta$；估計量系統性偏離真值的程度。
- **variance（變異數）**：估計量隨樣本不同而抖動的程度。
- **standard error, SE（標準誤差）**：估計量抽樣分布的標準差。
- **confidence interval, CI（信賴區間）**：一段以指定覆蓋率（如 95%）涵蓋真參數的區間。
- **null hypothesis（虛無假設）** $H_0$：通常代表「沒有效果」（例如真實平均報酬為 0）。
- **p-value（p 值）**：在 $H_0$ 為真的前提下，觀測到「至少同等極端」結果的機率。
- **bootstrap（自助法）**：對資料重複抽樣（放回）以估計抽樣分布。

---

## 3. 核心公式 (Core equations)

樣本平均的標準誤差：

$$\widehat{\operatorname{SE}}(\bar x) = \frac{s}{\sqrt{n}}, \qquad s^2 = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar x)^2$$

均值的 95% 信賴區間（近似）：

$$\bar x \;\pm\; z_{0.975}\cdot \widehat{\operatorname{SE}}(\bar x), \qquad z_{0.975} \approx 1.96$$

單樣本 t 檢定統計量（檢定 $H_0:\mu=\mu_0$）：

$$t = \frac{\bar x - \mu_0}{s/\sqrt{n}}$$

年化夏普比率（$\bar r$、$s$ 為日報酬統計量）：

$$\widehat{\text{Sharpe}} = \frac{\bar r}{s}\sqrt{252}$$

均方誤差 (mean squared error) 的偏誤–變異數分解：

$$\operatorname{MSE}(\hat\theta) = \operatorname{Bias}(\hat\theta)^2 + \operatorname{Var}(\hat\theta)$$

多重檢定下的家族錯誤率 (family-wise error rate)，$m$ 次獨立檢定、各自顯著水準 $\alpha$：

$$P(\text{至少一個假陽性}) = 1 - (1-\alpha)^m$$

---

## 4. 直覺解釋 (Plain-language intuition)

**信賴區間**回答「我的估計有多精確」。95% CI 的正確解讀是程序性的：若把整個流程重複很多次，約 95% 的區間會涵蓋真值——並不是「真值有 95% 機率落在這個特定區間內」。

**p 值**衡量「資料與『沒有效果』的相容程度」。p 值小代表「若真的沒效果，這麼極端的結果很罕見」。它**不是**「策略無效的機率」，也**不是**效果大小。

**bootstrap** 的精神：你只有一份歷史，但可以對它放回重抽，模擬出「許多平行歷史」，從中直接讀出估計量的抖動範圍——不需要常態性假設。

最關鍵的警示：**統計顯著 ≠ 經濟顯著**。一個樣本夠大時，連微不足道、扣掉交易成本後賺不了錢的效果，也能得到 $p<0.05$。反過來，當你測試 100 個策略，即使全都無效，平均也會有 5 個僅憑運氣就「顯著」——這就是 **selection bias（選擇偏誤）**，是策略挖掘最危險的陷阱。

---

## 5. 一個小範例 (A small example)

某策略 $n=252$ 個交易日，日報酬平均 $\bar r = 0.0006$、標準差 $s = 0.012$。

標準誤差：$\widehat{\operatorname{SE}} = 0.012/\sqrt{252} \approx 0.000756$。

t 統計量（檢定 $H_0:\mu=0$）：

$$t = \frac{0.0006}{0.000756} \approx 0.79$$

$|t|\approx0.79$ 遠小於 1.96，**無法**拒絕「真實平均報酬為 0」。年化夏普僅 $\frac{0.0006}{0.012}\sqrt{252}\approx0.79$——回測看似賺錢，但統計上與運氣無法區分。

多重檢定的後果：若你篩選了 $m=100$ 個都無效的策略，至少出現一個假陽性的機率為 $1-(1-0.05)^{100}\approx0.994$。幾乎必然會挑到「看起來顯著」卻假的策略。

```python
import numpy as np
from quant_math_roadmap.math.statistics import (
    standard_error_of_mean, confidence_interval_mean,
    bootstrap_mean_ci, one_sample_ttest, false_discovery_demo,
)

returns = np.random.default_rng(0).normal(0.0006, 0.012, size=252)
print(standard_error_of_mean(returns))
print(confidence_interval_mean(returns, confidence=0.95))
print(bootstrap_mean_ci(returns, n_resamples=10_000, seed=0))
print(one_sample_ttest(returns, mu0=0.0).summary())
false_discovery_demo(n_strategies=100, seed=0)   # 觀察純運氣造成的假陽性
```

---

## 6. 常見實作錯誤 (Typical implementation mistakes)

- **誤解 p 值**：p 值不是「$H_0$ 為真的機率」，也不是效果大小。
- **忽略多重檢定**：搜尋了上百個策略卻只用 $\alpha=0.05$ 評估「贏家」，等於保證挑到假陽性；需用 Bonferroni 或控制 FDR。
- **把統計顯著當成可交易**：顯著但效果小於交易成本，實務上毫無價值。
- **獨立性假設失效**：報酬有自相關，樸素 SE 會低估不確定性，使夏普與 t 值灌水。
- **bootstrap 破壞時間結構**：對有自相關的報酬做逐點重抽會破壞相依性；時間序列應改用 block bootstrap。
- **n−1 vs n**：樣本變異數用 $n-1$（無偏）；用 $n$ 會低估變異數。
- **只報點估計、不報區間**：單一夏普數字若無 CI，無法評估其可信度。

---

## 7. 完成度檢查清單 (Readiness checklist)

- [ ] 我能正確（程序性地）解讀 95% 信賴區間。
- [ ] 我能說明 p 值是什麼、又不是什麼。
- [ ] 我能計算並解讀單樣本 t 檢定。
- [ ] 我能說明偏誤–變異數分解。
- [ ] 我能解釋選擇偏誤如何在策略搜尋中製造假陽性，並知道如何校正。
- [ ] 我能區分統計顯著與經濟顯著。
- [ ] 我能用 `bootstrap_mean_ci` 建構不依賴常態假設的信賴區間。

---

## 8. 延伸連結 (Links)

- 課程 notebook：[`notebooks/04_statistical_inference_for_strategy_returns.ipynb`](../../notebooks/04_statistical_inference_for_strategy_returns.ipynb)
- 可重用程式碼：`quant_math_roadmap.math.statistics`（`standard_error_of_mean`、`confidence_interval_mean`、`bootstrap_mean_ci`、`one_sample_ttest`、`false_discovery_demo`、`ols_fit`）
- 官方學習資源：
  - MIT OpenCourseWare 18.05 Introduction to Probability and Statistics，<https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/>
  - 國立臺灣大學開放式課程 統計學一上與計量導論，<https://ocw.aca.ntu.edu.tw/courses/112S103>
