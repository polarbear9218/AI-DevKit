# 驗證與環境

在 Windows x64 及 Python 3.12 下執行 [安裝器](../tools/install-windows.ps1)，所用開發套件及遞移相依固定於 [requirements-dev.txt](../requirements-dev.txt)。Gitleaks 8.30.0 由發布檔安裝，驗證 Windows x64 壓縮檔的 SHA-256。Python 指令可在其他系統執行，該平台需取得同版本原生掃描器；目前驗證範圍為 Windows。

```powershell
& ./tools/install-windows.ps1
.venv/Scripts/python.exe -B -m adk check
.venv/Scripts/python.exe -B -m adk verify
```

verify 組合專案政策、Ruff 格式與 lint、mypy strict、unittest 與 Gitleaks 遮罩掃描。檢查範圍包含 Git 追蹤檔及未被忽略的新檔。Gitleaks 對這個快照掃描。歷史審查另對實際 outgoing commits 執行。驗證結果與 commit SHA 一同保存。


提交後執行 `python -m adk verify-commit SHA`，以完整 SHA 比對 HEAD，再以本機隔離 Git clone 讀取提交物件，在脫離分支的快照內執行 gate。Ruff 與 mypy 明確使用該提交的 pyproject.toml。此入口適用於保存版本證據及整合審查。
