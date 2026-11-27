# ADK-002 驗收狀態

狀態為 **Partial，正式整合受阻**。基線 d744fc4b87e81dabff50f1658695586d6032e571。[正式 Draft PR #1](https://github.com/polarbear9218/AI-DevKit/pull/1) 仍待完整驗收。

| 能力 | 實際驗收與限制 |
| --- | --- |
| Branch、PR、main 保護 | 正式修改在 adk/adk-002-trusted-pipeline。Ruleset 28243117 為 active，無 bypass，要求必要 CI、至少一個最新審查、解決對話，禁止非快轉與刪除。相同規則的短期分支實測拒絕直接 push，返回 GH013，main 未被用作破壞性測試。 |
| 正常 CI | Run 46022746954 在 head 27fea12debf5a826fad32c9583e6abfd1f58e28f、合併候選 51c8ff166a93e413949263a1e272f5ed0786e387 全數通過。前次 46021718044 失敗原因為政策路徑誤判，已新增根目錄正規化的回歸。 |
| 違規 CI | 隔離 [PR #2](https://github.com/polarbear9218/AI-DevKit/pull/2) 的 [run 46022869213](https://github.com/polarbear9218/AI-DevKit/actions/runs/46022869213) 以 exit 1 拒絕測試檔第 1 行一般註解。CI job 140586691661 提供診斷。測試 PR 已關閉且未合併。 |
| Independent Review | Reviewer 由 GitHub Connector 自主取得 PR、diff、需求與 job log，找到路徑與身分兩項缺口。重試正式工作區外暫存，Runtime 仍以 read-only 套用政策，拒絕 Git 與 Python 程序。Program 實跑獨立取證腳本取得真正合併候選並通過，執行證據歸 Program。 |
| Identity 與 Integration | 本機 gate 只接受 Ruleset 指定 App 的 check 與同 SHA 的原生核准，以 head SHA 綁定 merge 請求。現有 Program 認證為管理員，不可供正式 merge 使用。Reviewer App 尚未安裝及綁定，尚未驗證 App 核准被原生審查計數。正式 PR 維持草稿，不呼叫 merge。 |
| Agent Eval | 兩個未參與規則調整的隔離 Reviewer 案例均正確，含拒絕與核准。Seed 的基線及 17 項本機 Software Verification 通過。跨 Session 一致性、原生審查過期、自主 merge 及恢復的端到端結果仍待執行。 |
| 介入及回饋 | 負責人核准 ADR-002 方向與平台規則。第一次 run 在 runner 配置前遇到 billing lock，後續 runner 已成功啟動。正式隔離身分及 Reviewer 可合法啟動測試的環境仍是授權／環境阻礙。 |

## 恢復條件

建立與 Program 憑證隔離的 Reviewer 執行環境，啟用可持有獨立 App 的授權邊界。App 需能讀取 Contents、寫入 Pull requests 與 Checks。以隔離 PR 驗證核准計數、App check 綁定與新版本撤銷。取得非管理員 Program 身分，只有專案 Contents 與 Pull requests 需要的權限。確認管理認證與 Reviewer 憑證皆無法從 Program 環境取得。

確認 Reviewer 能執行隔離候選驗證後，重新審查正式 PR 的最新 head，並以真正的 GitHub 保護、最新 CI 與獨立審查結果執行整合。保存 merge 後 main 版本及完整生命週期。**Athena 產品開發仍須等待本里程碑完成驗收。**

- [ADR-002](decisions/ADR-002.md) · [Reviewer 取證與整合](adk-002-review.md) · [Eval](../evals/adk-002/README.md)
- [保護規則](https://github.com/polarbear9218/AI-DevKit/rules/28243117) · [正常 run](https://github.com/polarbear9218/AI-DevKit/actions/runs/46022746954)


獨立 Reviewer 複審 17928d92429b6fb83463e0384c5c3c19bdaaba82，自主取得正常 CI run 46023620622 與違規 job 140586691661 的實際證據，確認前次兩項 P1 程式修正。受限環境仍無法自行執行 gate。Reviewer 發現的身分及 billing 操作文件落差已在本輪修正。
