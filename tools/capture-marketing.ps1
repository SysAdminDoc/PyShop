#Requires -Version 7.0
[CmdletBinding()]
param(
    [string] $OutputDir = '',
    [string] $Executable = '',
    [string] $DemoImage = ''
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$privateDesktopHarness = 'C:\repos\MattsVoyanceTools\tools\Invoke-PrivateDesktop.ps1'
if (-not $OutputDir) { $OutputDir = Join-Path $repoRoot 'build\marketing-capture' }
$OutputDir = [System.IO.Path]::GetFullPath($OutputDir)
$arguments = ''
$workingDirectory = $repoRoot
if (-not $DemoImage) { $DemoImage = Join-Path $repoRoot 'assets\demo\coastal-cabin.png' }
if (-not $Executable) {
    $Executable = Join-Path $repoRoot '.venv\Scripts\python.exe'
    $arguments = '"{0}"' -f (Join-Path $PSScriptRoot 'capture-marketing.py')
} else {
    $workingDirectory = Split-Path -Parent ([System.IO.Path]::GetFullPath($Executable))
}
foreach ($required in $Executable, $privateDesktopHarness, $DemoImage) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Required file not found: $required" }
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('PyShop-Capture-' + [guid]::NewGuid().ToString('N'))
$environment = @{
    QT_QPA_PLATFORM = 'windows'
    QT_SCALE_FACTOR = '1'
    PYSHOP_TEST_PROFILE = $tempRoot
    PYSHOP_DATA_DIR = (Join-Path $tempRoot 'data')
    PYSHOP_CAPTURE_DIR = $OutputDir
    PYSHOP_CAPTURE_DEMO = $DemoImage
}
$previous = @{}
try {
    foreach ($key in $environment.Keys) {
        $previous[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
        [Environment]::SetEnvironmentVariable($key, $environment[$key], 'Process')
    }
    & $privateDesktopHarness -FilePath $Executable -Arguments $arguments -WorkingDirectory $workingDirectory -StdOutPath (Join-Path $OutputDir 'capture.stdout.log') -StdErrPath (Join-Path $OutputDir 'capture.stderr.log')
    if ($LASTEXITCODE -ne 0) { throw "Capture failed with exit code $LASTEXITCODE. See capture.stderr.log in $OutputDir." }
    if (-not (Test-Path -LiteralPath (Join-Path $OutputDir 'capture-report.json'))) { throw 'Capture did not produce its evidence report.' }
} finally {
    foreach ($key in $previous.Keys) { [Environment]::SetEnvironmentVariable($key, $previous[$key], 'Process') }
    $resolved = [System.IO.Path]::GetFullPath($tempRoot)
    $allowedRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\') + '\'
    if (-not $resolved.StartsWith($allowedRoot, [StringComparison]::OrdinalIgnoreCase) -or (Split-Path $resolved -Leaf) -notlike 'PyShop-Capture-*') {
        throw "Refusing to remove unexpected profile path: $resolved"
    }
    if (Test-Path -LiteralPath $resolved) { Remove-Item -LiteralPath $resolved -Recurse -Force }
}
Write-Host "Screenshots and evidence written to $OutputDir"
