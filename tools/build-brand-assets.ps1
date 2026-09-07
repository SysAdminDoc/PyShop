[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$master = Join-Path $repoRoot 'assets\brand\pyshop-icon-master.png'
$smallMaster = Join-Path $repoRoot 'assets\brand\pyshop-icon-small-master.png'
$iconRoot = Join-Path $repoRoot 'icon.png'
$iconDirectory = Join-Path $repoRoot 'assets\brand\icons'
$smallIconRoot = Join-Path $iconDirectory '.pyshop-small-1024.png'
$magick = (Get-Command magick -ErrorAction Stop).Source

foreach ($requiredMaster in $master, $smallMaster) {
    if (-not (Test-Path -LiteralPath $requiredMaster)) {
        throw "Brand master not found: $requiredMaster"
    }
}

New-Item -ItemType Directory -Force -Path $iconDirectory | Out-Null

& $magick $master `
    -trim +repage `
    -resize '900x900' `
    -gravity center `
    -background none `
    -extent '1024x1024' `
    -strip `
    -define 'png:color-type=6' `
    $iconRoot

if ($LASTEXITCODE -ne 0) {
    throw 'Failed to create the 1024 pixel icon.'
}

& $magick $smallMaster `
    -trim +repage `
    -resize '900x900' `
    -gravity center `
    -background none `
    -extent '1024x1024' `
    -strip `
    -define 'png:color-type=6' `
    $smallIconRoot

if ($LASTEXITCODE -ne 0) {
    throw 'Failed to create the optical-size icon.'
}

$sizes = 16, 24, 32, 48, 64, 128, 256, 512, 1024
foreach ($size in $sizes) {
    $output = Join-Path $iconDirectory "pyshop-$size.png"
    $source = if ($size -le 64) { $smallIconRoot } else { $iconRoot }
    $arguments = @(
        $source,
        '-filter', 'Lanczos',
        '-resize', "${size}x${size}",
        '-strip',
        '-define', 'png:color-type=6'
    )
    if ($size -le 64) {
        $arguments += @('-unsharp', '0x0.55+0.7+0.02')
    }
    $arguments += $output
    & $magick @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create the $size pixel icon."
    }
}

$icoInputs = 16, 24, 32, 48, 64, 128, 256 | ForEach-Object {
    Join-Path $iconDirectory "pyshop-$_.png"
}
& $magick @icoInputs (Join-Path $repoRoot 'icon.ico')
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to create icon.ico.'
}

$bannerMark = Join-Path $iconDirectory '.pyshop-banner-mark.png'
$socialMark = Join-Path $iconDirectory '.pyshop-social-mark.png'
& $magick $iconRoot -resize '330x330' -strip $bannerMark
& $magick $iconRoot -resize '430x430' -strip $socialMark

$banner = Join-Path $repoRoot 'assets\brand\pyshop-readme-banner.png'
& $magick `
    -size '1600x460' 'gradient:#101a35-#070b16' `
    $bannerMark `
    -gravity northwest -geometry '+72+65' -composite `
    -font 'Inter-SemiBold' -fill '#f8fbff' -pointsize 112 `
    -annotate '+442+92' 'PyShop' `
    -font 'Inter-Regular' -fill '#a9b7cf' -pointsize 33 `
    -annotate '+450+232' 'Layered editing that stays on your desktop.' `
    -fill '#22d3ee' -draw 'roundrectangle 450,292 788,298 3,3' `
    -font 'Inter-Medium' -fill '#7f90ac' -pointsize 21 `
    -annotate '+450+328' 'RAW   PSD   OPENRASTER   NATIVE PROJECTS' `
    -strip `
    $banner
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to create the README banner.'
}

$social = Join-Path $repoRoot 'assets\brand\pyshop-social-preview.png'
& $magick `
    -size '1280x640' 'gradient:#101a35-#070b16' `
    $socialMark `
    -gravity northwest -geometry '+72+105' -composite `
    -font 'Inter-SemiBold' -fill '#f8fbff' -pointsize 94 `
    -annotate '+532+190' 'PyShop' `
    -font 'Inter-Regular' -fill '#a9b7cf' -pointsize 31 `
    -annotate '+540+326' 'A serious image editor, built in Python.' `
    -fill '#22d3ee' -draw 'roundrectangle 540,384 896,391 3,3' `
    -font 'Inter-Medium' -fill '#7f90ac' -pointsize 20 `
    -annotate '+540+426' 'LAYERS   RAW   PSD   LOCAL-FIRST' `
    -strip `
    $social
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to create the social preview.'
}

Remove-Item -LiteralPath $bannerMark, $socialMark, $smallIconRoot -Force

Write-Host "Brand assets built from $master"
