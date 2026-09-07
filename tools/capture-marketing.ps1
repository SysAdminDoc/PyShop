[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot '.venv\Scripts\python.exe'
$captureScript = Join-Path $PSScriptRoot 'capture-marketing.py'
$privateDesktopHarness = 'C:\repos\MattsVoyanceTools\tools\Invoke-PrivateDesktop.ps1'
$logDirectory = Join-Path ([System.IO.Path]::GetTempPath()) 'pyshop-marketing-capture'

if (-not (Test-Path -LiteralPath $python)) {
    $python = (Get-Command python -ErrorAction Stop).Source
}
if (-not (Test-Path -LiteralPath $privateDesktopHarness)) {
    throw "Private desktop harness not found: $privateDesktopHarness"
}

New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
$stdout = Join-Path $logDirectory 'stdout.log'
$stderr = Join-Path $logDirectory 'stderr.log'
$env:QT_QPA_PLATFORM = 'windows'

& $privateDesktopHarness `
    -FilePath $python `
    -Arguments "`"$captureScript`"" `
    -WorkingDirectory $repoRoot `
    -StdOutPath $stdout `
    -StdErrPath $stderr

if ($LASTEXITCODE -ne 0) {
    if (Test-Path -LiteralPath $stderr) {
        Get-Content -LiteralPath $stderr | Write-Error
    }
    throw "Marketing capture failed with exit code $LASTEXITCODE."
}

Write-Host "Marketing screenshots written to $(Join-Path $repoRoot 'assets\screenshots')"
