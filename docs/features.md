# Feature Map

- [ADK-101 Feature Map 探索](../features/ADK-101.json)
- [ADK-102 工程政策與驗證](../features/ADK-102.json)
- [ADK-103 Agent Eval 結果判定](../features/ADK-103.json)

每項功能以 features 下的一份 UTF-8 JSON 記錄為準。檔名與 id 一致，採大寫字母開頭、可含數字的前綴與三位數字後綴。必填 id、name、purpose、status、behavior、requirements，狀態為 planned、implemented、deprecated。implemented 必填非空 entrypoints、code、verification。選填 aliases、dependencies、preconditions、invariants、side_effects、security、adrs、references。除五個文字欄位外，其餘欄位以文字陣列表示。dependencies 使用 Feature ID，引用使用 Repository 根目錄相對檔案路徑。入口可包含人類或 Agent 使用的命令，實際行為由對應測試確認。

新功能以[範本](feature-template.json)建檔，再更新此索引。執行 `python -m adk features` 探索全部記錄，或加上識別碼、名稱或別名查詢。執行 `python -m adk check` 核對結構、引用與依賴。Athena 和 Hydra 各自維護功能資料。

- [ADK-104 GitHub PR 工程驗證](../features/ADK-104.json)

- [ADK-105 PR 整合資格驗證](../features/ADK-105.json)
