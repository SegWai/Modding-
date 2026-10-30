param([string]$OriginalRoot = '', [string]$ProjectRoot = '')
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
# Locate extracted game data; no changes are made to the original DZ files.
$movementlabUnarmedRelative = 'DZ\anims\anm\player\moves\unarmed'
$movementlabWorkspaceRelative = 'DZ\anims\workspaces\player\player_main'
$movementlabSavedRoot = Join-Path $PSScriptRoot 'MovementLab-ProjectRoot.txt'
function Find-MovementLabProjectRoot([string]$Candidate) {
    if ([string]::IsNullOrWhiteSpace($Candidate)) { return $null }
    $Candidate = $Candidate.Trim().Trim([char]34)
    if (-not (Test-Path -LiteralPath $Candidate -PathType Container)) { return $null }
    $Candidate = (Resolve-Path -LiteralPath $Candidate).Path
    if ($Candidate -match '(?i)^(.*?)[\\/]DZ[\\/]anims[\\/]anm[\\/]player[\\/]moves[\\/]unarmed[\\/]?$') {
        $Candidate = $Matches[1].TrimEnd('\') + '\'
    } elseif ((Split-Path -Leaf $Candidate.TrimEnd('\')) -ieq 'DZ') {
        $Candidate = Split-Path -Parent $Candidate.TrimEnd('\')
    }
    if ((Test-Path -LiteralPath (Join-Path $Candidate $movementlabUnarmedRelative) -PathType Container) -and
        (Test-Path -LiteralPath (Join-Path $Candidate $movementlabWorkspaceRelative) -PathType Container)) {
        return $Candidate
    }
    return $null
}
$movementlabCandidates = @($ProjectRoot, $OriginalRoot)
if (Test-Path -LiteralPath $movementlabSavedRoot -PathType Leaf) {
    $movementlabCandidates += (Get-Content -LiteralPath $movementlabSavedRoot -Raw).Trim()
}
$movementlabCandidates += @('N:\DayZProjects', 'D:\DayZProjects', 'P:\', 'F:\DayZProjects', 'C:\DayZProjects')
foreach ($movementlabDrive in Get-PSDrive -PSProvider FileSystem) {
    if ($movementlabDrive.Root -match '^[A-Za-z]:\\$') {
        $movementlabCandidates += $movementlabDrive.Root
        $movementlabCandidates += (Join-Path $movementlabDrive.Root 'DayZProjects')
    }
}
$movementlabProjectRoot = $null
foreach ($movementlabCandidate in $movementlabCandidates) {
    $movementlabProjectRoot = Find-MovementLabProjectRoot $movementlabCandidate
    if ($movementlabProjectRoot) { break }
}
if (-not $movementlabProjectRoot) {
    Write-Host 'Extracted DayZ data was not found automatically.'
    Write-Host 'Choose your DayZProjects folder (containing DZ), or the DZ folder itself.'
    Write-Host 'If it has not been extracted, use DayZ Tools > Extract Game Data first.'
    Add-Type -AssemblyName System.Windows.Forms
    $movementlabDialog = New-Object System.Windows.Forms.FolderBrowserDialog
    try {
        $movementlabDialog.Description = 'Choose extracted DayZ data: DayZProjects or DZ folder'
        $movementlabDialog.ShowNewFolderButton = $false
        if ($movementlabDialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
            throw 'Folder selection cancelled. No original animation files were changed.'
        }
        $movementlabProjectRoot = Find-MovementLabProjectRoot $movementlabDialog.SelectedPath
    } finally {
        $movementlabDialog.Dispose()
    }
}
if (-not $movementlabProjectRoot) {
    throw 'The selected folder lacks extracted DZ\anims data. Use DayZ Tools > Extract Game Data, then select its output folder. This is not the Steam DayZ installation folder.'
}
$OriginalRoot = Join-Path $movementlabProjectRoot $movementlabUnarmedRelative
Set-Content -LiteralPath $movementlabSavedRoot -Value $movementlabProjectRoot -Encoding UTF8
Write-Host "Using extracted DayZ project: $movementlabProjectRoot"
if (-not (Test-Path -LiteralPath $OriginalRoot -PathType Container)) { throw "Original animation folder missing: $OriginalRoot" }
$movementlabRoot = (Resolve-Path -LiteralPath $OriginalRoot).Path.TrimEnd('\')
foreach ($movementlabRequired in Get-Content -LiteralPath (Join-Path $PSScriptRoot 'RequiredOriginalClips.txt')) {
    if (-not (Test-Path -LiteralPath (Join-Path $movementlabRoot $movementlabRequired) -PathType Leaf)) { throw "Original clip missing: $movementlabRequired. Restore/extract the complete unarmed folder first." }
}
$movementlabFiles = [System.Collections.Generic.SortedDictionary[string,byte[]]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($movementlabFile in Get-ChildItem -LiteralPath $movementlabRoot -Recurse -File) {
    $movementlabName = $movementlabFile.FullName.Substring($movementlabRoot.Length + 1)
    $movementlabFiles.Add($movementlabName, [System.IO.File]::ReadAllBytes($movementlabFile.FullName))
}

# Separate standing-walk variants retain root-motion displacement per frame.
# Walking L1=24/30=80%; legacy L2 variant aliases native100%, never120%.
foreach ($movementlabWalkDirection in @('B','BL','BR','F','FL','FR')) {
    $movementlabWalkName = "p_erc_walk$movementlabWalkDirection.anm"
    if (-not $movementlabFiles.ContainsKey($movementlabWalkName)) { throw "Standing walk clip missing: $movementlabWalkName" }
    $movementlabWalkOriginal = $movementlabFiles[$movementlabWalkName]
    if ($movementlabWalkOriginal.Length -lt 32 -or [System.Text.Encoding]::ASCII.GetString($movementlabWalkOriginal,0,4) -ne 'FORM' -or [System.Text.Encoding]::ASCII.GetString($movementlabWalkOriginal,8,8) -ne 'ANIMSET6' -or [System.Text.Encoding]::ASCII.GetString($movementlabWalkOriginal,20,3) -ne 'FPS' -or [System.BitConverter]::ToUInt32($movementlabWalkOriginal,28) -ne 30) { throw "Expected original 30 FPS standing clip: $movementlabWalkName" }
    foreach ($movementlabWalkTier in @(1,2)) {
        $movementlabWalkVariant = [byte[]]$movementlabWalkOriginal.Clone()
        $movementlabWalkFps = @(0,22,30)[$movementlabWalkTier]
        [System.Array]::Copy([System.BitConverter]::GetBytes([uint32]$movementlabWalkFps),0,$movementlabWalkVariant,28,4)
        $movementlabFiles.Add("StandingWalkVariants\L$movementlabWalkTier\$movementlabWalkName",$movementlabWalkVariant)
        Write-Host "Standing clip $movementlabWalkName L$movementlabWalkTier FPS=$([System.BitConverter]::ToUInt32($movementlabWalkVariant,28))"
    }
}

# Separate jogging variants:24/30=80%, same root-motion distance per frame.
foreach ($movementlabJogDirection in @('B','BL','BR','F','FL','FR')) {
    $movementlabJogName = "p_erc_run$movementlabJogDirection.anm"
    if (-not $movementlabFiles.ContainsKey($movementlabJogName)) { throw "Jogging clip missing: $movementlabJogName" }
    $movementlabJogOriginal = $movementlabFiles[$movementlabJogName]
    if ($movementlabJogOriginal.Length -lt 32 -or [System.Text.Encoding]::ASCII.GetString($movementlabJogOriginal,0,4) -ne 'FORM' -or [System.Text.Encoding]::ASCII.GetString($movementlabJogOriginal,8,8) -ne 'ANIMSET6' -or [System.Text.Encoding]::ASCII.GetString($movementlabJogOriginal,20,3) -ne 'FPS' -or [System.BitConverter]::ToUInt32($movementlabJogOriginal,28) -ne 30) { throw "Expected original 30 FPS jogging clip: $movementlabJogName" }
    $movementlabJogVariant = [byte[]]$movementlabJogOriginal.Clone()
    [System.Array]::Copy([System.BitConverter]::GetBytes([uint32]24),0,$movementlabJogVariant,28,4)
    $movementlabFiles.Add("StandingJogVariants\J80\$movementlabJogName",$movementlabJogVariant)
    Write-Host "Jogging clip $movementlabJogName J80 FPS=$([System.BitConverter]::ToUInt32($movementlabJogVariant,28))"
}

foreach ($movementlabDirection in @('b','bl','br','f','fl','fr')) {
    $movementlabOriginalName = "p_cro_walk$movementlabDirection.anm"
    if (-not $movementlabFiles.ContainsKey($movementlabOriginalName)) { throw "Missing $movementlabOriginalName" }
    $movementlabOriginalBytes = $movementlabFiles[$movementlabOriginalName]
    if ([System.BitConverter]::ToUInt32($movementlabOriginalBytes,28) -ne 30) { throw "Original FPS must be 30: $movementlabOriginalName" }
    foreach ($movementlabLevel in @(2,3,4,5)) {
        $movementlabVariant = [byte[]]$movementlabOriginalBytes.Clone()
        $movementlabFps = @(0,0,14,18,22,26)[$movementlabLevel]
        [System.Array]::Copy([System.BitConverter]::GetBytes([uint32]$movementlabFps),0,$movementlabVariant,28,4)
        $movementlabFiles.Add("WheelVariants\L$movementlabLevel\$movementlabOriginalName",$movementlabVariant)
    }
}
foreach ($movementlabDirection in @('b','bl','br','f','fl','fr')) {
    $movementlabName = "p_cro_walk$movementlabDirection.anm"
    if (-not $movementlabFiles.ContainsKey($movementlabName)) { throw "Crouch clip missing: $movementlabName" }
    $movementlabBytes = $movementlabFiles[$movementlabName]
    if ($movementlabBytes.Length -lt 32 -or [System.Text.Encoding]::ASCII.GetString($movementlabBytes,0,4) -ne 'FORM' -or [System.Text.Encoding]::ASCII.GetString($movementlabBytes,8,8) -ne 'ANIMSET6' -or [System.Text.Encoding]::ASCII.GetString($movementlabBytes,20,3) -ne 'FPS' -or [System.BitConverter]::ToUInt32($movementlabBytes,28) -ne 30) { throw "Unexpected clip format/FPS: $movementlabName. Expected the original 30 FPS file." }
    $movementlabBytes[28] = 9
    $movementlabBytes[29] = 0
    $movementlabBytes[30] = 0
    $movementlabBytes[31] = 0
}
$movementlabConfig = 'class CfgPatches { class MovementLabSlowCrouchClips { units[] = {}; weapons[] = {}; requiredVersion = 0.1; requiredAddons[] = {"DZ_Anims_Anm_Player"}; }; };'

$movementlabArmedPlan = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'Armed-Speed-Plan.json') -Raw | ConvertFrom-Json
foreach ($movementlabArmedVariant in $movementlabArmedPlan.variants) {
    $movementlabArmedPath = Join-Path $movementlabProjectRoot ($movementlabArmedVariant.source.Replace('/','\'))
    if (-not (Test-Path -LiteralPath $movementlabArmedPath -PathType Leaf)) { throw "Missing armed animation: $movementlabArmedPath" }
    $movementlabArmedBytes = [System.IO.File]::ReadAllBytes($movementlabArmedPath)
    if ($movementlabArmedBytes.Length -lt 32) { throw "Truncated armed animation: $movementlabArmedPath" }
    $movementlabArmedVersion = [System.Text.Encoding]::ASCII.GetString($movementlabArmedBytes,8,8)
    if ([System.Text.Encoding]::ASCII.GetString($movementlabArmedBytes,0,4) -ne 'FORM' -or $movementlabArmedVersion -notin @('ANIMSET5','ANIMSET6') -or [System.Text.Encoding]::ASCII.GetString($movementlabArmedBytes,20,4) -ne "FPS`0" -or $movementlabArmedBytes[24] -ne 0 -or $movementlabArmedBytes[25] -ne 0 -or $movementlabArmedBytes[26] -ne 0 -or $movementlabArmedBytes[27] -ne 4) { throw "Unsupported armed animation header: $movementlabArmedPath" }
    $movementlabArmedOriginalFps = [System.BitConverter]::ToUInt32($movementlabArmedBytes,28)
    if ($movementlabArmedOriginalFps -lt 1 -or $movementlabArmedOriginalFps -gt 240) { throw "Invalid armed animation FPS: $movementlabArmedPath" }
    [System.Array]::Copy([System.BitConverter]::GetBytes([uint32]$movementlabArmedVariant.fps),0,$movementlabArmedBytes,28,4)
    $movementlabFiles[$movementlabArmedVariant.output.Replace('/','\')] = $movementlabArmedBytes
}
$movementlabFiles['config.cpp'] = [System.Text.Encoding]::ASCII.GetBytes($movementlabConfig)
$movementlabStream = [System.IO.MemoryStream]::new()
$movementlabWriter = [System.IO.BinaryWriter]::new($movementlabStream)
function Write-MovementLabString([string]$Value) {
    $movementlabWriter.Write([System.Text.Encoding]::ASCII.GetBytes($Value))
    $movementlabWriter.Write([byte]0)
}
Write-MovementLabString ''
$movementlabWriter.Write([uint32]0x56657273)
1..4 | ForEach-Object { $movementlabWriter.Write([uint32]0) }
Write-MovementLabString 'prefix'
Write-MovementLabString 'DZ\anims\anm\player\moves\unarmed'
Write-MovementLabString ''
foreach ($movementlabEntry in $movementlabFiles.GetEnumerator()) {
    Write-MovementLabString $movementlabEntry.Key
    1..4 | ForEach-Object { $movementlabWriter.Write([uint32]0) }
    $movementlabWriter.Write([uint32]$movementlabEntry.Value.Length)
}
Write-MovementLabString ''
1..5 | ForEach-Object { $movementlabWriter.Write([uint32]0) }
foreach ($movementlabEntry in $movementlabFiles.GetEnumerator()) { $movementlabWriter.Write($movementlabEntry.Value) }
$movementlabWriter.Flush()
$movementlabBody = $movementlabStream.ToArray()
$movementlabSha = [System.Security.Cryptography.SHA1]::Create()
$movementlabDigest = $movementlabSha.ComputeHash($movementlabBody)
$movementlabWriter.Write([byte]0)
$movementlabWriter.Write($movementlabDigest)
$movementlabWriter.Flush()
$movementlabTarget = Join-Path $PSScriptRoot '@MovementLabSlowCrouchClips\Addons\MovementLabSlowCrouchClips.pbo'
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($movementlabTarget)) | Out-Null
[System.IO.File]::WriteAllBytes($movementlabTarget, $movementlabStream.ToArray())
$movementlabWriter.Dispose()
$movementlabStream.Dispose()
$movementlabSha.Dispose()
Write-Host "Prepared $($movementlabFiles.Count) resources, preserving original standing/jump/landing clips. Six crouch clips retimed 30 -> 9 FPS."
Write-Host 'Standing walk wheel:73% (22 FPS), native100%, then level3 transitions to jog80%. Default/reset73%. Original standing clips preserved.'
Write-Host 'Original files were read only and remain unchanged.'


$movementlabWorkspaceRoot = Join-Path $movementlabProjectRoot $movementlabWorkspaceRelative
if (-not (Test-Path -LiteralPath $movementlabWorkspaceRoot -PathType Container)) { throw 'Original player_main workspace folder missing.' }
$movementlabFiles = [System.Collections.Generic.SortedDictionary[string,byte[]]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($movementlabFile in Get-ChildItem -LiteralPath $movementlabWorkspaceRoot -Recurse -File) {
    $movementlabName = $movementlabFile.FullName.Substring($movementlabWorkspaceRoot.Length + 1)
    $movementlabFiles.Add($movementlabName,[System.IO.File]::ReadAllBytes($movementlabFile.FullName))
}
foreach ($movementlabPatch in Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'WorkspacePatches') -File) {
    if (-not $movementlabFiles.ContainsKey($movementlabPatch.Name)) { throw "Original workspace resource missing: $($movementlabPatch.Name)" }
    $movementlabFiles[$movementlabPatch.Name] = [System.IO.File]::ReadAllBytes($movementlabPatch.FullName)
}

foreach ($movementlabArmedInstance in $movementlabArmedPlan.instances) {
    $movementlabInstanceName = $movementlabArmedInstance.file.Replace('/','\')
    if (-not $movementlabFiles.ContainsKey($movementlabInstanceName)) { throw "Missing animation instance: $movementlabInstanceName" }
    $movementlabInstanceText = [System.Text.Encoding]::UTF8.GetString($movementlabFiles[$movementlabInstanceName])
    foreach ($movementlabReplace in $movementlabArmedInstance.replace.PSObject.Properties) {
        $movementlabRowPattern = '"' + [regex]::Escape($movementlabReplace.Name) + '"\s+"[^"\r\n]+"'
        $movementlabNewRow = '"' + $movementlabReplace.Name + '" "' + $movementlabReplace.Value + '"'
        $movementlabInstanceText = [regex]::Replace($movementlabInstanceText,$movementlabRowPattern,$movementlabNewRow)
    }
    $movementlabExtraRows = ''
    foreach ($movementlabAddition in $movementlabArmedInstance.add.PSObject.Properties) {
        $movementlabExtraRows += '   "' + $movementlabAddition.Name + '" "' + $movementlabAddition.Value + '"' + "`r`n"
    }
    $movementlabAnimationsAt = $movementlabInstanceText.IndexOf('$animations')
    if ($movementlabAnimationsAt -lt 0) { throw "Missing animation mapping block: $movementlabInstanceName" }
    $movementlabInsertAt = $movementlabInstanceText.IndexOf('{',$movementlabAnimationsAt) + 1
    $movementlabInstanceText = $movementlabInstanceText.Insert($movementlabInsertAt,"`r`n" + $movementlabExtraRows)
    $movementlabFiles[$movementlabInstanceName] = [System.Text.Encoding]::UTF8.GetBytes($movementlabInstanceText)
}
$movementlabFiles['config.cpp'] = [System.Text.Encoding]::ASCII.GetBytes('class CfgPatches { class MovementLabCrouchWheelWorkspace { units[] = {}; weapons[] = {}; requiredVersion = 0.1; requiredAddons[] = {"DZ_Anims_Cfg", "MovementLabSlowCrouchClips"}; }; };')
$movementlabStream = [System.IO.MemoryStream]::new()
$movementlabWriter = [System.IO.BinaryWriter]::new($movementlabStream)
function Write-MovementLabString([string]$Value) {
    $movementlabWriter.Write([System.Text.Encoding]::ASCII.GetBytes($Value))
    $movementlabWriter.Write([byte]0)
}
Write-MovementLabString ''
$movementlabWriter.Write([uint32]0x56657273)
1..4 | ForEach-Object { $movementlabWriter.Write([uint32]0) }
Write-MovementLabString 'prefix'
Write-MovementLabString 'DZ\anims\workspaces\player\player_main'
Write-MovementLabString ''
foreach ($movementlabEntry in $movementlabFiles.GetEnumerator()) {
    Write-MovementLabString $movementlabEntry.Key
    1..4 | ForEach-Object { $movementlabWriter.Write([uint32]0) }
    $movementlabWriter.Write([uint32]$movementlabEntry.Value.Length)
}
Write-MovementLabString ''
1..5 | ForEach-Object { $movementlabWriter.Write([uint32]0) }
foreach ($movementlabEntry in $movementlabFiles.GetEnumerator()) { $movementlabWriter.Write($movementlabEntry.Value) }
$movementlabWriter.Flush()
$movementlabBody = $movementlabStream.ToArray()
$movementlabSha = [System.Security.Cryptography.SHA1]::Create()
$movementlabDigest = $movementlabSha.ComputeHash($movementlabBody)
$movementlabWriter.Write([byte]0)
$movementlabWriter.Write($movementlabDigest)
$movementlabWriter.Flush()
$movementlabTarget = Join-Path $PSScriptRoot '@MovementLabSlowCrouchClips\Addons\MovementLabCrouchWheelWorkspace.pbo'
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($movementlabTarget)) | Out-Null
[System.IO.File]::WriteAllBytes($movementlabTarget, $movementlabStream.ToArray())
$movementlabWriter.Dispose()
$movementlabStream.Dispose()
$movementlabSha.Dispose()
Write-Host 'Six-level workspace prepared. Originals unchanged.'
