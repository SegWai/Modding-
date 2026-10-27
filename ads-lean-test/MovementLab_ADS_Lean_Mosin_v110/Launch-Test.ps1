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
 # Load AJ's weapon pack only, alongside the animation packages.
 $ajCandidates = @(
  (Join-Path (Split-Path (Split-Path $GameDir -Parent) -Parent) 'workshop\content\221100\3571685323'),
  (Join-Path $GameDir '!Workshop\@AJs Weapons'),
  (Join-Path $GameDir "!Workshop\@AJ's Weapons"),
  (Join-Path $GameDir '@AJs Weapons'),
  (Join-Path $GameDir "@AJ's Weapons")
 )
 $aj = $null
 foreach ($candidate in $ajCandidates) {
  if (Test-Path -LiteralPath (Join-Path $candidate 'Addons') -PathType Container) { $aj = $candidate; break }
 }
 if (-not $aj) {
  $workshop = Join-Path (Split-Path (Split-Path $GameDir -Parent) -Parent) 'workshop\content\221100'
  if (Test-Path -LiteralPath $workshop -PathType Container) {
   foreach ($directory in @(Get-ChildItem -LiteralPath $workshop -Directory)) {
    $metadata = Join-Path $directory.FullName 'mod.cpp'
    if ((Test-Path -LiteralPath $metadata -PathType Leaf) -and (Get-Item -LiteralPath $metadata).Length -lt 65536) {
     $text = Get-Content -LiteralPath $metadata -Raw
     if ($text -match '(?i)AJ.?s\s*Weapons' -and (Test-Path -LiteralPath (Join-Path $directory.FullName 'Addons') -PathType Container)) {
      $aj = $directory.FullName; break
     }
    }
   }
  }
 }
 if (-not $aj) { $aj = (Read-Host 'Paste the installed AJs Weapons folder path containing Addons').Trim().Trim('"') }
 if (-not (Test-Path -LiteralPath (Join-Path $aj 'Addons') -PathType Container)) { throw 'AJs Weapons Addons folder not found. Download the mod through Steam first.' }
 # AJs_Weapons_Scripts requires JM_CF_Scripts (Community Framework).
 $cfCandidates = @(
  (Join-Path (Split-Path (Split-Path $GameDir -Parent) -Parent) 'workshop\content\221100\1559212036'),
  (Join-Path $GameDir '!Workshop\@CF'),
  (Join-Path $GameDir '@CF'),
  (Join-Path $GameDir '!Workshop\@Community Framework'),
  (Join-Path $GameDir '@Community Framework')
 )
 $cf = $null
 foreach ($candidate in $cfCandidates) {
  if (Test-Path -LiteralPath (Join-Path $candidate 'Addons') -PathType Container) { $cf = $candidate; break }
 }
 if (-not $cf) {
  Write-Host 'AJs Weapons requires Community Framework (CF), Workshop item 1559212036.'
  Write-Host 'Install/download CF through Steam: https://steamcommunity.com/sharedfiles/filedetails/?id=1559212036'
  $cf = (Read-Host 'Paste the installed CF folder path containing Addons').Trim().Trim('"')
 }
 if (-not (Test-Path -LiteralPath (Join-Path $cf 'Addons') -PathType Container)) {
  throw 'Community Framework was not found. Install/download CF through Steam, then launch again.'
 }
 $mods = @($cf,$aj,$workspace,$logic)
 Write-Host "Community Framework: $cf"

 Write-Host "AJs Weapons: $aj"

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
 @("Build: Mosin lean v110", "Time: $(Get-Date -Format o)","Mode: $mode","AJs Weapons: $aj","Community Framework: $cf","Loaded mods: $($mods -join ';')","Game: $GameDir","Executable version: $version","Project root: $ProjectRoot","Project source check: $sourceStatus",'') | Add-Content -LiteralPath (Join-Path $profiles 'launcher-run.txt') -Encoding UTF8
 Write-Host "Mode: $mode"
 Write-Host "Project check: $sourceStatus"
 Write-Host 'Steam must be running. This is a separate offline Mosin test.'
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
