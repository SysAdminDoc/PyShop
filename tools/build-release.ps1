[CmdletBinding()]
param(
    [switch] $BuildOnly,
    [switch] $PackageOnly
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot '.venv\Scripts\python.exe'
$tar = 'C:\Windows\System32\tar.exe'
if ($BuildOnly -and $PackageOnly) { throw 'Choose BuildOnly or PackageOnly, not both.' }

if (-not (Test-Path -LiteralPath $python)) {
    throw "Build environment not found: $python"
}
if (-not (Test-Path -LiteralPath $tar)) {
    throw "Archive tool not found: $tar"
}

$version = [regex]::Match([System.IO.File]::ReadAllText((Join-Path $repoRoot 'pyshop\app_info.py')), 'APP_VERSION = "([^"]+)"').Groups[1].Value
if (-not $version) {
    throw 'Could not read the PyShop version.'
}

if (-not $PackageOnly) {
foreach ($directoryName in 'build', 'dist') {
    $target = Join-Path $repoRoot $directoryName
    $resolvedTarget = [System.IO.Path]::GetFullPath($target)
    $resolvedRoot = [System.IO.Path]::GetFullPath($repoRoot) + [System.IO.Path]::DirectorySeparatorChar
    if (-not $resolvedTarget.StartsWith($resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove a path outside the repository: $resolvedTarget"
    }
    if (Test-Path -LiteralPath $resolvedTarget) {
        Remove-Item -LiteralPath $resolvedTarget -Recurse -Force
    }
}
}

Push-Location $repoRoot
try {
    if (-not $PackageOnly) {
    & $python -m PyInstaller --noconfirm --clean 'PyShop.spec'
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE."
    }

    $exe = Join-Path $repoRoot 'dist\PyShop.exe'
    if (-not (Test-Path -LiteralPath $exe)) {
        throw "Expected executable was not created: $exe"
    }

    $certificate = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert |
        Where-Object { $_.NotAfter -gt (Get-Date) } |
        Sort-Object NotAfter -Descending |
        Select-Object -First 1
    if ($certificate) {
        $signature = Set-AuthenticodeSignature -FilePath $exe -Certificate $certificate -TimestampServer 'http://timestamp.digicert.com'
        if ($signature.Status -ne 'Valid') {
            throw "Code signing failed: $($signature.StatusMessage)"
        }
    } else {
        Write-Warning 'No code-signing certificate is installed. The executable will be unsigned.'
    }
    }
    $exe = Join-Path $repoRoot 'dist\PyShop.exe'
    if ($BuildOnly) {
        Write-Host "Built $exe. Capture and review this executable before packaging."
        return
    }
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw "Executable not found: $exe" }
    if ((Get-Item -LiteralPath $exe).VersionInfo.ProductVersion -ne $version) { throw 'Executable version does not match the source.' }
    & $python 'tools\verify-release.py' --executable $exe --version $version
    if ($LASTEXITCODE -ne 0) { throw 'Review fresh captures from this executable before packaging.' }

    $stage = Join-Path $repoRoot "dist\PyShop-v$version-win64"
    $stageFull = [System.IO.Path]::GetFullPath($stage)
    $distRoot = [System.IO.Path]::GetFullPath((Join-Path $repoRoot 'dist')) + '\'
    if (-not $stageFull.StartsWith($distRoot, [StringComparison]::OrdinalIgnoreCase)) { throw "Unexpected staging path: $stageFull" }
    if (Test-Path -LiteralPath $stageFull) { Remove-Item -LiteralPath $stageFull -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $stage | Out-Null
    Copy-Item -LiteralPath $exe -Destination (Join-Path $stage 'PyShop.exe')
    Copy-Item -LiteralPath (Join-Path $repoRoot 'README.md') -Destination $stage
    Copy-Item -LiteralPath (Join-Path $repoRoot 'LICENSE') -Destination $stage
    Copy-Item -LiteralPath (Join-Path $repoRoot 'CHANGELOG.md') -Destination $stage
    Copy-Item -LiteralPath (Join-Path $repoRoot 'assets') -Destination $stage -Recurse

    $archive = Join-Path $repoRoot "dist\PyShop-v$version-win64.zip"
    Push-Location $stage
    try {
        & $tar -a -c -f $archive '*'
        if ($LASTEXITCODE -ne 0) {
            throw "Archive creation failed with exit code $LASTEXITCODE."
        }
    } finally {
        Pop-Location
    }
    & $python 'tools\verify-release.py' --executable $exe --version $version --archive $archive
    if ($LASTEXITCODE -ne 0) { throw 'Portable package verification failed.' }

    $checksums = @($exe, $archive) | ForEach-Object {
        $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $_
        "$($hash.Hash.ToLowerInvariant())  $([System.IO.Path]::GetFileName($_))"
    }
    $checksumPath = Join-Path $repoRoot "dist\PyShop-v$version.sha256"
    [System.IO.File]::WriteAllLines($checksumPath, $checksums, [System.Text.UTF8Encoding]::new($false))

    Write-Host "Built $archive"
    Write-Host "Checksums: $checksumPath"
} finally {
    Pop-Location
}
