[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot '.venv\Scripts\python.exe'
$tar = 'C:\Windows\System32\tar.exe'

if (-not (Test-Path -LiteralPath $python)) {
    throw "Build environment not found: $python"
}
if (-not (Test-Path -LiteralPath $tar)) {
    throw "Archive tool not found: $tar"
}

$version = (& $python -c 'from pyshop import APP_VERSION; print(APP_VERSION)').Trim()
if (-not $version) {
    throw 'Could not read the PyShop version.'
}

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

Push-Location $repoRoot
try {
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

    $stage = Join-Path $repoRoot "dist\PyShop-v$version-win64"
    New-Item -ItemType Directory -Force -Path $stage | Out-Null
    Copy-Item -LiteralPath $exe -Destination (Join-Path $stage 'PyShop.exe')
    Copy-Item -LiteralPath (Join-Path $repoRoot 'README.md') -Destination $stage
    Copy-Item -LiteralPath (Join-Path $repoRoot 'LICENSE') -Destination $stage

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
