# 工程規範

| 規範 | 狀態 | 範圍、要求與強制方式 |
| --- | --- | --- |
| 架構依賴 | Accepted | 核心依賴依模組準則，政策檢查驗證明示匯入。 |
| 格式、lint、型別 | Accepted | ADK Python 與測試採倉庫 Ruff 設定及 mypy strict，由 verify 執行。 |
| 註解及抑制 | Accepted | Python 僅允許第一行指定 shebang、前兩行 UTF-8 宣告、前五行 SPDX；公開契約 Docstring 以 Contract: 開頭。拒絕未授權抑制。 |
| 驗證與實作完整性 | Accepted | 按實際行為測試正常與違規案例。禁止以測試跳過、預期失敗或箝制工具規則取得通過；語意與覆蓋由 Review 判斷。 |
| Feature Map 與工程引用 | Accepted | 功能紀錄維護結構、引用與依賴。Markdown inline 相對檔案引用須可解析。 |
| Context 與工程文字 | Accepted | README 與 AGENTS 為入口，決策、預期與證據分別保留。 |
| Agent 治理、Git | Accepted | 依治理邊界執行，版本及審查需相符。保護既有歷史及成果。 |
| 安全 | Accepted | 公開推送前做 Gitleaks 遮罩掃描與人工內容判斷，依最小權限處理外部資料。 |
| 持續改善 | Accepted | 依問題、根因、修正、證據及委派判斷建立改善記錄。 |

狀態定義及強制標準見 [工程原則](foundation.md)。
