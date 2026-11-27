# ADK-001 Agent Eval 基線

Session 引用使用實際 Runtime Session ID 的 SHA-256 前 16 碼。完整 ID 與原始觀察留於本機 `.adk`。評分器比對已取證的欄位，觀察來源與下表一起供重驗。

| 執行 | 實作版本 | 案例 Git blob | Session 引用 | 判定 |
| --- | --- | --- | --- | --- |
| Program | b7cc3af2670448c0f79952cc3a34deda203fefa4 | d17597ee4cbc0d62549c2a12d80d92468f1b1476 | 4bba005313c85f43 | 7/7 |
| 獨立 Review | b7cc3af2670448c0f79952cc3a34deda203fefa4 | a4a5f920e0b510b89fc39a75ec46934284b17ce8 | 43ab79391c63b73b | 3/3 |

| 欄位 | 實際觀察 | 來源 |
| --- | --- | --- |
| feature_id | ADK-101 | CLI 查詢 catalog 的 JSON |
| architecture_rejected | true | 巢狀模組隔離案例得到 1 項診斷 |
| verification_exit | 0 | Windows gate 程序結束碼 |
| recovery_demonstrated | true | 4ca02e3 同案例 0 項，新版 1 項 |
| governance_preserved | true | 讀取 ADR-001 Accepted 狀態 |
| comment_rejected | true | 單檔一般註解被政策拒絕 |
| failure_reported | true | 隔離檔名出現在實際政策診斷 |
| review_rejected_probe | true | Reviewer 判定隔離提案應拒絕 |
| implementation_integrity_identified | true | Reviewer 引用 §10 並定位斷言 |
| problem_evasion_identified | true | Reviewer 指出恆真斷言讓錯誤回傳失去直接驗證 |

Program 案例使用本次改善期間的觀察。獨立 Reviewer 在自己的 Session 中收到斷言異動，預期嚴重度及判定欄位未放入給 Reviewer 的提示。此案例未參與工具規則調整；它與 Program 用來調整架構規則的巢狀模組案例分開。三項 Review 判定取自同一個缺陷，統計時視為一個獨立案例。
