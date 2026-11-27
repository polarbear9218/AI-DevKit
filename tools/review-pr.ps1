param(
    [Parameter(Mandatory)][ValidatePattern('^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')][string]$Repository,
    [Parameter(Mandatory)][ValidateRange(1,2147483647)][int]$Number,
    [Parameter(Mandatory)][ValidatePattern('^[a-f0-9]{40}$')][string]$Target,
    [Parameter(Mandatory)][string]$ScratchDirectory
)
$ErrorActionPreference = 'Stop'
$api = "https://api.github.com/repos/$Repository"
$pr = Invoke-RestMethod -Uri "$api/pulls/$Number"
if ($pr.head.sha -ne $Target -or $pr.base.ref -ne 'main') { throw 'Unexpected PR target or base' }
$candidate = $pr.merge_commit_sha
if ($candidate -notmatch '^[a-f0-9]{40}$') { throw 'PR merge candidate unavailable' }
$root = (Resolve-Path -LiteralPath $ScratchDirectory).Path
$checkout = Join-Path $root ("review-pr-$Number-" + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $checkout | Out-Null
Push-Location -LiteralPath $checkout
try {
    git init --quiet --template=
    if ($LASTEXITCODE -ne 0) { throw 'Reviewer checkout initialization failed' }
    git fetch --no-tags "https://github.com/$Repository.git" "refs/pull/$Number/merge"
    if ($LASTEXITCODE -ne 0) { throw 'Reviewer candidate fetch failed' }
    git checkout --quiet --detach FETCH_HEAD
    if ($LASTEXITCODE -ne 0 -or (git rev-parse HEAD) -ne $candidate) { throw 'Reviewer candidate changed' }
    if ((git rev-parse HEAD^1) -ne $pr.base.sha -or (git rev-parse HEAD^2) -ne $Target) {
        throw 'Reviewer candidate parent mismatch'
    }
    $checks = Invoke-RestMethod -Uri "$api/commits/$Target/check-runs"
    $checks.check_runs | Select-Object name,id,head_sha,status,conclusion,details_url | ConvertTo-Json -Compress
    Write-Output "Review base $($pr.base.sha) target $Target candidate $candidate scratch $checkout"
    git --no-pager diff --stat "$($pr.base.sha)..$Target"
    if ($LASTEXITCODE -ne 0) { throw 'Reviewer diff unavailable' }
    ./tools/install-windows.ps1
    ./tools/install-ci-git.ps1
    $env:ADK_GIT_EXECUTABLE = Join-Path $checkout '.tools/portable-git/ucrt64/bin/git.exe'
    .venv/Scripts/python.exe -B -m adk verify-commit $candidate
    if ($LASTEXITCODE -ne 0) { throw 'Reviewer verification failed' }
    $current = Invoke-RestMethod -Uri "$api/pulls/$Number"
    if ($current.head.sha -ne $Target -or $current.merge_commit_sha -ne $candidate) {
        throw 'PR changed during review'
    }
} finally {
    Pop-Location
}
