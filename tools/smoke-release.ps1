#Requires -Version 7.0
[CmdletBinding()]
param(
    [string] $ScreenshotPath = (Join-Path ([System.IO.Path]::GetTempPath()) 'pyshop-release-smoke.png'),
    [string] $Executable = '',
    [string] $DemoImage = ''
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $Executable) { $Executable = Join-Path $repoRoot 'dist\PyShop.exe' }
if (-not $DemoImage) { $DemoImage = Join-Path $repoRoot 'assets\demo\coastal-cabin.png' }
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

$profileRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('PyShop-Smoke-' + [guid]::NewGuid().ToString('N'))
$environment = @{
    QT_QPA_PLATFORM = 'windows'
    QT_SCALE_FACTOR = '1'
    PYSHOP_SMOKE_EXIT_MS = '8000'
    PYSHOP_SMOKE_SCREENSHOT = $ScreenshotPath
    PYSHOP_TEST_PROFILE = $profileRoot
    PYSHOP_DATA_DIR = (Join-Path $profileRoot 'data')
    PYSHOP_CAPTURE_DIR = ''
}
$previous = @{}
try {
    foreach ($key in $environment.Keys) {
        $previous[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
        [Environment]::SetEnvironmentVariable($key, $environment[$key], 'Process')
    }
    & $privateDesktopHarness -FilePath $Executable -Arguments ('"{0}"' -f $DemoImage) -WorkingDirectory (Split-Path -Parent ([System.IO.Path]::GetFullPath($Executable))) -StdOutPath $stdout -StdErrPath $stderr
    $smokeExitCode = $LASTEXITCODE
} finally {
    foreach ($key in $previous.Keys) { [Environment]::SetEnvironmentVariable($key, $previous[$key], 'Process') }
    $resolved = [System.IO.Path]::GetFullPath($profileRoot)
    $allowedRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\') + '\'
    if (-not $resolved.StartsWith($allowedRoot, [StringComparison]::OrdinalIgnoreCase) -or (Split-Path $resolved -Leaf) -notlike 'PyShop-Smoke-*') {
        throw "Refusing to remove unexpected profile path: $resolved"
    }
    if (Test-Path -LiteralPath $resolved) { Remove-Item -LiteralPath $resolved -Recurse -Force }
}

if ($smokeExitCode -ne 0) {
    if (Test-Path -LiteralPath $stderr) {
        Get-Content -LiteralPath $stderr | Write-Error
    }
    throw "Packaged smoke test failed with exit code $smokeExitCode."
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
