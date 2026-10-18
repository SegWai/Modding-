param([string]$WorkDrive = '')
$ErrorActionPreference = 'Stop'
# Read/copy only: no extraction tools, game modification, or automatic upload.
$rules = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'AssetRules.json') -Raw | ConvertFrom-Json
if ([string]::IsNullOrWhiteSpace($WorkDrive)) {
    foreach ($candidate in @('D:\DayZProjects', 'P:\')) {
        if ((Test-Path -LiteralPath (Join-Path $candidate 'dz\anims')) -or (Test-Path -LiteralPath (Join-Path $candidate 'dz\characters'))) {
            $WorkDrive = $candidate
            break
        }
    }
}
if ([string]::IsNullOrWhiteSpace($WorkDrive)) {
    $WorkDrive = Read-Host 'Enter your EXTRACTED DayZ Tools work-drive folder (for example D:\DayZProjects or P:\)'
}
$root = [IO.Path]::GetFullPath($WorkDrive).TrimEnd('\', '/')
if ($root -match '^[A-Za-z]:$') { $root += '\' }
if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'The work-drive folder does not exist.' }
$anims = Join-Path $root 'dz\anims'
$characters = Join-Path $root 'dz\characters'
if (-not (Test-Path -LiteralPath $anims) -and -not (Test-Path -LiteralPath $characters)) {
    throw 'This folder has no extracted dz\anims or dz\characters. Mount/extract the game data through DayZ Tools first; selecting the game Addons folder is not enough.'
}
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$output = Join-Path $PSScriptRoot ('Ragdoll-Assets-' + $stamp + '-' + [Guid]::NewGuid().ToString('N').Substring(0,6))
New-Item -ItemType Directory -Path $output | Out-Null
$records = New-Object System.Collections.Generic.List[object]
$inventory = New-Object System.Collections.Generic.List[object]
$warnings = New-Object System.Collections.Generic.List[string]
$parts = New-Object System.Collections.Generic.List[string]
$seen = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
$partNumber = 1
$partBytes = [long]0
$partPath = Join-Path $output ('Part-{0:D2}' -f $partNumber)
New-Item -ItemType Directory -Path $partPath | Out-Null
$parts.Add($partPath)
foreach ($subRoot in $rules.roots) {
    $scanRoot = Join-Path $root $subRoot.Replace('/', '\')
    if (-not (Test-Path -LiteralPath $scanRoot)) { $warnings.Add('Missing extracted folder: ' + $subRoot); continue }
    Write-Host ('Scanning ' + $subRoot + ' ...')
    $scanErrors = @()
    $files = @(Get-ChildItem -LiteralPath $scanRoot -Recurse -File -ErrorAction SilentlyContinue -ErrorVariable +scanErrors | Sort-Object FullName)
    if ($scanErrors.Count -gt 0) { $warnings.Add(('Some files could not be listed under {0}; count={1}' -f $subRoot, $scanErrors.Count)) }
    foreach ($file in $files) {
        $relative = $file.FullName.Substring($root.Length).TrimStart('\', '/').Replace('\', '/')
        if (-not $seen.Add($relative)) { continue }
        # Keep an asset-name inventory so missing matches can be diagnosed.
        if ($file.Extension -notin @('.paa','.rvmat','.ogg','.wav','.wss','.edds','.tga','.png','.anm','.rtm')) {
            $inventory.Add([pscustomobject]@{path=$relative; bytes=$file.Length})
        }
        $include = $false
        foreach ($pattern in $rules.include) {
            if ([regex]::IsMatch($relative, $pattern, [Text.RegularExpressions.RegexOptions]::IgnoreCase)) { $include = $true; break }
        }
        if (-not $include) { continue }
        if ($file.Length -gt [long]$rules.max_file_bytes) {
            $warnings.Add(('Too large for automatic collection: {0} ({1} bytes)' -f $relative, $file.Length))
            continue
        }
        if ($partBytes + $file.Length -gt [long]$rules.part_budget_bytes -and $partBytes -gt 0) {
            $partNumber++
            $partBytes = 0
            $partPath = Join-Path $output ('Part-{0:D2}' -f $partNumber)
            New-Item -ItemType Directory -Path $partPath | Out-Null
            $parts.Add($partPath)
        }
        $destination = Join-Path $partPath $relative.Replace('/', '\')
        New-Item -ItemType Directory -Force -Path ([IO.Path]::GetDirectoryName($destination)) | Out-Null
        Copy-Item -LiteralPath $file.FullName -Destination $destination
        $header = ''
        $stream = [IO.File]::OpenRead($destination)
        try {
            $bytes = New-Object byte[] 4
            $read = $stream.Read($bytes,0,4)
            if ($read -eq 4) { $header = [Text.Encoding]::ASCII.GetString($bytes) }
        } finally { $stream.Dispose() }
        $hash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
        $records.Add([pscustomobject]@{path=$relative; bytes=$file.Length; sha256=$hash; header=$header; part=$partNumber})
        $partBytes += $file.Length
    }
}
if ($records.Count -eq 0) {
    throw ('No matching rig assets found. No game files were changed. Diagnostic output folder: ' + $output + '. Confirm that game data is extracted, not just that P: is mounted.')
}
# Include the manifest in every part so partial uploads remain identifiable.
$manifest = [pscustomobject]@{
    format='MovementLab-Rig-Assets-1'; collectedUtc=(Get-Date).ToUniversalTime().ToString('o');
    copiedCount=$records.Count; partCount=$parts.Count; files=@($records.ToArray()); warnings=@($warnings.ToArray());
    notes=@('Copied from extracted work-drive data only.', 'ODOL P3D files are binarized; this collector does not convert them to editable models.', 'No game/mod files changed; no automatic upload.');
}
$manifestJson = $manifest | ConvertTo-Json -Depth 8
$inventoryJson = ConvertTo-Json -InputObject @($inventory.ToArray()) -Depth 4
foreach ($part in $parts) {
    [IO.File]::WriteAllText((Join-Path $part 'manifest.json'), $manifestJson, (New-Object Text.UTF8Encoding($false)))
    [IO.File]::WriteAllText((Join-Path $part 'asset-inventory.json'), $inventoryJson, (New-Object Text.UTF8Encoding($false)))
    $zip = $part + '.zip'
    Compress-Archive -Path (Join-Path $part '*') -DestinationPath $zip -CompressionLevel Optimal
    if ((Get-Item -LiteralPath $zip).Length -gt 30MB) { throw ('Archive exceeded the intended upload size: ' + $zip) }
    Write-Host ('READY TO SEND: ' + $zip) -ForegroundColor Green
}
foreach ($warning in $warnings) { Write-Warning $warning }
Write-Host ('Collected {0} files into {1} ZIP part(s). Send those Part-XX.zip files in this chat.' -f $records.Count, $parts.Count)
Write-Host ('Output folder: ' + $output)
