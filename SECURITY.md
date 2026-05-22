# 安全性政策 / Security Policy

本專案是一個教育取向的開源專案。它**不是**正式上線的軟體服務，但我們仍重視
以下幾類問題的負責任回報。

## 回報範圍 / What to report

請回報以下情況：

1. **意外洩漏的機密資訊（secrets）**——例如不慎被提交進倉庫的 API 金鑰、
   token、密碼或憑證。
2. **意外洩漏的個人資訊**——任何不慎被加入的真實人名、email、學號或個人
   背景資料（本專案的隱私政策見
   [`docs/open_source_and_data_policy.md`](docs/open_source_and_data_policy.md)）。
3. **有問題的相依套件**——已知含有漏洞、或來源可疑的相依套件。
4. **惡意程式碼**——任何被提交進倉庫的可疑或惡意內容。

## 如何回報 / How to report

- 對於**機密或個資外洩**：請**不要**開啟公開 issue（那會讓問題更廣為人知）。
  請改用 GitHub 的私下回報機制：在本倉庫的 **Security** 分頁使用
  *"Report a vulnerability"*（Private vulnerability reporting）。
- 對於**相依套件問題**：可開啟一般 issue，並標註 `security` 標籤。
- 回報時請盡量包含：問題描述、受影響的檔案或 commit、以及（若有）建議修法。

## 我們的回應 / Our response

- 我們會儘速確認收到回報。
- 確認的機密外洩會被處理：撤銷該機密、從歷史中移除（必要時），並通知相關方。
- 確認的個資外洩會立即被移除。

## 使用者自我檢查 / Self-check for contributors

提交前，請自行確認你的變更**不包含**：

- 任何真實的機密（金鑰、token、密碼）。
- 任何真實個人資訊。
- 任何下載的第三方市場資料（`data/raw/` 已被 Git 忽略）。

`pre-commit` 設定中包含偵測私鑰與大型檔案的基本檢查，但這**不能取代**你自己的
人工檢查。

---

## English summary

This is an educational open-source project, not a production service. Please
report: accidentally committed **secrets** (keys, tokens, passwords),
accidentally committed **personal information**, **problematic dependencies**,
or malicious code. For secrets or personal-data exposure, **do not open a
public issue** — use GitHub's private vulnerability reporting under the
repository's **Security** tab. Dependency concerns may be filed as a normal
issue tagged `security`. Confirmed exposures are remediated promptly.
