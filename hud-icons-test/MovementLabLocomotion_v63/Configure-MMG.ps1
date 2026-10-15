param([Parameter(Mandatory=$true)][string]$GameDirectory)
$ErrorActionPreference = 'Stop'
$configuredFile = Join-Path $PSScriptRoot 'MMG-Mod-Path.txt'
$mmgPath = ''
if (Test-Path -LiteralPath $configuredFile) {
    $mmgPath = (Get-Content -LiteralPath $configuredFile -Raw).Trim().Trim('"')
}
if (!$mmgPath) {
    $workshopDirectory = Join-Path $GameDirectory '!Workshop'
    if (Test-Path -LiteralPath $workshopDirectory) {
        $mmgDirectory = Get-ChildItem -LiteralPath $workshopDirectory -Directory |
            Where-Object { $_.Name -match '^@?MMG.*(Military|Gear)|^@?Mightys?\s*Military' } | Select-Object -First 1
        if ($mmgDirectory) { $mmgPath = $mmgDirectory.FullName }
    }
}
if (!$mmgPath -or !(Test-Path -LiteralPath (Join-Path $mmgPath 'Addons'))) {
    throw 'MMG - Mightys Military Gear was not found. Put its installed mod folder path in MMG-Mod-Path.txt, then launch again. Do not put a Workshop URL there.'
}
if ($mmgPath.Contains(';') -or $mmgPath.Contains('"') -or $mmgPath.Contains("`n")) {
    throw 'MMG-Mod-Path.txt must contain one local folder path.'
}
Set-Content -LiteralPath (Join-Path $PSScriptRoot 'MMG-Resolved-Path.txt') -Value $mmgPath -Encoding ASCII
Write-Host ('Loading installed MMG - Mightys Military Gear: ' + $mmgPath)
