$ErrorActionPreference = 'Stop'
$movementlabLogsRoot = Join-Path $PSScriptRoot 'Profiles\MovementLogic'
if (-not (Test-Path -LiteralPath $movementlabLogsRoot)) { throw 'Run this test first, then close DayZ before collecting logs.' }
$movementlabLogFiles = @(Get-ChildItem -LiteralPath $movementlabLogsRoot -Recurse -File | Where-Object { $_.Extension -in @('.RPT','.log') })
if ($movementlabLogFiles.Count -eq 0) { throw 'No RPT/log files found in this test folder.' }
$movementlabZipTarget = Join-Path $PSScriptRoot 'MovementLab-Aim-Linked-v2-Revision46-Logs.zip'
Compress-Archive -LiteralPath $movementlabLogFiles.FullName -DestinationPath $movementlabZipTarget -Force
Write-Host "Send this archive if standing mode switching is incorrect: $movementlabZipTarget"
