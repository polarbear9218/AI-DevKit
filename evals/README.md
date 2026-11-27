# Agent Eval

案例的 checks 定義獨立預期觀察，執行後以機器取證建立包含 session 與 observations 的本機 JSON。執行 `python -m adk eval CASE OBSERVATIONS`，每個欄位回傳實際比較結果，任何缺失或差異使程序失敗。Session ID 應從 Runtime 取得，判定資料由主持者核對真實輸出及 Git，Agent 的自述可提供線索。

本輪使用 [核心行為案例](engineering.json)，衡量 Feature Discovery、Architecture Compliance、Autonomous Verification、Autonomous Recovery、Governance Compliance、Self-documenting Code 及 Honest Failure Reporting。Independent Review Accuracy、Implementation Integrity 與 Problem Evasion Detection 需要獨立審查植入缺陷案例及其證據。新一輪使用未參與規則調整的案例。


實際執行與判定記錄見 [基線](baseline.md)。
