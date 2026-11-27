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


## 真實改善任務 ADK-001-GUARDRAIL

依原始需求 §9、§11、§22、§27，從 ADK-101 查詢 catalog 定位政策檢查與 Feature Map。base 為 4ca02e3da67faa5e179367e3171fa6e74740f3ad。隔離案例顯示舊版允許未登錄巢狀模組，根因是架構依賴只驗證頂層已知 Python 模組。修正後拒絕未登錄模組，並更新功能記錄及回歸測試。b7cc3af2670448c0f79952cc3a34deda203fefa4 的 Windows gate 從乾淨分支執行並通過 7 項 unittest。新規則可委派給靜態檢查。

Gitleaks 合成憑證案例改用雜湊生成的假樣本，偵測後回傳 1。樣本在暫存目錄，只有遮罩後的結果用於判定。根因是第一次的低變異樣本未觸發偵測。採用實際偵測結果改善案例，未修改掃描規則。

## Agent Eval 基線及獨立審查

真實 Program Session 對 b7cc3af 執行核心案例，輸出 7/7。可核對的觀察為 ADK-101 查詢結果、舊版／新版架構案例、gate exit 0、有條件核准紀錄、註解拒絕和診斷。觀察由命令輸出取得；治理項目只涵蓋本輪核准紀錄，沒有跨情境的泛化結論。

獨立 Codex Session 針對 base cf181054e36f8ecc79b96e2a968b9f143dd1d27b、target b7cc3af2670448c0f79952cc3a34deda203fefa4 的提交資料進行唯讀靜態審查。Windows 工具政策限制該 Session 執行 Git 或測試，因此 Program 提供掃描過的 commit diff、原始需求和測試摘要。Reviewer 判定尚缺真實 Eval 基線、閉環紀錄及乾淨版本驗證。Reviewer 亦拒絕隔離提案將錯誤斷言改成恆真斷言，指出會失去對 load_catalog 回傳值的直接驗證。隔離提案未寫入 Git。結果支援 Review Accuracy、Implementation Integrity 和 Problem Evasion Detection 的初步觀察。

介入紀錄：階段為工具決策，類型為 Governance Decision，原因是首次引入架構與工具，相依證據為 ADR-001，結果為有條件核准，屬刻意保留的治理步驟。獨立審查命令遭拒屬工程環境限制，Program 改以限定公開範圍的提交資料供獨立 Session 靜態審查，由於審查讀取能力有限，版本證據由程式 gate 綁定。兩者皆有各自的追溯紀錄，沒有請負責人執行一般工程步驟。

Athena 現可試用通用 Feature Map 與 Windows gate。正式整合仍需確認 ADK 最終目標版本的獨立審查、未見案例覆蓋及可重跑安裝，Athena 自身的產品驗證另依 Pilot 工作執行。
