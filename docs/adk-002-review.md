# ADK-002 Reviewer 環境與整合

Reviewer 在獨立 Session 及與 Program 憑證隔離的執行邊界中，使用正式 Repository 的唯讀 GitHub 存取。從受信任工作區執行 [Reviewer 入口](../tools/review-pr.ps1)，指定 PR、完整 head SHA 和可寫的隔離暫存目錄。腳本自行取得 PR、base、head、merge candidate 與 check run，並在暫存 checkout 驗證。執行 PR 程式及工具安裝的環境應與持有核准憑證的環境分開。

由治理角色把 `Independent review gate` 加入 active Ruleset，選定已隔離的 Reviewer GitHub App 作為必要來源，保留原生 PR 核准規則。Reviewer App 在同一 head 提交成功 check 與原生核准。整合 gate 從有效 Ruleset 與 check 來源確認 App，再核對該 bot 的原生 approval 與 commit ID。App 實際核准計數、check 發布和舊核准撤銷仍待實測。

以 `python -m adk integrate OWNER/REPO PR SHA` 查詢即時資格。使用無管理權的 `ADK_PROGRAM_TOKEN`，明確指定 `--apply` 才嘗試合併。Merge 請求綁定 head SHA，並由 GitHub 平台檢查 PR 保護。資格不足即阻擋。

Hosted Windows 已驗證正常與違規 CI。獨立 Reviewer 自主取得精確版本、差異與 job log，也確認原兩項 P1 程式修正。其執行政策仍阻止本機測試。正式整合待驗證隔離執行環境、平台身分及完整生命週期。[驗收狀態](adk-002-status.md)
