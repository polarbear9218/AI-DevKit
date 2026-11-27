$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
python -c 'import sys; sys.exit(sys.version_info[:2] != (3, 12))'
if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 is required' }
if (-not (Test-Path -LiteralPath .venv/Scripts/python.exe)) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'venv creation failed' }
}
.venv/Scripts/python.exe -m pip install --only-binary=:all: -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
.venv/Scripts/python.exe -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency conflict' }
$archive = '.tools/gitleaks_8.30.0_windows_x64.zip'
New-Item -ItemType Directory -Path .tools -Force | Out-Null
if (-not (Test-Path -LiteralPath $archive)) {
    Invoke-WebRequest -UseBasicParsing "https://github.com/gitleaks/gitleaks/releases/download/v8.30.0/gitleaks_8.30.0_windows_x64.zip" -OutFile $archive
}
if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne '54FE94F644B832DD08E8C3A5915EFB3BFA862386D59FB27CA0792CB687A83573') {
    throw 'Gitleaks archive checksum mismatch'
}
Expand-Archive -LiteralPath $archive -DestinationPath .tools -Force
.tools/gitleaks.exe version
if ($LASTEXITCODE -ne 0) { throw 'Gitleaks execution failed' }
