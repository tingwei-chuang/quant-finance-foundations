# 外部學習資源 / External Learning Resources

本文件整理本路線圖建議的官方／公開教育資源。

> **使用原則**
> - 以下連結僅作為**外部參考**。本專案**不**下載、不重製、不轉錄、不抓取、
>   也不再散布任何影片、講義、教科書或習題集。
> - 所有解說、範例、習題與解答皆為本專案**原創**。
> - 請自行遵守各資源網站的使用條款。
> - 各資源依其官方頁面標題與網址標註；本文件不宣稱確切的影片編號或章節結構，
>   實際內容請以官方頁面為準。

每個資源標註：**用途**、**對應週次**、以及是 **核心 (core)** 或 **選用 (optional)**。

---

## 1. 統計與計量經濟 (Statistics and econometrics)

### NTU OpenCourseWare — 統計學一上與計量導論
- **機構 / 作者**：國立臺灣大學開放式課程（NTU OpenCourseWare）
- **官方網址**：<https://ocw.aca.ntu.edu.tw/courses/112S103>
- **用途**：複習敘述統計、機率、估計與假設檢定，並建立計量經濟與迴歸的入門基礎。
- **對應週次**：Week 4（統計推論）、Week 5（迴歸與因子模型）。
- **核心 / 選用**：**核心 (core)**。

---

## 2. 機率與統計習題 (Probability and statistics exercises)

### MIT OpenCourseWare — 18.05 Introduction to Probability and Statistics
- **機構 / 作者**：MIT OpenCourseWare
- **官方網址**：<https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/>
- **用途**：複習隨機變數、期望值、條件機率與 Bayes 規則、信賴區間、假設檢定；
  作為機率與推論的練習來源。
- **對應週次**：Week 3（機率複習）、Week 4（統計推論）。
- **核心 / 選用**：**核心 (core)**。

---

## 3. 線性代數 (Linear algebra)

### MIT OpenCourseWare — 18.06SC Linear Algebra
- **機構 / 作者**：MIT OpenCourseWare
- **官方網址**：<https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/>
- **用途**：複習向量、矩陣、特徵值與特徵向量、最小平方、quadratic form；
  支撐共變異數矩陣與 OLS 的理解。
- **對應週次**：Week 1（線性代數）、Week 5（OLS 矩陣形式）。
- **核心 / 選用**：**核心 (core)**。

---

## 4. 多變數微積分 (Multivariable calculus)

### MIT OpenCourseWare — 18.02SC Multivariable Calculus
- **機構 / 作者**：MIT OpenCourseWare
- **官方網址**：<https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/>
- **用途**：複習偏微分、梯度、Hessian、Taylor 近似、約束最佳化；支撐最小變異
  投資組合的最佳化。
- **對應週次**：Week 2（多變數微積分與最佳化）。
- **核心 / 選用**：**核心 (core)**。

---

## 5. 財金基礎 (Finance foundations)

### NTU OpenCourseWare — 基礎財金素養
- **機構 / 作者**：國立臺灣大學開放式課程（NTU OpenCourseWare）
- **官方網址**：<https://ocw.aca.ntu.edu.tw/courses/110S204>
- **用途**：建立貨幣時間價值、折現、債券、報酬與風險、衍生性商品 payoff 的
  財金基礎概念。
- **對應週次**：Week 1（報酬與風險）、Week 6（財務數學與選擇權）。
- **核心 / 選用**：**核心 (core)**。

---

## 6. 時間序列預測 (Time-series forecasting)

### Forecasting: Principles and Practice, the Pythonic Way
- **機構 / 作者**：Hyndman 等人；Pythonic 版線上書
- **官方網址**：<https://otexts.com/fpppy/>
- **用途**：學習時間序列的探索、診斷與預測評估，特別是走動式 (walk-forward)
  評估的正確做法。
- **對應週次**：Week 7（時間序列診斷）、Week 8（走動式預測與回測完整性）。
- **核心 / 選用**：**核心 (core)**。

---

## 7. 時間序列補充參考 (Additional time-series reference)

### Penn State STAT 510 — Applied Time Series Analysis
- **機構 / 作者**：Pennsylvania State University（線上課程教材）
- **官方網址**：<https://online.stat.psu.edu/stat510/>
- **用途**：補充定態性、ACF/PACF、AR/MA/ARIMA 等時間序列分析的理論細節。
- **對應週次**：Week 7（時間序列診斷）、Week 8。
- **核心 / 選用**：**選用 (optional)**，作為較深入的補充。

---

## 不該做的事 (What not to do)

- 不要把下載的課程影片內嵌進本倉庫。
- 不要鏡像 (mirror) 講義投影片。
- 不要重製外部習題集。
- 不要抓取 (scrape) 全文。

如需以真實市場資料練習，請見 [`open_source_and_data_policy.md`](open_source_and_data_policy.md)
與 `scripts/optional_download_market_data.py`。

---

## English summary

This guide links **official, public** educational resources only — the
repository never bundles, mirrors, transcribes, or scrapes any copyrighted
course material. Core resources: MIT OCW 18.06SC (linear algebra), 18.02SC
(multivariable calculus), 18.05 (probability & statistics); NTU OCW 112S103
(statistics & introductory econometrics) and 110S204 (finance foundations);
and *Forecasting: Principles and Practice, the Pythonic Way* (time-series
forecasting). Penn State STAT 510 is listed as an optional, deeper time-series
reference. Each entry states its purpose, the roadmap week it maps to, and
whether it is core or optional. Always comply with each site's terms of use.
