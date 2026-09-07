[CmdletBinding()]
param(
    [string] $ScreenshotPath = (Join-Path ([System.IO.Path]::GetTempPath()) 'pyshop-release-smoke.png')
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$executable = Join-Path $repoRoot 'dist\PyShop.exe'
$demoImage = Join-Path $repoRoot 'assets\demo\coastal-cabin.png'
$privateDesktopHarness = 'C:\repos\MattsVoyanceTools\tools\Invoke-PrivateDesktop.ps1'
$logDirectory = Join-Path ([System.IO.Path]::GetTempPath()) 'pyshop-release-smoke'
$stdout = Join-Path $logDirectory 'stdout.log'
$stderr = Join-Path $logDirectory 'stderr.log'

foreach ($requiredPath in $executable, $demoImage, $privateDesktopHarness) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "Required file not found: $requiredPath"
    }
}

New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
if (Test-Path -LiteralPath $ScreenshotPath) {
    Remove-Item -LiteralPath $ScreenshotPath -Force
}

$env:QT_QPA_PLATFORM = 'windows'
$env:QT_SCALE_FACTOR = '1'
$env:PYSHOP_SMOKE_EXIT_MS = '8000'
$env:PYSHOP_SMOKE_SCREENSHOT = $ScreenshotPath

& $privateDesktopHarness -FilePath $executable -Arguments ('"{0}"' -f $demoImage) -WorkingDirectory $repoRoot -StdOutPath $stdout -StdErrPath $stderr

if ($LASTEXITCODE -ne 0) {
    if (Test-Path -LiteralPath $stderr) {
        Get-Content -LiteralPath $stderr | Write-Error
    }
    throw "Packaged smoke test failed with exit code $LASTEXITCODE."
}

if (-not (Test-Path -LiteralPath $ScreenshotPath -PathType Leaf)) {
    throw "Packaged application did not create the smoke screenshot: $ScreenshotPath"
}

Add-Type -AssemblyName System.Drawing
$image = [System.Drawing.Image]::FromFile($ScreenshotPath)
try {
    if ($image.Width -lt 1000 -or $image.Height -lt 600) {
        throw "Smoke screenshot is too small: $($image.Width)x$($image.Height)"
    }
    Write-Host "Packaged application smoke test passed at $($image.Width)x$($image.Height)."
} finally {
    $image.Dispose()
}

if ((Get-Item -LiteralPath $ScreenshotPath).Length -lt 10000) {
    throw "Smoke screenshot file is unexpectedly small: $ScreenshotPath"
}

$stderrText = if (Test-Path -LiteralPath $stderr) {
    [System.IO.File]::ReadAllText($stderr).Trim()
} else {
    ''
}
if ($stderrText) {
    Write-Warning "Packaged application wrote to stderr: $stderrText"
}

Write-Host "Smoke screenshot: $ScreenshotPath"
