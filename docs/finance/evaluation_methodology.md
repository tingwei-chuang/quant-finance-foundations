# 評估方法論 (Evaluation Methodology)

> 教育與研究方法用途說明：本文件僅為量化金融基礎教育與研究方法之教材，**不構成任何投資建議**，文中數字皆為說明用途，不宣稱任何交易獲利能力。

> 本文件是整個 roadmap 中**最重要的一份**。其他文件教你「怎麼算」，這份文件教你「怎麼知道自己有沒有騙到自己」。

## 1. 動機

量化研究最危險的不是「算錯」，而是「算對了一個沒有意義的東西」。一條漂亮的 equity curve（權益曲線）非常容易做出來——只要不小心讓模型偷看了未來，或在上百組參數中挑出最好看的那一組，回測幾乎一定亮眼。

**核心信念：一條漂亮的 equity curve 並不能證明策略有效 (a good equity curve does not prove a valid strategy)。** 真正能說服人的，是一套嚴謹、可重現、且刻意對自己不利的評估流程。本文件為**具備程式設計經驗、準備量化金融與系統化研究課程的學習者**整理出評估方法論的核心概念與防錯清單。

## 2. 定義

- **in-sample / out-of-sample（樣本內 / 樣本外）**：模型開發 / 調參所用的資料 vs. 完全未參與開發、僅用於最終檢驗的資料。
- **time-based split（時間切分）**：依時間順序切資料，訓練集永遠在測試集之前。
- **walk-forward testing（前進式測試）**：反覆「以過去訓練、對緊接的未來測試」並向前推進。
- **look-ahead bias（前視偏誤）**：在時點 $t$ 使用了 $t$ 之後才存在的資訊。
- **data leakage（資料洩漏）**：未來資訊以隱蔽方式滲入特徵或標籤。
- **survivorship bias（倖存者偏誤）**：資料集只含「存活到今天」的標的，已下市者被剔除。
- **benchmark（基準）**：用來比較策略好壞的參考對象（如 buy-and-hold）。
- **multiple testing（多重檢定）**：嘗試大量策略 / 參數，使「靠運氣勝出」的機率大增。

## 3. 核心公式

時間切分：給定資料索引 $0, 1, \dots, T-1$，以比例 $\alpha$ 切分：

$$ \text{train} = \{0, \dots, \lfloor \alpha T \rfloor - 1\}, \qquad \text{test} = \{\lfloor \alpha T \rfloor, \dots, T-1\} $$

**no look-ahead 的訊號對位規則**：在時點 $t$ 形成的訊號 $s_t$，只能用於 $t+1$（含）之後的報酬。部位 (position) 必須位移：

$$ \text{position}_t = s_{t-1}, \qquad \text{strategy\_return}_t = \text{position}_t \cdot r_t = s_{t-1}\cdot r_t $$

walk-forward（expanding window，第 $k$ 折）：

$$ \text{train}_k = \{0, \dots, e_k - 1\}, \qquad \text{test}_k = \{e_k, \dots, e_k + h - 1\} $$

walk-forward（rolling window，固定訓練長度 $L$）：

$$ \text{train}_k = \{e_k - L, \dots, e_k - 1\}, \qquad \text{test}_k = \{e_k, \dots, e_k + h - 1\} $$

含交易成本的淨報酬（$c$ 為單位成本，$\text{Turnover}_t$ 為部位變動量）：

$$ r^{\text{net}}_t = \text{position}_{t}\cdot r_t - c \cdot \text{Turnover}_t $$

多重檢定下，期望最大 Sharpe（即使真實 Sharpe 全為 0）仍隨嘗試次數 $M$ 上升——這正是「靠運氣」的數學來源。

## 4. 直覺解釋

**in-sample vs out-of-sample**：模型在它「讀過」的資料上表現好，是理所當然，不構成證據。唯有在**完全沒參與開發**的資料上仍然成立，才稍微可信。因此 out-of-sample 資料必須像「封存的考題」，在最終驗證前絕不打開。

**時間切分而非隨機切分**：金融資料有時間順序，隨機洗牌會讓「未來」混進訓練集，這本身就是 leakage。訓練集必須永遠在測試集之前。

**walk-forward testing** 模擬真實上線：每次只用「截至某時點」的資料訓練，對緊接的未來測試，再向前滾動。expanding window 訓練集越來越長（資訊累積）；rolling window 固定訓練長度（較能適應結構變化）。它比單次切分更貼近實況，也更難自欺。

**look-ahead bias 與 data leakage** 是頭號殺手。最常見的形式：用「當期」的訊號去乘「當期」的報酬——但當期收盤後你才算得出訊號，根本不可能在當期就建立部位。正確做法是把部位**位移一格**（`position_t = signal_{t-1}`）。其他隱蔽形式包括：用整段資料的均值 / 標準差做標準化、用未來才公布的財報日期、用「重述後」的資料。

**survivorship bias（概念性警告）**：如果回測只用「今天還在交易」的標的，你已經系統性地排除了所有倒閉、下市的公司，結果必然過度樂觀。即使本 roadmap 多用合成或自備資料，也必須在概念上隨時警惕這一點。

**benchmark selection**：策略賺 8% 聽起來不錯，但若同期 buy-and-hold 賺 12%，這個策略其實在「毀滅價值」。沒有合適 benchmark 的績效數字沒有意義。

**multiple testing**：如果你試了 200 組參數，挑出最好的一組，那組的亮眼回測有極大成分是運氣。**a backtested Sharpe of 2 完全可能對應 true Sharpe of 0**。嘗試次數必須誠實記錄，並對結果打折。

**最嚴厲的提醒**：一個**刻意洩漏 (intentionally leaked)** 的模型——例如用未來報酬決定今天部位——會產生「好到不真實」的 equity curve。這種曲線**只能當作反面教材，用來示範洩漏長什麼樣子，絕不可被解讀為一個策略**。

## 5. 一個小範例

假設某資產日報酬序列 $r = [+0.01, -0.02, +0.03, +0.01, -0.01]$，以及一個由收盤資訊算出的訊號 $s = [+1, -1, +1, +1, -1]$（$+1$ 看多、$-1$ 看空）。

**錯誤做法（look-ahead / leakage）**：用同期訊號 $\text{strategy}_t = s_t \cdot r_t$。

$$ s \cdot r = [+0.01,\ +0.02,\ +0.03,\ +0.01,\ +0.01] $$

每一天都賺錢、累積報酬約 $+8\%$、Sharpe 高得離譜——因為 $s_t$ 偷看了 $r_t$。這條曲線**毫無意義**。

**正確做法（部位位移一格）**：$\text{position}_t = s_{t-1}$，第 1 天無前一日訊號故不持倉。

$$ \text{strategy}_t = s_{t-1}\cdot r_t = [\,\text{n/a},\ +0.01,\ +0.02,\ +0.03,\ -0.01\,] $$

累積結果平凡許多，可能輸給 buy-and-hold。**這個平凡的數字才是誠實的估計。** 兩者的差距，就是 look-ahead bias 的大小。

進一步，套用 walk-forward：例如以 expanding window 切 4 折，每折用過去訓練、對未來 $h$ 天測試，把各折的 out-of-sample 報酬接起來，再扣掉 $c\cdot\text{Turnover}$ 的交易成本，並與同期 buy-and-hold benchmark 對照——這才是一個可被檢視的評估流程。

## 6. 常見實作錯誤

- 用同期訊號乘同期報酬（$s_t \cdot r_t$），**忘記把部位位移**為 $s_{t-1}$。
- 隨機切分時間序列，把未來資料洗進訓練集。
- 用**整段資料**的均值 / 標準差做特徵標準化（測試期統計量滲入訓練）。
- 在挑完最佳參數後，才「順便」看一眼 out-of-sample——它已被汙染。
- 不記錄嘗試過的參數 / 策略總數，無視 multiple testing。
- 回測**不計交易成本與 turnover**。
- 沒有 benchmark，或選了一個刻意偏弱的 benchmark。
- 使用只含現存標的的資料（survivorship bias）而不加註警告。
- 把 `leaked_strategy_returns` 這類**示範用洩漏模型**的輸出當成真實績效呈現。
- 特徵用到「重述後」資料或未來才公布的事件日期。

## 7. 完成度檢查清單

- [ ] 我能清楚區分 in-sample 與 out-of-sample，並說明後者為何不可提前打開。
- [ ] 我的所有切分都是 time-based，訓練集永遠早於測試集。
- [ ] 我能實作 expanding window 與 rolling window 的 walk-forward。
- [ ] 我已確認每個特徵在時點 $t$ 只用了 $t$（含）之前的資訊。
- [ ] 我的部位已正確位移（`position_t = signal_{t-1}`），並能解釋原因。
- [ ] 我的回測已計入 transaction cost 與 turnover。
- [ ] 我為策略選定了合理的 benchmark（如 buy-and-hold）。
- [ ] 我已記錄嘗試過的策略 / 參數數量，並對結果做多重檢定的保留。
- [ ] 我理解 survivorship bias，並檢視過資料是否受其影響。
- [ ] 我能說明為何「漂亮的 equity curve 不等於有效策略」。
- [ ] 我能辨識 intentionally leaked 模型，並絕不把它當成策略呈現。

## 8. 延伸連結

- 課程 notebook：[notebooks/08_walk_forward_forecasting_and_backtesting_integrity.ipynb](../../notebooks/08_walk_forward_forecasting_and_backtesting_integrity.ipynb)
- 可重用程式碼：`quant_math_roadmap.time_series.splits`（`train_test_split_time`、`expanding_window_splits`、`rolling_window_splits`）；`quant_math_roadmap.backtesting.leakage_checks`（`signal_to_positions`、`assert_no_lookahead`、`leaked_strategy_returns`——後者僅為洩漏的反面示範）；`quant_math_roadmap.backtesting.engine`（`run_backtest`、`buy_and_hold_benchmark`）；`quant_math_roadmap.backtesting.costs`（`apply_transaction_costs`、`position_turnover`）；`quant_math_roadmap.backtesting.baselines`（`buy_and_hold_equity`、`equal_weight_rebalanced_equity`）。
- 官方外部學習資源：
  - "Forecasting: Principles and Practice, the Pythonic Way"，<https://otexts.com/fpppy/>
  - Penn State STAT 510 (Applied Time Series Analysis)，<https://online.stat.psu.edu/stat510/>
