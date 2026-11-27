# ADK-002 進度及恢復

基線為 d744fc4b87e81dabff50f1658695586d6032e571。建立工作分支前，工作樹乾淨且 HEAD、本機 main、origin/main 與 GitHub main 均指向基線。工作分支為 adk/adk-002-trusted-pipeline。origin 儲存 SSH URL，現有操作使用 HTTPS 與 Git Credential Manager。

| 工作包 | 狀態 |
| --- | --- |
| 需求、基線與工作分支 | 已保存需求並完成盤點。見 [ADK-002](requirements/ADK-002.md) 與 [ADR-002](decisions/ADR-002.md)。 |
| 治理與 CI 選型 | 推薦方向獲核准，實際能力仍須逐項驗證。 |
| Draft PR 與 ADK-001 回歸 | 基線提交 bc15010 的 Windows 隔離 gate 通過 10 項測試及工具檢查；已建立 GitHub Draft PR #1。 |
| CI、獨立執行及身分 | 待核准後實跑，記錄 PR head、合併候選與 run、review ID。 |
| 整合 gate、保護規則、Eval | 須以真的 GitHub 及隔離違規案例驗證。 |
| 正式合併與 Athena | 完整驗收前維持 PR 未整合。Athena 產品開發須等待本里程碑。 |

後續應追蹤 Requirement、base、head、PR、run、Review Session、finding、修正輪次、整合決策、Merge SHA 與介入原因。公共紀錄不含憑證或完整 Session 輸出。


## GitHub 實際狀態

- [Draft PR #1](https://github.com/polarbear9218/AI-DevKit/pull/1) 已建立並維持未整合。
- [CI run 46020575099](https://github.com/polarbear9218/AI-DevKit/actions/runs/46020575099) 針對 head 130567123c26345d7284d2749965714f4dc3e269 建立。GitHub annotation 表示帳戶 billing issue 鎖定，runner 未啟動，無測試結果。這是平台阻礙，與刻意注入違規案例無關。
- [Ruleset 28243117](https://github.com/polarbear9218/AI-DevKit/rules/28243117) 已啟用，main API 回報 protected。規則要求 PR、無 bypass、GitHub Actions 原生來源的 Windows engineering gate、至少一個核准、新版本撤銷舊核准、最後推送者之外核准及對話解決，並禁止非快轉更新及刪除。
- [Reviewer 與整合](adk-002-review.md) 入口已加入。獨立執行環境、Reviewer App 授權及非管理員 Program 身分仍須實測。現有管理員憑證僅用於已核准的平台設定操作與 Bootstrap 工作分支。
