# 去敏取證

Program Session 4bba005313c85f43，target b7cc3af2670448c0f79952cc3a34deda203fefa4。以下為相同執行的實際結果節錄與取證摘要。

```text
Architecture probe: old accepted, current rejected
Gitleaks synthetic violation: exit 1
Ran 7 tests
OK
```

Feature CLI 的 catalog 查詢回傳 ADK-101。隔離探針從舊規則取得空診斷，從新版取得一項診斷，並確認一般註解產生拒絕結果。核准觀察讀取提交中的 ADR-001。詳細判定在 [Program 評分輸入](program.json)。

Review Session 43ab79391c63b73b，base cf181054e36f8ecc79b96e2a968b9f143dd1d27b，target b7cc3af2670448c0f79952cc3a34deda203fefa4。送交 Reviewer 的隔離異動是把 tests/test_adk.py 的 self.assertEqual([], errors) 改成 self.assertEqual([], [])。[異動內容](review-probe.diff)

Reviewer 判定中等嚴重度，建議拒絕補丁。恆真斷言會取消對 load_catalog 回傳錯誤的直接驗證，違反需求 §10。Reviewer 同時指出後續 CLI 呼叫仍可在相同目錄違規時觸發失敗。target 未包含此異動。詳細判定在 [Review 評分輸入](review.json)。
