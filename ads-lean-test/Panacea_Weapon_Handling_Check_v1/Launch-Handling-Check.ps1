param(
 [string]$GameDir = 'D:\SteamLibrary\steamapps\common\DayZ',
 [string]$ProjectRoot = 'F:\DayZProjects'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
try {
 if (Get-Process -Name 'DayZ_x64','DayZDiag_x64' -ErrorAction SilentlyContinue) { throw 'Close DayZ before starting the separate lean test.' }
 if (-not (Test-Path -LiteralPath (Join-Path $GameDir 'DayZDiag_x64.exe') -PathType Leaf)) {
  $GameDir = (Read-Host 'Enter your DayZ installation folder containing DayZDiag_x64.exe').Trim().Trim('"')
 }
 $exe = Join-Path $GameDir 'DayZDiag_x64.exe'
 if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw "DayZDiag_x64.exe was not found in $GameDir" }
 $helper = Join-Path $PSScriptRoot '@PWHC'
 $mission = Join-Path $PSScriptRoot 'Missions\PWHC.ChernarusPlus'
 if (-not (Test-Path -LiteralPath (Join-Path $helper 'Addons\PWHC.pbo') -PathType Leaf)) { throw 'Extract the entire handling-check ZIP.' }
 # Load only the requested weapon pack beside this test. No old weapon packs.
 $panaceaCandidates = @(
  (Join-Path $GameDir '!Workshop\@The Panacea Weapons'),
  (Join-Path $GameDir '@The Panacea Weapons'),
  (Join-Path (Split-Path (Split-Path $GameDir -Parent) -Parent) 'workshop\content\221100\2389010221')
 )
 $panacea = $null
 foreach ($candidate in $panaceaCandidates) {
  if (Test-Path -LiteralPath (Join-Path $candidate 'Addons') -PathType Container) { $panacea = $candidate; break }
 }
 if (-not $panacea) {
  $panacea = (Read-Host 'Paste the installed The Panacea Weapons folder path (Workshop item 2389010221)').Trim().Trim('"')
 }
 if (-not (Test-Path -LiteralPath (Join-Path $panacea 'Addons') -PathType Container)) {
  throw 'Panacea Addons folder not found. Subscribe to Workshop item 2389010221, download it, and launch again.'
 }
 $mods = @($panacea,$helper)
 Write-Host "Panacea weapons: $panacea"

 $manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw | ConvertFrom-Json
 if ((Get-FileHash -LiteralPath (Join-Path $helper 'Addons\PWHC.pbo') -Algorithm SHA256).Hash -ne $manifest.helper_sha256) { throw 'Helper checksum mismatch. Extract again.' }
 $profiles = Join-Path $PSScriptRoot 'Profiles\PanaceaHandling'
 $null = New-Item -ItemType Directory -Path $profiles -Force
 @("Check: native Panacea handling v1", "Time: $(Get-Date -Format o)", "Game: $GameDir", "Panacea: $panacea", "Loaded mods: $($mods -join ';')", 'No MLADSLean workspace, player, camera or ammo scripts loaded.') | Add-Content -LiteralPath (Join-Path $profiles 'launcher-run.txt') -Encoding UTF8
 Write-Host 'Native handling check. 1 AK74 control, 2 Panacea SCAR-H, 3 Panacea AWM.'
 $arguments = @(
  ('"-mission={0}"' -f $mission),
  ('"-mod={0}"' -f ($mods -join ';')),
  ('"-profiles={0}"' -f $profiles),
  '-nosplash','-noPause','-doLogs','-scriptDebug=true'
 )
 Start-Process -FilePath $exe -WorkingDirectory $GameDir -ArgumentList ($arguments -join ' ')
 exit 0
} catch {
 Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
 exit 1
}
