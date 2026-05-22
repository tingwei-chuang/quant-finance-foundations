# 投資組合建構 (Portfolio Construction)

> 教育與研究方法用途說明：本文件僅為量化金融基礎教育與研究方法之教材，**不構成任何投資建議**，文中數字皆為說明用途，不宣稱任何交易獲利能力。

## 1. 動機

有了報酬與風險的語言之後，下一個問題是：「資金該如何分配到多檔資產？」這就是 portfolio construction。不同的權重決定方式，會帶來截然不同的風險、turnover 與交易成本。

對一位**具備程式設計經驗、準備量化金融與系統化研究課程的學習者**而言，本文件從最簡單的 equal weight 出發，經過 buy-and-hold，到需要 covariance 估計的 minimum-variance portfolio，並強調一個常被忽略的現實：**權重的好壞，受限於 covariance 估計的品質**。

## 2. 定義

- **weight vector（權重向量）** $w$：各資產佔總資金的比例，通常要求 $\sum_i w_i = 1$。
- **equal weight（等權重）**：每檔資產分配相同比例 $1/n$。
- **buy-and-hold（買進持有）**：期初配置一次，之後不再調整；權重會隨價格漲跌而 drift（漂移），turnover 為零。
- **minimum-variance portfolio（最小變異數投資組合）**：在權重總和為 1 的限制下，使組合變異數最小的權重。
- **covariance matrix（共變異數矩陣）** $\Sigma$：描述各資產報酬間共同變動的方陣。
- **transaction cost（交易成本）**：每次調整權重所付出的成本，與 turnover 成正比。
- **constraint（限制條件）**：例如 long-only（不可放空，$w_i \ge 0$）。
- **shrinkage（收縮估計）**：把樣本 covariance 朝一個結構化目標拉近，以降低估計雜訊。

## 3. 核心公式

投資組合變異數（$w$ 為權重向量，$\Sigma$ 為 covariance matrix）：

$$ \sigma_p^2 = w^\top \Sigma\, w $$

equal weight：

$$ w_i = \frac{1}{n}, \quad i = 1, \dots, n $$

minimum-variance portfolio 的最佳化問題：

$$ \min_{w}\ w^\top \Sigma\, w \quad \text{s.t.}\quad \mathbf{1}^\top w = 1 $$

以 Lagrange multiplier 求解，得到 closed-form 解：

$$ w^\star = \frac{\Sigma^{-1}\mathbf{1}}{\mathbf{1}^\top \Sigma^{-1}\mathbf{1}} $$

其中 $\mathbf{1}$ 為全 1 向量。turnover（相鄰兩期）：

$$ \text{Turnover}_t = \sum_i \big| w_{t,i} - w_{t-1,i} \big| $$

shrinkage covariance（$\delta \in [0,1]$ 為收縮強度，$T$ 為結構化目標）：

$$ \Sigma_{\text{shrink}} = (1 - \delta)\,\Sigma_{\text{sample}} + \delta\, T $$

## 4. 直覺解釋

**equal weight** 是最樸素的基準：不需要任何估計，把蛋平均放進每個籃子。它出奇地難被打敗，常被當作其他複雜方法的「對照組」。

**buy-and-hold** 強調一個容易被忽略的事實：一旦期初配置完成、之後不交易，權重並不會停在 $1/n$——上漲的資產佔比自然變大、下跌的變小。它的 turnover 為零，因此**交易成本最低**，但風險暴露會逐漸偏離初衷。

**minimum-variance portfolio** 不去預測「哪檔會漲」（那很難且不穩定），只專注於「如何讓組合波動最小」。它的 closed-form 解 $w^\star = \Sigma^{-1}\mathbf{1} / (\mathbf{1}^\top \Sigma^{-1}\mathbf{1})$ 漂亮，但有個陷阱：它**完全仰賴 $\Sigma$ 的反矩陣**。

**為什麼 covariance 估計品質如此關鍵？** 當資產數 $n$ 接近樣本期數 $T$ 時，樣本 covariance matrix 會病態 (ill-conditioned)，$\Sigma^{-1}$ 會放大估計雜訊，產生極端、不穩定、甚至大幅放空的權重。解法是 **shrinkage**：把雜訊很大的樣本估計，朝一個較穩定的結構化目標（例如對角矩陣或常數相關模型）收縮，犧牲一點偏誤換取大幅降低變異。實務上幾乎不會直接用未經處理的樣本 covariance。

最後，每一次再平衡都產生 turnover、進而產生 transaction cost。一個「紙上」最佳的組合，扣掉成本後可能不如 buy-and-hold。因此**建構權重時必須意識到成本與週轉**，並考慮 long-only 等實際限制。

## 5. 一個小範例

考慮兩檔資產，年化波動分別為 $\sigma_1 = 20\%$、$\sigma_2 = 10\%$，相關係數 $\rho = 0.2$。covariance matrix：

$$ \Sigma = \begin{pmatrix} 0.04 & 0.004 \\ 0.004 & 0.01 \end{pmatrix} $$

equal weight $w = (0.5, 0.5)$ 的組合變異數：

$$ \sigma_p^2 = 0.25(0.04) + 0.25(0.01) + 2(0.25)(0.004) = 0.0145,\quad \sigma_p \approx 12.0\% $$

minimum-variance 解：$\Sigma^{-1}\mathbf{1}$ 計算後，最小變異權重約為 $w^\star \approx (0.158,\ 0.842)$——更多資金配置到低波動的資產 2。其組合波動約 $9.7\%$，**低於** equal weight 的 $12.0\%$，符合「最小化變異」的目標。

注意：若這是一個會逐期重算 $w^\star$ 的策略，每期權重變動都會貢獻 turnover；而 buy-and-hold 從 $(0.158, 0.842)$ 出發後不再交易，turnover 為零。

## 6. 常見實作錯誤

- 直接用未經處理的樣本 covariance 求 $\Sigma^{-1}$，在 $n$ 接近 $T$ 時得到極端權重。
- 忽略 minimum-variance 解可能含**大幅放空**，而實際帳戶有 long-only 限制。
- 把 buy-and-hold 誤當成「固定權重」，忘記權重會隨價格 drift。
- 估計 covariance 時用錯頻率，或年化與非年化混用。
- 評估策略時**不計入 transaction cost 與 turnover**，高估績效。
- 權重未正規化（$\sum_i w_i \ne 1$）。
- 用未來資料估計 $\Sigma$（look-ahead），詳見評估方法論文件。

## 7. 完成度檢查清單

- [ ] 我能寫出組合變異數 $w^\top \Sigma w$ 並手算兩資產情形。
- [ ] 我能推導並解釋 minimum-variance 的 closed-form 解。
- [ ] 我能解釋 buy-and-hold 的權重為何會 drift、turnover 為何為零。
- [ ] 我能說明 covariance 估計病態如何破壞 minimum-variance 權重。
- [ ] 我能說明 shrinkage 的動機與基本形式。
- [ ] 我能將 turnover 與 transaction cost 納入策略評估。
- [ ] 我能說明 long-only 等限制如何改變最佳化結果。

## 8. 延伸連結

- 課程 notebook：[notebooks/02_multivariable_calculus_and_min_variance_portfolio.ipynb](../../notebooks/02_multivariable_calculus_and_min_variance_portfolio.ipynb)
- 可重用程式碼：`quant_math_roadmap.finance.portfolio`（`equal_weights`、`minimum_variance_portfolio`、`buy_and_hold_weights`、`shrinkage_covariance`、`portfolio_variance`）；turnover 相關見 `quant_math_roadmap.finance.metrics.turnover` 與 `quant_math_roadmap.backtesting.costs.position_turnover`。
- 官方外部學習資源：國立臺灣大學開放式課程「基礎財金素養」，<https://ocw.aca.ntu.edu.tw/courses/110S204>
