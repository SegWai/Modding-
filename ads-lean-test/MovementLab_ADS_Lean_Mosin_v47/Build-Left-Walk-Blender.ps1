param([string]$BlenderExe = '')
$ErrorActionPreference = 'Stop'
try {
 if (-not $BlenderExe) {
  $found = Get-Command blender.exe -ErrorAction SilentlyContinue
  if ($found) { $BlenderExe = $found.Source }
 }
 if (-not $BlenderExe) {
  $blenderRoot = Join-Path $env:ProgramFiles 'Blender Foundation'
  if (Test-Path -LiteralPath $blenderRoot) {
   $candidate = Get-ChildItem -LiteralPath $blenderRoot -Directory | Sort-Object Name -Descending | ForEach-Object { Join-Path $_.FullName 'blender.exe' } | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
   if ($candidate) { $BlenderExe = $candidate }
  }
 }
 if (-not $BlenderExe -or -not (Test-Path -LiteralPath $BlenderExe -PathType Leaf)) { throw 'Blender was not found. Run this helper with -BlenderExe followed by the full path to blender.exe, or send the collected logs for conversion.' }
 $profiles = Join-Path $PSScriptRoot 'Profiles\LeanMosin'
 $importer = Join-Path $PSScriptRoot 'BlenderTools\import_left_walk.py'
 $output = Join-Path $PSScriptRoot ('Captured_Left_Lean_Walk_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.blend')
 & $BlenderExe --background --python-exit-code 1 --python $importer -- --log $profiles --output $output
 if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $output -PathType Leaf)) { throw 'The clip was not built. Press F9 in v46, wait for Left walk clip captured, close DayZ and retry. Send collected logs if it still fails.' }
 Write-Host "Open this file in Blender: $output"
 Write-Host 'Frames 1 through 36 are recorded character-left walking lean samples.'
 exit 0
} catch { Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red; exit 1 }
