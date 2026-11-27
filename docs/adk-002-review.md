# ADK-002 Reviewer 環境與整合

Reviewer 在獨立 Session 及與 Program 憑證隔離的執行邊界中，使用正式 Repository 的唯讀 GitHub 存取。從受信任工作區執行 [Reviewer 入口](../tools/review-pr.ps1)，指定 PR、完整 head SHA 和可寫的隔離暫存目錄。腳本自行取得 PR、base、head、merge candidate 與 check run，並在暫存 checkout 驗證。執行 PR 程式及工具安裝的環境應與持有核准憑證的環境分開。

由治理角色把 `Independent review gate` 加入 active Ruleset，選定已隔離的 Reviewer GitHub App 作為必要來源，保留原生 PR 核准規則。Reviewer App 在同一 head 提交成功 check 與原生核准。整合 gate 從有效 Ruleset 與 check 來源確認 App，再核對該 bot 的原生 approval 與 commit ID。App 實際核准計數、check 發布和舊核准撤銷仍待實測。

以 `python -m adk integrate OWNER/REPO PR SHA` 查詢即時資格。使用無管理權的 `ADK_PROGRAM_TOKEN`，明確指定 `--apply` 才嘗試合併。Merge 請求綁定 head SHA，並由 GitHub 平台檢查 PR 保護。資格不足即阻擋。

Hosted Windows 已驗證正常與違規 CI。獨立 Reviewer 自主取得精確版本、差異與 job log，也確認原兩項 P1 程式修正。其執行政策仍阻止本機測試。正式整合待驗證隔離執行環境、平台身分及完整生命週期。[驗收狀態](adk-002-status.md)


## 身分與執行邊界決策

| 候選 | 成本及風險 |
| --- | --- |
| 私有 Reviewer App，搭配獨立暫存執行環境 | 推薦。只安裝到 AI-DevKit，最小權限為 Contents read、Pull requests write、Checks write。測試程序在無憑證環境執行，App 簽發與發布在分離的憑證邊界。需 Account Owner 完成註冊授權及限定範圍，另需實測原生核准計數。 |
| 獨立具 write 權限的 Reviewer 帳號 | 原生核准有較直接的帳號模型，持有較大的 Repository 權限，且仍需獨立 execution boundary。現行 gate 仍需受信任 App check 綁定。需另行核准相關架構。 |
| 由 Reviewer 發起現有 GitHub Actions 重跑 | 可重跑相同 SHA 和 ref，但沿用原觸發者權限，屬獨立執行的補充證據。此方案需授權 Actions write。現有 Session 的 Connector 實測在 Runtime 核准層即被拒絕。 |
| 隔離 VM 或新帳號下的受管 Windows 執行 | 與既有 Windows gate 相容。需要實際可用的隔離主機或執行配額，由憑證管理者確認成本與邊界。正式來源使用公開唯讀 checkout。 |

Program 採獨立非管理員 GitHub collaborator，只在分離環境注入限 AI-DevKit 的短期 GitHub 認證，驗證 push 為 true 且 admin 為 false，再驗證該環境無法讀取管理員 GCM 及 Reviewer App 認證。現有 Program 的 Windows profile 無法提供所需隔離。GitHub App 安裝及實際帳號需由權限持有人授權。此提案沒有新增付費服務。

正式 PR 維持 Draft。取得合法身分後，先以隔離測試 PR 驗證相同 head 正常核准、缺陷拒絕、App check 來源、更新 head 撤銷舊核准、CI 失敗與未授權合併。只有這些結果、正式 Reviewer 的最新核准及兩種平台 check 均可驗證時，才對 PR #1 使用 SHA 綁定的 gate。

[App manifest 與帳戶授權](https://docs.github.com/en/apps/sharing-github-apps/registering-a-github-app-from-a-manifest) · [原生 Review API](https://docs.github.com/en/rest/pulls/reviews#create-a-review-for-a-pull-request) · [Actions 重跑權限](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
