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
