$ErrorActionPreference = 'Stop'
$staging = $null
try {
 $staging = Join-Path ([IO.Path]::GetTempPath()) ('MLLeanDistance_' + [guid]::NewGuid().ToString('N'))
 $null = New-Item -ItemType Directory -Path $staging
 $count = 0
 foreach ($profileName in @('LeanMosin','VanillaLean')) {
  $profiles = Join-Path $PSScriptRoot ('Profiles\' + $profileName)
  if (-not (Test-Path -LiteralPath $profiles -PathType Container)) { continue }
  $target = Join-Path $staging $profileName
  $null = New-Item -ItemType Directory -Path $target
  $files = @()
  foreach ($pattern in @('*.RPT','script_*.log','error_*.log','crash_*.log','CrashReporter.log','launcher-run.txt')) {
   $files += @(Get-ChildItem -LiteralPath $profiles -Filter $pattern -File | Sort-Object LastWriteTime -Descending | Select-Object -First 2)
  }
  foreach ($file in @($files | Sort-Object FullName -Unique)) { Copy-Item -LiteralPath $file.FullName -Destination $target; $count++ }
 }
 if ($count -eq 0) { throw 'No test logs found. Run the two distance tests first.' }
 $archive = Join-Path $PSScriptRoot ('Mosin-Lean-v73-Logs-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.zip')
 Compress-Archive -Path (Join-Path $staging '*') -DestinationPath $archive -CompressionLevel Optimal
 Write-Host "Send this ZIP: $archive"
 Write-Host 'Contains native and custom test logs. Dumps and unrelated profiles excluded.'
 exit 0
} catch { Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red; exit 1 }
finally { if ($staging -and (Test-Path -LiteralPath $staging)) { Remove-Item -LiteralPath $staging -Recurse -Force } }
