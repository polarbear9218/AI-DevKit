# ADK-001 執行紀錄

| 節點 | 階段 | 實際觀察 |
| --- | --- | --- |
| cf18105 | 恢復 | 遠端 HTTPS HEAD 與本機 main 一致。工作區已有未提交的 Python 政策、Feature Map 核心與工具暫存，續作保留並驗證。 |
| ADR-001 | Governance Decision | 負責人有條件核准工具與本機架構。原始驗收條件維持。 |
| 4ca02e3 | Program | Windows 上 5 項 unittest 通過，Ruff、mypy strict、Gitleaks 快照通過。安裝器以 SHA-256 驗證發布 zip，pip check 無相依衝突。 |
| 4ca02e3 | Review | Codex CLI 0.172.0 的獨立唯讀 Session 已啟動。Windows 執行政策拒絕 PowerShell 和 cmd.exe 讀取，未完成檔案審查。 |
| 4ca02e3 → 改善 | Program | 孤立巢狀模組被舊政策漏檢，新政策報告未登錄模組。新增回歸測試，最新工具 gate 7 項 unittest 通過。 |
| 改善 | Program | Gitleaks 首次合成憑證案例的重複字串未達偵測條件。此輸出視為測試失敗。 |

一般作業由 Agent 執行。這輪負責人介入屬治理決策。Windows Reviewer 的讀取障礙屬環境能力缺口，改善候選為向獨立 Session 提供經掃描、與 SHA 綁定的精簡材料。管理式 Sandbox 寫入依命令核准流程執行。
