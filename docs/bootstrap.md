# ADK-001 進度與恢復入口

| 工作包 | 依賴 | 狀態與驗收證據 |
| --- | --- | --- |
| 盤點、保存需求及知識入口 | 無 | 已盤點空 Repository。原始訊息包含 33 節。 |
| 技術研究與治理決策 | 盤點 | ADR-001 已有條件核准。工具實跑結果見驗證紀錄。 |
| 工程核心及 Feature Map | ADR-001 核准 | 已實作初期 CLI、Feature Map 與 gate，Windows 驗證與違規回歸已執行。 |
| Harness、獨立 Review 與回饋 | 核心與可追溯版本 | Windows 獨立 Session 已執行靜態審查並辨識隔離缺陷。版本 gate 及介入紀錄已建立。 |
| Agent Evals 與 dogfooding | 工程核心與審查能力 | 已建立基線並完成巢狀模組漏檢的真實改善閉環，見 [Eval 基線](../evals/baseline.md)。 |
| 最終驗收與 Athena 準備度 | 前述工作包 | Windows MVEE 已通過同版 gate 與獨立複審，見 [最終驗收](acceptance.md)。 |

初次盤點顯示 main 尚無 commit，工作目錄只有 .git，未設定 remote。實測 Python 3.12.0、Node.js 20.18.0、Git 2.44.0.windows.1、Codex CLI 0.172.0。工作區採唯讀 Sandbox。版本化基線以第一次成功的 Git commit 為準。

ADR-001 已有條件核准。恢復時先確認分支、驗證覆蓋與尚待處理的審查 finding。已完成 Windows MVEE 驗收，過程證據見 [ADK-001 執行紀錄](evidence.md)。

## 基線驗證

- 以目前 Session 的原始使用者訊息核對需求副本。原文共 33 節，寫入後逐字比對一致。
- 以 Python 3.12.0 檢查五份工程入口及提案文件內的 8 個本機 Markdown 引用，全部可解析。
- 本機寫入依管理式 Sandbox 的命令核准流程執行。專案重大架構及工具取捨另由 ADR 治理決策記錄。


## GitHub 版本整合

- 本機分支為 main，初始文件基線為 17e6647。本機 origin 已設定為指定的 GitHub SSH URL。
- 整合前透過 GitHub HTTPS 查詢，未回傳任何遠端 refs。SSH 查詢遭拒絕，使用現有 HTTPS 憑證進行推送試跑也遭拒絕。需完成推送認證，並以實際遠端 main SHA 核對本機提交。
- 推送前以 Git 檢查空白差異及檔案範圍，並掃描常見憑證格式。ADR-001 仍為 Proposed，ADK-001 仍為部分完成。


Git Credential Manager 重新登入後，HTTPS 推送試跑確認可新建 main。保留指定的 SSH origin；此輪透過同一 Repository 的 HTTPS 位址執行一般推送。推送後以遠端 main ref、origin/main 與本機 HEAD 三方比對驗證。SSH 認證仍待建立。
