param([Parameter(Mandatory=$true)][string]$GameDirectory)
$ErrorActionPreference = 'Stop'
$configuredFile = Join-Path $PSScriptRoot 'SNAFU-Mod-Path.txt'
$snafuPath = ''
if (Test-Path -LiteralPath $configuredFile) {
    $snafuPath = (Get-Content -LiteralPath $configuredFile -Raw).Trim().Trim('"')
}
if (!$snafuPath) {
    $workshopDirectory = Join-Path $GameDirectory '!Workshop'
    if (Test-Path -LiteralPath $workshopDirectory) {
        $snafuDirectory = Get-ChildItem -LiteralPath $workshopDirectory -Directory |
            Where-Object { $_.Name -match '^@?SNAFU\s*Weapons' } | Select-Object -First 1
        if ($snafuDirectory) { $snafuPath = $snafuDirectory.FullName }
    }
}
if (!$snafuPath -or !(Test-Path -LiteralPath (Join-Path $snafuPath 'Addons'))) {
    throw 'SNAFU Weapons was not found. Put its installed mod folder path in SNAFU-Mod-Path.txt, then launch again. Do not put a Workshop URL there.'
}
if ($snafuPath.Contains(';') -or $snafuPath.Contains('"') -or $snafuPath.Contains("`n")) {
    throw 'SNAFU-Mod-Path.txt must contain one local folder path.'
}
Set-Content -LiteralPath (Join-Path $PSScriptRoot 'SNAFU-Resolved-Path.txt') -Value $snafuPath -Encoding ASCII
Write-Host ('Loading installed SNAFU Weapons: ' + $snafuPath)
