# 折現與債券 (Discounting and Bonds)

> 教育與研究方法用途說明：本文件僅為量化金融基礎教育與研究方法之教材，**不構成任何投資建議**，文中數字皆為說明用途，不宣稱任何交易獲利能力。

## 1. 動機

「今天的一元」與「一年後的一元」價值不同——這是金融學最核心、也最容易被低估的一句話。所有的估值（股票、債券、衍生品、專案）本質上都是把未來現金流折算回今天。

對一位**具備程式設計經驗、準備量化金融與系統化研究課程的學習者**而言，掌握 time value of money（貨幣的時間價值）與 discount factor（折現因子）是進入固定收益與選擇權定價的必經之路。本文件用最小的數學量，把折現、present value、債券定價、yield to maturity 與 zero-coupon bond 串起來。

## 2. 定義

- **time value of money（貨幣的時間價值）**：相同名目金額，越早收到價值越高。
- **discount factor（折現因子）**：把某一未來時點的一元換算為今日價值的乘數，介於 0 與 1 之間。
- **present value, PV（現值）**：未來現金流以折現因子加總後的今日總價值。
- **bond cash flows（債券現金流）**：債券持有期間按期收到的 coupon（票息），到期時收回 face value（面額）。
- **yield to maturity, YTM（到期殖利率）**：使債券所有現金流現值總和等於市場價格的單一折現率。
- **zero-coupon bond（零息債券）**：不付票息，僅到期償付面額的債券。

## 3. 核心公式

折現因子（年化利率 $r$，距今 $t$ 年）：

$$ DF(t) = \frac{1}{(1 + r)^{t}} $$

若一年複利 $m$ 次：$DF(t) = \left(1 + \tfrac{r}{m}\right)^{-mt}$；連續複利：$DF(t) = e^{-rt}$。

一組未來現金流 $\{C_1, C_2, \dots, C_n\}$ 的 present value：

$$ PV = \sum_{k=1}^{n} \frac{C_k}{(1 + r)^{t_k}} = \sum_{k=1}^{n} C_k \cdot DF(t_k) $$

附息債券價格（票息 $C$，面額 $F$，期數 $n$，每期殖利率 $y$）：

$$ P = \sum_{k=1}^{n} \frac{C}{(1 + y)^{k}} + \frac{F}{(1 + y)^{n}} $$

zero-coupon bond 價格：

$$ P_{\text{zero}} = \frac{F}{(1 + y)^{n}} $$

YTM 為下式的解（無封閉解，需數值求根）：

$$ P_{\text{market}} = \sum_{k=1}^{n} \frac{C}{(1 + y)^{k}} + \frac{F}{(1 + y)^{n}} $$

## 4. 直覺解釋

折現因子可以想成「未來一元的今日標價」。利率越高、時間越久，這個標價越低——因為你若現在就有錢，可以拿去賺利息，所以未來才拿到的錢必須打折。

債券價格就是「把所有未來票息與面額的標價加起來」。YTM 則是反過來問：「市場現在開這個價，等於用哪一個折現率？」它是一個把整條現金流壓縮成單一數字的「內部報酬率」。

**為什麼 bond price 隨 yield 上升而下跌？** 因為價格是現金流除以 $(1+y)^k$。債券的票息與面額在發行後是**固定**的（分子不變），當市場要求的 yield 上升時，分母變大，每一筆現金流的現值都縮水，加總後的價格自然下跌。兩者呈反向關係，這是固定收益最根本的直覺。期限越長的債券，對 yield 變動越敏感。

## 5. 一個小範例

考慮一張 3 年期、面額 $F = 100$、年票息率 5%（即每年 $C = 5$）的附息債券。

若市場 yield $y = 5\%$（等於票息率）：

$$ P = \frac{5}{1.05} + \frac{5}{1.05^2} + \frac{105}{1.05^3} = 4.762 + 4.535 + 90.703 = 100.00 $$

債券恰好以面額（par）交易。

若 yield 上升到 $y = 7\%$：

$$ P = \frac{5}{1.07} + \frac{5}{1.07^2} + \frac{105}{1.07^3} = 4.673 + 4.367 + 85.712 = 94.75 $$

yield 從 5% 升到 7%，價格從 100 跌到約 94.75，**反向關係**清楚可見。

zero-coupon 對照：同樣 3 年、面額 100、$y = 7\%$ 的零息債券價格為 $100 / 1.07^3 \approx 81.63$。

## 6. 常見實作錯誤

- 折現時 **複利頻率 (periods-per-year) 不一致**：票息半年付一次，卻用年化率直接折現。
- 把年化 yield 直接當成每期 yield，未除以每年期數。
- 計算 PV 時漏掉最後一期的 **face value**，只折現了票息。
- 時間單位混用：$t$ 用「年」但利率用「每期」。
- 求 YTM 時忽略其為數值解，誤以為有簡單封閉公式；或求根初始值太差導致不收斂。
- 把 coupon rate（票息率）與 YTM 混為一談——只有債券以 par 交易時兩者才相等。
- 忘記 yield 與 price 反向：看到 yield 上升卻預期 price 上升。

## 7. 完成度檢查清單

- [ ] 我能解釋 discount factor 為何介於 0 與 1，以及它如何隨利率與時間變化。
- [ ] 我能手算一組現金流的 present value。
- [ ] 我能寫出附息債券的定價公式並指出票息與面額兩部分。
- [ ] 我能用具體數字說明「yield 上升 → bond price 下跌」。
- [ ] 我能說明 zero-coupon bond 與附息債券定價的差異。
- [ ] 我能解釋 YTM 的意義，並知道它需要數值求根。
- [ ] 我能正確處理複利頻率與時間單位的一致性。

## 8. 延伸連結

- 課程 notebook：[notebooks/06_financial_mathematics_and_option_pricing.ipynb](../../notebooks/06_financial_mathematics_and_option_pricing.ipynb)
- 可重用程式碼：`quant_math_roadmap.finance.fixed_income`（`discount_factor`、`present_value`、`bond_price`、`zero_coupon_bond_price`、`yield_to_maturity`）。
- 官方外部學習資源：國立臺灣大學開放式課程「基礎財金素養」，<https://ocw.aca.ntu.edu.tw/courses/110S204>
