# ADK-002 Reviewer 環境與整合

Reviewer 在獨立 Session 及與 Program 憑證隔離的執行邊界中，使用正式 Repository 的唯讀 GitHub 存取。從受信任工作區執行 [Reviewer 入口](../tools/review-pr.ps1)，指定 PR、完整 head SHA 和可寫的隔離暫存目錄。腳本以 GitHub PR API 及 Git ref 自行取得 source、base、head、merge candidate 和 check run，並在暫存 checkout 驗證。正式來源僅讀取。執行 PR 程式和工具安裝的環境不應持有 Reviewer 核准憑證；核准的身分與憑證應位於獨立授權邊界。

待 Reviewer 環境及身分落地後，核准需綁定 PR head，並確認該核准實際符合 GitHub ruleset。以 `python -m adk integrate OWNER/REPO PR SHA` 查詢即時資格，明確指定 `--apply` 才嘗試合併。使用 Provision 後的 `ADK_REVIEWER_LOGIN` 與非管理員 `ADK_PROGRAM_TOKEN`。合併用 GitHub 平台規則重新檢查，並以同一個 SHA 綁定請求。資格不足即阻擋。

目前測試驗證正常資料、CI 失敗／錯誤來源、舊版核准、拒絕審查、自審、缺保護、錯誤分支及 draft/conflict。這些是 deterministic gate tests。真實自主 Merge 仍受 CI billing lock 與獨立身分配置阻礙。
