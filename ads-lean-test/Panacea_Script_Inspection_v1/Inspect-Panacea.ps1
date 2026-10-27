param([string]$PanaceaDir = 'D:\SteamLibrary\steamapps\workshop\content\221100\2389010221')
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
function Read-PboString([IO.BinaryReader]$Reader) {
 $bytes = New-Object 'System.Collections.Generic.List[byte]'
 while ($true) {
  $value = $Reader.ReadByte()
  if ($value -eq 0) { break }
  if ($bytes.Count -ge 8192) { throw 'Invalid or unsupported PBO string length.' }
  $bytes.Add($value)
 }
 return [Text.Encoding]::ASCII.GetString($bytes.ToArray())
}
try {
 if (-not (Test-Path -LiteralPath (Join-Path $PanaceaDir 'Addons') -PathType Container)) {
  $PanaceaDir = (Read-Host 'Paste the installed The Panacea Weapons folder path').Trim().Trim('"')
 }
 if (-not (Test-Path -LiteralPath (Join-Path $PanaceaDir 'Addons') -PathType Container)) { throw 'Panacea Addons folder not found.' }
 $report = [ordered]@{ Folder = $PanaceaDir; Time = (Get-Date -Format o); Purpose = 'Read-only PBO header and script-path inspection; mod files are not changed'; Pbos = @(); Metadata = @() }
 foreach ($name in @('mod.cpp','meta.cpp')) {
  $path = Join-Path $PanaceaDir $name
  if ((Test-Path -LiteralPath $path -PathType Leaf) -and (Get-Item -LiteralPath $path).Length -lt 65536) {
   $report.Metadata += [ordered]@{ File = $name; Text = (Get-Content -LiteralPath $path -Raw) }
  }
 }
 foreach ($pbo in @(Get-ChildItem -LiteralPath (Join-Path $PanaceaDir 'Addons') -Filter '*.pbo' -File -Recurse)) {
  $entry = [ordered]@{ Name = $pbo.Name; Bytes = $pbo.Length; Properties = @{}; FileCount = 0; ScriptFiles = @(); ScriptDefinitions = @(); Error = $null }
  $stream = $null; $reader = $null
  try {
   $stream = [IO.File]::Open($pbo.FullName, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
   $reader = New-Object IO.BinaryReader($stream)
   $rows = New-Object 'System.Collections.Generic.List[object]'
   while ($true) {
    $name = Read-PboString $reader
    $method = $reader.ReadUInt32(); $original = $reader.ReadUInt32(); $reserved = $reader.ReadUInt32(); $timestamp = $reader.ReadUInt32(); $size = $reader.ReadUInt32()
    if ($name -eq '' -and $method -eq 0x56657273) {
     while ($true) {
      $key = Read-PboString $reader
      if ($key -eq '') { break }
      $entry.Properties[$key] = Read-PboString $reader
     }
     continue
    }
    if ($name -eq '') { break }
    if ($rows.Count -ge 200000) { throw 'Unsupported PBO entry count.' }
    $rows.Add([pscustomobject]@{ Name=$name; Method=$method; Size=$size; Original=$original })
    if ($name -match '(?i)(\.c$|script|\.c\.(bin|enf)$)') {
     $entry.ScriptFiles += [ordered]@{ Name=$name; Method=$method; Bytes=$size }
    }
   }
   $entry.FileCount = $rows.Count
   $offset = $stream.Position
   foreach ($row in $rows) {
    if ($offset + $row.Size -gt $stream.Length) { throw 'PBO payload extends past end of file.' }
    if ($row.Method -eq 0 -and $row.Size -le 1048576 -and $row.Name -match '(?i)(^|[\\/])config\.cpp$') {
     $null = $stream.Seek($offset,[IO.SeekOrigin]::Begin)
     $text = [Text.Encoding]::UTF8.GetString($reader.ReadBytes([int]$row.Size))
     if ($text -match '(?i)(CfgMods|ScriptModule)') {
      $entry.ScriptDefinitions += [ordered]@{ Name=$row.Name; Text=$text.Substring(0,[Math]::Min(131072,$text.Length)) }
     }
    }
    $offset += $row.Size
   }
  } catch { $entry.Error = $_.Exception.Message }
  finally { if ($reader) { $reader.Dispose() } elseif ($stream) { $stream.Dispose() } }
  $report.Pbos += $entry
  Write-Host ($entry.Name + ': ' + $entry.FileCount + ' entries; ' + $entry.ScriptFiles.Count + ' script-related entries')
 }
 $outputDir = Join-Path $PSScriptRoot 'Inspection'
 $null = New-Item -ItemType Directory -Path $outputDir -Force
 $output = Join-Path $outputDir 'Panacea-Script-Inspection.json'
 $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $output -Encoding UTF8
 $zip = Join-Path $PSScriptRoot ('Panacea-Script-Inspection-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.zip')
 Compress-Archive -LiteralPath $output -DestinationPath $zip -CompressionLevel Optimal
 Write-Host "Send this ZIP: $zip"
 Write-Host 'The mod was read only. No game launch or mod changes were performed.'
 exit 0
} catch { Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red; exit 1 }
