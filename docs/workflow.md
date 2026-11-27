# 工程工作流

1. 從需求與 [Feature Map](features.md) 探索範圍，記錄 Git base 與當前分支。
2. 實作後執行 [統一驗證](verification.md)。保留失敗分類、修正及重跑證據，更新受影響的功能記錄。
3. 提交目標版本後，把 base、target、需求、驗證輸出與工具版本交給唯讀獨立 Review Session。用 Git SHA 核對 diff。Reviewer 提供可定位的 finding、嚴重度、證據與狀態。變更 target 後重跑必要 gate 及審查。
4. 整合前確認目前 target、無阻擋 findings、驗證與版本一致，再做普通 fast-forward。Public Repository 推送前檢查敏感內容。保留本機分支和 commit 作為恢復點。

任務紀錄使用 task、role、runtime、base、target、operation、outcome、duration、status。Runtime 提供 token 用量時才納入。紀錄必要摘要與證據引用，完整輸出及私人資料留於本機。介入紀錄使用 task、phase、category、reason、evidence、root cause、outcome、avoidable、improvement。

改善從觀察與根因開始，選擇可強制的工程階層，執行程式驗證或 Agent Eval，再依結果決定可否委派。Agent Eval 衡量實際 Session 是否解決任務及誠實報告；軟體測試衡量程式行為。

使用 [Program](../.agents/skills/program/SKILL.md)、[Review](../.agents/skills/review/SKILL.md)、[Research](../.agents/skills/research/SKILL.md) 工作流程。
