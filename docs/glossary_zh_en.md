# 中英術語對照表 (Bilingual Glossary)

本文件提供量化金融與系統化研究常用術語的中英對照與一句話說明,
涵蓋統計、線性代數、微積分、金融、時間序列與回測等領域。
目標讀者為具備程式設計經驗、準備量化金融與系統化研究課程的學習者。
標準英文技術術語予以保留,以便對照原文教材與本倉庫程式碼。

> 本文件僅供教育與研究方法用途,不構成任何投資建議。

表格依英文術語字母順序排列。

| English Term | 中文 | 簡短說明 (Definition) |
|---|---|---|
| ACF (Autocorrelation Function) | 自相關函數 | 描述時間序列與其自身落後值相關程度的函數。 |
| AR(1) | 一階自迴歸模型 | 當期值由前一期值加白噪音線性決定的時間序列模型。 |
| Autocorrelation | 自相關 | 同一序列在不同時間點之間的相關性。 |
| Backtest | 回測 | 以歷史資料模擬策略表現以評估其績效的程序。 |
| Benchmark | 基準 | 用來衡量策略相對表現的參照標的或投組。 |
| Beta | 貝它係數 | 迴歸中衡量資產報酬對某因子敏感度的係數。 |
| Bias | 偏誤 | 估計量的期望值與真實參數之間的系統性差距。 |
| Binomial Tree | 二項樹 | 以離散上下分支模擬標的價格演化的選擇權定價模型。 |
| Bond | 債券 | 承諾未來支付固定現金流的固定收益證券。 |
| Bootstrap | 拔靴法 | 以放回抽樣重複估計統計量以量化不確定性的方法。 |
| Buy-and-Hold | 買進並持有 | 期初配置一次後不再交易、權重隨表現漂移的被動策略。 |
| Call Option | 買權 | 賦予持有者以履約價買入標的之權利的合約。 |
| Central Limit Theorem | 中央極限定理 | 大量獨立同分配變數之和(平均)近似常態分配的定理。 |
| Confidence Interval | 信賴區間 | 以給定覆蓋機率涵蓋真實參數的一段估計區間。 |
| Correlation | 相關係數 | 標準化後的共變異數,衡量線性關聯,取值於 -1 至 1。 |
| Covariance Matrix | 共變異數矩陣 | 描述多變數彼此共變異關係的對稱半正定矩陣。 |
| Curve-fitting | 曲線擬合 | 過度調參使模型擬合歷史噪音而非真實規律。 |
| Data Leakage | 資料洩漏 | 訓練過程混入不該取得的資訊,使績效虛高。 |
| Discount Factor | 折現因子 | 將未來一單位現金流換算為現值的乘數。 |
| Drawdown | 回撤 | 權益曲線自先前高點下跌的幅度。 |
| Eigenvalue | 特徵值 | 矩陣作用於對應特徵向量時的縮放倍數。 |
| Estimator | 估計量 | 由樣本資料計算、用以推估母體參數的函數。 |
| Expanding Window | 擴展窗 | 訓練窗起點固定、長度隨時間增長的 walk-forward 切分。 |
| Expectation | 期望值 | 隨機變數依機率加權的平均值。 |
| Factor Model | 因子模型 | 以少數共同因子解釋資產報酬的線性模型。 |
| Forward | 遠期合約 | 約定未來某日以議定價格買賣標的的客製化合約。 |
| Futures | 期貨 | 在交易所標準化、每日結算的遠期型合約。 |
| Gradient | 梯度 | 多變數函數各偏導數構成的向量,指向上升最快方向。 |
| Hessian | Hessian 矩陣 | 多變數函數二階偏導數構成的方陣。 |
| Heteroskedasticity | 異質變異 | 誤差項變異數隨觀測而改變的現象。 |
| Hypothesis Test | 假設檢定 | 以資料判斷是否拒絕某虛無假設的統計程序。 |
| In-sample | 樣本內 | 用於擬合或調參的歷史資料區間。 |
| Intercept | 截距 | 迴歸式中所有自變數為零時的應變數預測值。 |
| Law of Large Numbers | 大數法則 | 樣本平均隨樣本數增加而收斂至母體平均的定理。 |
| Log Return | 對數報酬 | 毛報酬取自然對數,具跨期可加性。 |
| Look-ahead Bias | 前視偏誤 | 在某時點使用了當時尚不可得的未來資訊。 |
| Maximum Drawdown | 最大回撤 | 整段期間內最深的一次回撤。 |
| Minimum-variance Portfolio | 最小變異投組 | 在權重約束下使投組變異數最小的配置。 |
| Multiple Testing | 多重檢定 | 同時進行多次檢定,使假陽性機率累積上升。 |
| No-arbitrage | 無套利 | 不存在零成本、零風險而必獲利機會的定價原則。 |
| OLS (Ordinary Least Squares) | 普通最小平方法 | 以最小化殘差平方和來估計線性迴歸係數的方法。 |
| Out-of-sample | 樣本外 | 未參與擬合、用於驗證的資料區間。 |
| p-value | p 值 | 在虛無假設成立下觀察到不少於現有極端結果的機率。 |
| Payoff | 收益 | 衍生品到期時依標的價格決定的現金流。 |
| Positive Semidefinite | 半正定 | 二次型對任意向量皆非負的對稱矩陣性質。 |
| Present Value | 現值 | 未來現金流經折現後加總的當前價值。 |
| Put Option | 賣權 | 賦予持有者以履約價賣出標的之權利的合約。 |
| Put-Call Parity | 買賣權平價 | 連結同條件買權、賣權與標的的無套利等式關係。 |
| Quadratic Form | 二次型 | 形如 w 轉置乘 A 乘 w 的純量函數,投組變異數即一例。 |
| R-squared | 判定係數 | 迴歸模型所解釋的應變數變異比例。 |
| Random Walk | 隨機漫步 | 當期值等於前期值加獨立隨機衝擊的非定態序列。 |
| Rebalancing | 再平衡 | 定期將投組權重調回目標配置的主動行為。 |
| Regression | 迴歸 | 以自變數解釋或預測應變數的統計建模方法。 |
| Residual | 殘差 | 觀測值與模型擬合值之間的差。 |
| Rolling Window | 滾動窗 | 訓練窗長度固定、隨時間向前滑動的切分方式。 |
| Sharpe Ratio | 夏普比率 | 超額報酬除以波動率的風險調整後績效指標。 |
| Simple Return | 簡單報酬 | 價格變動相對前期價格的百分比變化。 |
| Standard Error | 標準誤 | 估計量本身的標準差,衡量抽樣不確定性。 |
| Stationarity | 定態性 | 時間序列統計性質不隨時間改變的性質。 |
| Survivorship Bias | 倖存者偏誤 | 僅用仍存活標的回測,系統性排除壞結果造成的偏誤。 |
| Synthetic Data | 合成資料 | 以已知模型人工生成、用於教學與測試的資料。 |
| Transaction Cost | 交易成本 | 因交易而產生的手續費、價差與滑價等摩擦成本。 |
| Turnover | 週轉率 | 一段期間內投組部位變動的總量。 |
| Variance | 變異數 | 隨機變數偏離其平均的平方期望值。 |
| Volatility | 波動率 | 報酬的標準差,衡量風險大小。 |
| Walk-forward | 滾動前進驗證 | 反覆以較早資料訓練、緊接區段測試的時序驗證流程。 |
| White Noise | 白噪音 | 平均為零、無自相關、變異數固定的隨機序列。 |
| Yield to Maturity | 到期殖利率 | 使債券未來現金流現值等於市價的折現率。 |
| Zero-coupon Bond | 零息債券 | 不付息、僅到期償還面額的債券。 |

---

如需各符號的數學定義,請參閱 `docs/mathematical_notation.md`;
回測陷阱的詳細說明請參閱 `docs/common_backtesting_mistakes.md`。
