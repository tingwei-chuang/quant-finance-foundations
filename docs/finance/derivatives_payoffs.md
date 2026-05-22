# 衍生品損益 (Derivatives Payoffs)

> 教育與研究方法用途說明：本文件僅為量化金融基礎教育與研究方法之教材，**不構成任何投資建議**，文中數字皆為說明用途，不宣稱任何交易獲利能力。

## 1. 動機

衍生品 (derivatives) 的價值「衍生」自標的資產的價格。要理解選擇權與期貨，第一步不是去背公式，而是先把 **payoff（到期損益）** 畫清楚——只要能畫出損益圖，就能理解組合策略與 no-arbitrage（無套利）邏輯。

對一位**具備程式設計經驗、準備量化金融與系統化研究課程的學習者**而言，本文件刻意採取「最小數學」路線。

**重要範圍聲明**：本 8 週 roadmap **刻意避開隨機微積分 (stochastic calculus)**，**不要求 Black-Scholes 的推導**。我們改用 binomial model（二項樹模型）來定價歐式選擇權——它只需要**算術與 no-arbitrage 原理**，不需要 Itô's lemma 或偏微分方程。這讓學習者能在沒有研究所數學背景下，仍然真正「理解」選擇權定價的核心邏輯。

## 2. 定義

- **forward（遠期合約）**：雙方約定未來某日以固定價格買賣標的的場外合約。
- **futures（期貨）**：標準化、在交易所交易、每日結算 (mark-to-market) 的遠期合約。
- **call option（買權）**：賦予持有人「以 strike price $K$ 買入標的」之權利（非義務）。
- **put option（賣權）**：賦予持有人「以 strike price $K$ 賣出標的」之權利。
- **payoff（到期損益）**：合約在到期日依標的價格 $S_T$ 決定的現金結果。
- **straddle（跨式）**：同時買進相同 $K$、相同到期日的一個 call 與一個 put。
- **no-arbitrage（無套利）**：不存在「零成本、零風險卻必定獲利」的機會。
- **binomial tree（二項樹）**：假設每一小段時間內標的只會「上漲」或「下跌」兩種結果的離散模型。

## 3. 核心公式

call 與 put 的到期 payoff（$S_T$ 為到期標的價格）：

$$ \text{Call payoff} = \max(S_T - K,\ 0), \qquad \text{Put payoff} = \max(K - S_T,\ 0) $$

forward 的到期 payoff（多方，$F$ 為約定遠期價）：

$$ \text{Forward payoff} = S_T - F $$

long straddle 的到期 payoff：

$$ \text{Straddle payoff} = \max(S_T - K,\ 0) + \max(K - S_T,\ 0) = |S_T - K| $$

put-call parity（無套利下，歐式選擇權，$r$ 為無風險利率，$T$ 為到期時間）：

$$ C - P = S_0 - K\,e^{-rT} $$

一期二項樹的風險中性機率 $q$ 與選擇權定價（標的可上漲到 $S_0 u$ 或下跌到 $S_0 d$，$d < e^{r\Delta t} < u$）：

$$ q = \frac{e^{r\,\Delta t} - d}{u - d}, \qquad C_0 = e^{-r\,\Delta t}\big[\,q\,C_u + (1 - q)\,C_d\,\big] $$

多期則對 $n$ 期樹由葉節點向根節點逐步以同一式回溯 (backward induction)。

## 4. 直覺解釋

**期貨 / 遠期**的損益是一條 45 度直線：標的漲多少、多方就賺多少，對稱地，跌多少就賠多少。

**選擇權**的損益是「折線」：call 在 $S_T < K$ 時 payoff 為 0（不會行使權利），$S_T > K$ 後才隨標的線性上升——這個「下方被截平、上方保留」的不對稱性，正是選擇權的本質。put 則相反，是向左上方的折線。

**straddle** 把 call 與 put 疊在一起，得到一個 V 字形 $|S_T - K|$：無論標的大漲或大跌都賺，只在標的「不動」時最賠（付出的權利金損失）——這是一個對「波動」而非「方向」下注的組合。

**二項樹的直覺**：在一小段時間內，假設標的只會跳到「上」或「下」兩個價位。此時我們可以用標的與無風險資產組出一個複製選擇權損益的投資組合 (replicating portfolio)；既然複製組合的成本可算，no-arbitrage 就強制選擇權今天的價格等於該成本。把時間切成 $n$ 段，逐節點回溯，就能對歐式選擇權定價——全程只用加減乘除。

**關鍵警語**：binomial model 給出的是**模型價格 (model price)**，是在特定假設（給定 $u, d, r$）下的「無套利一致價格」。它**絕不應被解讀為對真實市場價格的預測**。真實市場價格受供需、流動性、波動度預期等諸多因素影響；模型的用途是檢驗一致性與相對定價，不是預測。

## 5. 一個小範例

設 $S_0 = 100$，一期後標的上漲到 $S_0 u = 110$（$u = 1.1$）或下跌到 $S_0 d = 90$（$d = 0.9$）。無風險利率使單期成長因子 $e^{r\Delta t} = 1.02$。考慮一個 strike $K = 100$ 的歐式 call。

葉節點 payoff：

- 上漲：$C_u = \max(110 - 100,\ 0) = 10$
- 下跌：$C_d = \max(90 - 100,\ 0) = 0$

風險中性機率：

$$ q = \frac{1.02 - 0.9}{1.1 - 0.9} = \frac{0.12}{0.20} = 0.60 $$

選擇權今日價格：

$$ C_0 = \frac{1}{1.02}\big[\,0.60 \times 10 + 0.40 \times 0\,\big] = \frac{6.0}{1.02} \approx 5.88 $$

因此這個 call 的模型價格約為 5.88。同樣的樹也能對 put 定價，並可用 put-call parity 交叉驗證 $C - P$ 是否等於 $S_0 - K e^{-rT}$。

## 6. 常見實作錯誤

- 混淆 payoff 與 profit：payoff 未扣除買進選擇權所付的 premium（權利金）。
- 二項樹參數違反 no-arbitrage 條件 $d < e^{r\Delta t} < u$，導致 $q$ 落在 $[0,1]$ 之外。
- 把風險中性機率 $q$ 誤當成「真實世界的上漲機率」。
- 多期樹回溯時折現次數算錯，或對美式選擇權忘記在每節點檢查提前行使。
- 對 call / put payoff 漏掉 $\max(\cdot, 0)$ 的下方截平。
- **把 binomial model price 當成市場價格預測**，或拿去宣稱可獲利。
- 套用 put-call parity 時把美式選擇權當歐式，或折現項符號弄反。

## 7. 完成度檢查清單

- [ ] 我能徒手畫出 call、put、forward、straddle 的損益圖。
- [ ] 我能寫出 $\max(S_T-K,0)$ 與 $\max(K-S_T,0)$ 並說明其不對稱性。
- [ ] 我能解釋 no-arbitrage 為何能「鎖定」選擇權價格。
- [ ] 我能手算一期二項樹的 $q$ 與選擇權價格。
- [ ] 我能說明多期二項樹如何由葉節點回溯定價歐式選擇權。
- [ ] 我能說明本 roadmap 為何不需要 Black-Scholes 推導與隨機微積分。
- [ ] 我能清楚說明「model price 不是市場價格的預測」。

## 8. 延伸連結

- 課程 notebook：[notebooks/06_financial_mathematics_and_option_pricing.ipynb](../../notebooks/06_financial_mathematics_and_option_pricing.ipynb)
- 可重用程式碼：`quant_math_roadmap.finance.derivatives`（`call_payoff`、`put_payoff`、`forward_payoff`、`long_straddle_payoff`、`binomial_european_option`、`put_call_parity_gap`）。
- 官方外部學習資源：國立臺灣大學開放式課程「基礎財金素養」，<https://ocw.aca.ntu.edu.tw/courses/110S204>
