$ErrorActionPreference = 'Stop'
$destination = Join-Path (Split-Path -Parent $PSScriptRoot) '.tools/portable-git'
New-Item -Force -ItemType Directory -Path $destination | Out-Null
$file = Join-Path $destination 'PortableGit-2.56.1-64-bit.7z.exe'
$checksum = '9dd04a608ceb5f6ab32a73709e0ecb159d211da71b697c45ff81f6dd0c6b49c7'
if (-not (Test-Path -LiteralPath $file)) {
    Invoke-WebRequest -UseBasicParsing 'https://github.com/git-for-windows/git/releases/download/v2.56.1.windows.1/PortableGit-2.56.1-64-bit.7z.exe' -OutFile $file
}
if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash -ne $checksum) { throw 'PortableGit archive checksum mismatch' }
if (-not (Test-Path -LiteralPath (Join-Path $destination 'ucrt64/bin/git.exe'))) {
$process = Start-Process -FilePath $file -ArgumentList @('-y', "-o`"$destination`"") -WindowStyle Hidden -PassThru -Wait
if ($process.ExitCode -ne 0) { throw 'PortableGit extraction failed' }
}
& (Join-Path $destination 'ucrt64/bin/git.exe') --version
if ($LASTEXITCODE -ne 0) { throw 'PortableGit execution failed' }
