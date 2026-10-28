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
 $logic = Join-Path $PSScriptRoot '@MLADSLeanLogic'
 $workspace = Join-Path $PSScriptRoot '@MLADSLeanWorkspace'
 $mission = Join-Path $PSScriptRoot 'Missions\MLADSLeanMosin.ChernarusPlus'
 foreach ($file in @((Join-Path $logic 'Addons\MLADSLeanLogic.pbo'),(Join-Path $mission 'init.c'))) {
  if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Extract the entire ZIP first. Missing: $file" }
 }
 if (-not (Test-Path -LiteralPath (Join-Path $workspace 'Addons\MLADSLeanWorkspace.pbo') -PathType Leaf)) { throw 'The workspace PBO is missing. Extract the entire ZIP.' }
 # Native DayZ AK74/SKS/Glock19 loadout. Load only this test's packages.
 $mods = @($workspace,$logic)
 $validation = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'validation.json') -Raw | ConvertFrom-Json
 foreach ($entry in $validation.pbo_sha256.PSObject.Properties) {
  $pbo = Join-Path $PSScriptRoot $entry.Name
  if ((Get-FileHash -LiteralPath $pbo -Algorithm SHA256).Hash -ne $entry.Value) { throw "PBO checksum mismatch: $pbo. Extract the ZIP again." }
 }
 $profiles = Join-Path $PSScriptRoot 'Profiles\LeanMosin'
 $null = New-Item -ItemType Directory -Path $profiles -Force
 $source = Join-Path $ProjectRoot 'DZ\anims\workspaces\player\player_main'
 $sourceStatus = 'not present; using the packaged workspace supplied in player_main.rar'
 if (Test-Path -LiteralPath $source -PathType Container) {
  $provenance = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'Workspace-Provenance.json') -Raw | ConvertFrom-Json
  $sourceStatus = 'matches uploaded critical files'
  foreach ($name in @('locomotion.agf','player_main.agr')) {
   $path = Join-Path $source $name
   if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { $sourceStatus = 'missing critical files'; break }
   if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $provenance.files.$name) { $sourceStatus = 'differs from uploaded workspace; collect logs if this build fails'; break }
  }
 }
 $mode = 'custom aiming lean only; rollback available as separate v79 backup'
 $version = (Get-Item -LiteralPath $exe).VersionInfo.FileVersion
 @("Build: Mosin lean v180", "Time: $(Get-Date -Format o)","Mode: $mode","Loaded mods: $($mods -join ';')","Game: $GameDir","Executable version: $version","Project root: $ProjectRoot","Project source check: $sourceStatus",'') | Add-Content -LiteralPath (Join-Path $profiles 'launcher-run.txt') -Encoding UTF8
 Write-Host "Mode: $mode"
 Write-Host "Project check: $sourceStatus"
 Write-Host 'Steam must be running. This is a separate offline Mosin test.'
 $arguments = @(
  ('"-mission={0}"' -f $mission),
  ('"-mod={0}"' -f ($mods -join ';')),
  ('"-profiles={0}"' -f $profiles),
  '-nosplash','-noPause','-doLogs'
 )
 Start-Process -FilePath $exe -WorkingDirectory $GameDir -ArgumentList ($arguments -join ' ')
 exit 0
} catch {
 Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
 exit 1
}
