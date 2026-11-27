# 架構地圖

| 責任 | 實作與介面 |
| --- | --- |
| Project Knowledge、Context Engineering、Feature Discovery | [Feature Map](features.md) 與 [記錄驗證器](../adk/features.py) |
| Engineering Guardrails、Software Verification | [政策檢查](../adk/policy.py)、[工具執行](../adk/gate.py) 與 [測試](../tests/test_adk.py) |
| Agent Integration、Harness、Project Integration | [CLI](../adk/__main__.py) 組合 Git、Python 工具與工程核心。Codex 作為獨立執行環境。 |
| Independent Review、Observability、Human Intervention、Evals、Continuous Improvement、Governance | [工作流](workflow.md) 與 [治理及工程原則](foundation.md) |

依賴方向為 CLI → 工具執行及政策 → Feature Map 路徑驗證。核心可讀取 Repository 中的知識，沒有 Athena、Hydra 或 Codex API 相依。以實際 Pilot 需求決定是否擴充入口。[設計與替代方案](decisions/ADR-001.md)

ADK-002 在 PR 合併候選上執行 GitHub Actions，Python 整合 gate 讀取平台保護、CI 及指定 Reviewer App 的 SHA 證據。[現行驗收](adk-002-status.md)
