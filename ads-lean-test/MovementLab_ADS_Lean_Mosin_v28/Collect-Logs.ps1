$ErrorActionPreference = 'Stop'
try {
 $profiles = Join-Path $PSScriptRoot 'Profiles\LeanMosin'
 if (-not (Test-Path -LiteralPath $profiles -PathType Container)) { throw 'Run the test first; the test profile folder does not exist.' }
 $files = @()
 foreach ($pattern in @('*.RPT','script_*.log','error_*.log','crash_*.log','CrashReporter.log','launcher-run.txt')) {
  $files += @(Get-ChildItem -LiteralPath $profiles -Filter $pattern -File | Sort-Object LastWriteTime -Descending | Select-Object -First 2)
 }
 $files = @($files | Sort-Object FullName -Unique)
 if ($files.Count -eq 0) { throw 'No test logs found.' }
 $archive = Join-Path $PSScriptRoot ('Mosin-Lean-v28-Logs-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.zip')
 Compress-Archive -LiteralPath @($files.FullName) -DestinationPath $archive -CompressionLevel Optimal
 Write-Host "Send this ZIP: $archive"
 Write-Host 'Large memory dumps and unrelated game profiles are excluded.'
 exit 0
} catch { Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red; exit 1 }
