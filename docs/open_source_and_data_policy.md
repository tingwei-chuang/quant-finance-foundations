# 開源與資料政策 / Open-Source and Data Policy

本文件說明本專案在**開源發布**、**版權**、**隱私**與**市場資料**上的政策。
所有貢獻者與使用者都應遵守。

---

## 1. 教育與研究用途免責聲明

- 本專案僅供**教育與研究方法論**用途。
- 本專案**不構成投資建議**。
- 任何 notebook 的結果**都不應被解讀為**實際可獲利、可投資或經過驗證的策略。
- 本專案刻意聚焦於**正確的評估方法論**，而非追求績效。

---

## 2. 隱私政策

本倉庫為公開發布。為保護隱私：

- **不**包含任何真實人名。
- **不**提及任何學校就學狀態、成績、個人職涯規劃、電子郵件、學號、私人專案
  歷史或個人背景。
- 目標學習者一律以通用方式描述為：
  > 「具備程式設計經驗、準備量化金融與系統化研究課程的學習者」
  > （a learner with programming experience preparing for quantitative finance
  > and systematic research coursework）。

若你在貢獻時不慎加入個人資訊，請見 [`SECURITY.md`](../SECURITY.md) 的回報流程。

---

## 3. 版權與內容政策

- **不**下載、重製、轉錄、抓取 (scrape) 或再散布任何影片、講義投影片、教科書
  或受版權保護的習題集。
- 可以**連結**到官方教育資源（見 [`resources.md`](resources.md)）。
- 所有解說、範例、習題與解答皆為**原創**撰寫。
- 推薦的外部學習資源以其**官方標題與官方網址**清楚標註。
- 本專案不宣稱外部課程的確切影片編號或章節結構；除非能由官方頁面驗證，
  否則僅連結到課程首頁並以通用方式描述主題。

---

## 4. 市場資料政策

- **不**將下載的第三方市場價格資料提交進本倉庫。
- 預設的 notebook 與測試**完全使用合成資料**與小型、本專案自有的範例資料集
  執行，不需要網路連線。
- 合成資料由 `scripts/generate_synthetic_dataset.py` 產生，使用固定且有文件
  記載的亂數種子，因此完全可重現。
- 選用的真實資料工作流程僅以**腳本或說明**提供
  （見 `scripts/optional_download_market_data.py`）。
- 任何下載資料的目錄（`data/raw/`）都被 Git 忽略。
- **使用者須自行負責遵守各資料供應商的使用條款。** 許多供應商禁止重新散布。

資料目錄的詳細說明請見 [`../data/README.md`](../data/README.md)。

---

## 5. 授權

- 本專案採用 **MIT License**（見 [`LICENSE`](../LICENSE)），除非某個實作相依套件
  另有要求。
- 選用相依套件 `cvxpy` 若被使用，本專案另提供 numpy/scipy 的 fallback；
  詳見 Week 2 notebook 與 `pyproject.toml`。

---

## 6. 貢獻者責任

提交 pull request 前，請確認你的變更：

- 不含任何真實個人資訊；
- 不含任何下載的第三方市場資料；
- 不加入任何投資獲利宣稱；
- 不重製任何受版權保護的教育材料；
- 通過 `ruff`、`pytest` 與 notebook 驗證。

詳見 [`../CONTRIBUTING.md`](../CONTRIBUTING.md)。

---

## English summary

This repository is released publicly under the **MIT License** for **education
and research methodology only** — it is **not investment advice** and makes no
claim of trading profitability. **Privacy:** no real names or personal details
appear anywhere; the target learner is described generically. **Copyright:** no
copyrighted videos, slides, textbooks, or problem sets are downloaded,
transcribed, scraped, or redistributed — only official resources are linked,
and all explanations and exercises are original. **Market data:** no
third-party price data is committed; notebooks and tests run offline on
reproducible synthetic data, the optional real-data folder (`data/raw/`) is
git-ignored, and users are solely responsible for complying with each data
provider's terms of use.
