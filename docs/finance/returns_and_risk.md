# 報酬與風險 (Returns and Risk)

> 教育與研究方法用途說明：本文件僅為量化金融基礎教育與研究方法之教材，**不構成任何投資建議**，文中數字皆為說明用途，不宣稱任何交易獲利能力。

## 1. 動機

任何系統化研究的起點，都是把「價格序列」轉換成「報酬序列」。價格本身不可直接比較（一檔 1000 元的股票漲 10 元，與一檔 20 元的股票漲 10 元，意義完全不同），而報酬是無量綱、可跨資產比較、且在統計上較接近平穩 (stationary) 的物件。

對一位**具備程式設計經驗、準備量化金融與系統化研究課程的學習者**而言，先把報酬的定義、年化假設、與風險度量徹底弄清楚，後續的投資組合建構、回測、評估才不會建立在錯誤的地基上。本文件聚焦於最基礎、但最容易被誤用的幾個量：simple return、log return、volatility、covariance、Sharpe ratio、maximum drawdown 與 turnover。

## 2. 定義

- **simple return（簡單報酬）**：第 $t$ 期的價格相對變動百分比。
- **log return（對數報酬 / 連續複利報酬）**：相鄰價格比值的自然對數。
- **compounding（複利）**：多期報酬如何累積成總報酬。
- **annualization（年化）**：把某一頻率（日 / 週 / 月）的統計量換算到「一年」尺度，需明確假設每年期數 (periods-per-year)。
- **volatility（波動度）**：報酬的標準差，衡量離散程度。
- **covariance（共變異數）**：兩個資產報酬共同變動的程度。
- **Sharpe ratio（夏普比率）**：超額報酬相對於波動度的比值。
- **maximum drawdown（最大回撤）**：權益曲線從歷史高點下跌的最大幅度。
- **turnover（週轉率）**：相鄰期之間投資組合權重變動的總量，與交易成本直接相關。

## 3. 核心公式

simple return：

$$ r_t = \frac{P_t - P_{t-1}}{P_{t-1}} = \frac{P_t}{P_{t-1}} - 1 $$

log return：

$$ \ell_t = \ln\!\left(\frac{P_t}{P_{t-1}}\right) = \ln(1 + r_t) $$

log return 可加性（多期複利）：$\ell_{1\to T} = \sum_{t=1}^{T} \ell_t$，而 simple return 為乘積：$1 + r_{1\to T} = \prod_{t=1}^{T}(1 + r_t)$。

年化平均與年化波動（$N$ 為 periods-per-year）：

$$ \mu_{\text{ann}} = N \cdot \bar{r}, \qquad \sigma_{\text{ann}} = \sqrt{N}\cdot \sigma_r $$

Sharpe ratio（$r_f$ 為無風險利率）：

$$ \text{Sharpe} = \frac{\mu_{\text{ann}} - r_f}{\sigma_{\text{ann}}} $$

covariance 與相關係數：

$$ \text{Cov}(r_x, r_y) = \mathbb{E}\big[(r_x - \mu_x)(r_y - \mu_y)\big], \qquad \rho_{xy} = \frac{\text{Cov}(r_x, r_y)}{\sigma_x \sigma_y} $$

maximum drawdown（$V_t$ 為權益曲線）：

$$ \text{MDD} = \min_{t}\left( \frac{V_t}{\max_{s \le t} V_s} - 1 \right) $$

turnover（$w_t$ 為權重向量）：

$$ \text{Turnover}_t = \sum_i \big| w_{t,i} - w_{t-1,i} \big| $$

## 4. 直覺解釋

simple return 是「我這一期實際賺賠的百分比」，直接對應現金；log return 則是「連續複利的指數」，它最大的好處是**可加性**——把一年的日 log return 加起來就是年度 log return，做統計（求平均、配常態分佈）特別方便。兩者在報酬很小時幾乎相等（$\ln(1+r)\approx r$）。

年化的核心假設是「各期報酬獨立同分佈」。波動度用 $\sqrt{N}$ 而非 $N$ 縮放，是因為變異數隨期數線性累加，標準差則是其平方根。

Sharpe ratio 把「報酬」與「承擔的風險」放在同一把尺上：兩個策略都賺 10%，波動度小的那個 Sharpe 較高，代表報酬「品質」較好。maximum drawdown 則回答另一個問題——「最痛的時候有多痛」，這對心理承受度與資金管理至關重要。

## 5. 一個小範例

某資產連續三日收盤價為 $P_0 = 100,\ P_1 = 102,\ P_2 = 99$。

- simple returns：$r_1 = 102/100 - 1 = 0.0200$；$r_2 = 99/102 - 1 = -0.0294$。
- log returns：$\ell_1 = \ln(1.02) = 0.0198$；$\ell_2 = \ln(99/102) = -0.0299$。
- 兩期累積（simple）：$(1.02)(0.9706) - 1 = -0.0100$，即總報酬約 $-1\%$，與 $99/100 - 1$ 一致。
- 兩期累積（log）：$0.0198 + (-0.0299) = -0.0101$，與 $\ln(99/100)$ 一致。

假設某日報酬樣本標準差 $\sigma_r = 0.012$、樣本平均 $\bar r = 0.0004$，以日頻 $N = 252$ 年化：$\sigma_{\text{ann}} = 0.012\sqrt{252} \approx 0.190$，$\mu_{\text{ann}} = 0.0004 \times 252 \approx 0.101$。若 $r_f = 0$，則 Sharpe $\approx 0.101 / 0.190 \approx 0.53$。

**Sharpe ratio 的重要警語 (caveats)**：上面的 0.53 是一個**估計值 (estimate)**，帶有抽樣誤差 (sampling error)。樣本越短、誤差越大。Sharpe 假設報酬近似常態，因此**忽略 skew（偏態）與 fat tails（厚尾）**——一個賣尾端風險的策略可能有漂亮的 Sharpe，卻在崩盤時瞬間爆掉。最關鍵的事實：在多次回測與參數搜尋下，一個 backtested Sharpe of 2 完全可能與 true Sharpe of 0 相容（純屬運氣 + 多重檢定）。因此 Sharpe 必須搭配信賴區間、樣本外驗證與多重檢定校正一起解讀。

## 6. 常見實作錯誤

- 把 log return **直接相加後當成 simple return** 報告給他人；對外溝通報酬時應換回 simple。
- 年化波動誤用 $N$ 而非 $\sqrt{N}$ 縮放。
- periods-per-year 用錯：日頻應為 252（交易日，非 365），週頻 52，月頻 12。
- 計算 simple return 時對含 0 或負值的價格 / 已調整序列直接相除。
- 用「未經除息、除權調整」的原始價格計算報酬，導致除權息日出現假跳空。
- 把單一回測得到的 Sharpe 當成「真實」績效，忽略抽樣誤差與多重檢定。
- 計算 maximum drawdown 時對「報酬序列」而非「累積權益曲線」取 min。
- 報酬序列與權重序列**時間沒有對齊**，turnover 因而虛高或虛低。

## 7. 完成度檢查清單

- [ ] 我能在不查表的情況下寫出 simple return 與 log return 公式，並說明何時兩者近似相等。
- [ ] 我能解釋為何 log return 可加、simple return 需連乘。
- [ ] 我能正確選擇 periods-per-year（日 252 / 週 52 / 月 12）並年化平均與波動。
- [ ] 我能說出 Sharpe ratio 至少三項 caveats（抽樣誤差、忽略偏態厚尾、多重檢定）。
- [ ] 我能從權益曲線正確計算 maximum drawdown。
- [ ] 我能解釋 turnover 為何與交易成本相關。
- [ ] 我能說明 covariance 與 correlation 的差異與用途。

## 8. 延伸連結

- 課程 notebook：[notebooks/01_returns_covariance_and_linear_algebra.ipynb](../../notebooks/01_returns_covariance_and_linear_algebra.ipynb)
- 可重用程式碼：`quant_math_roadmap.finance.returns`（`simple_returns`、`log_returns`、`cumulative_returns`、`total_return`）與 `quant_math_roadmap.finance.metrics`（`annualized_mean`、`annualized_volatility`、`sharpe_ratio`、`max_drawdown`、`covariance_matrix`、`correlation_matrix`、`turnover`、`periods_per_year`、`PERIODS_PER_YEAR`）。
- 官方外部學習資源：國立臺灣大學開放式課程「基礎財金素養」，<https://ocw.aca.ntu.edu.tw/courses/110S204>
