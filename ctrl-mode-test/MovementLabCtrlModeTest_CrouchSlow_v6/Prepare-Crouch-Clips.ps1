param([string]$OriginalRoot = 'D:\DayZProjects\DZ\anims\anm\player\moves\unarmed')
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
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
foreach ($movementlabDirection in @('b','bl','br','f','fl','fr')) {
    $movementlabName = "p_cro_walk$movementlabDirection.anm"
    if (-not $movementlabFiles.ContainsKey($movementlabName)) { throw "Crouch clip missing: $movementlabName" }
    $movementlabBytes = $movementlabFiles[$movementlabName]
    if ($movementlabBytes.Length -lt 32 -or [System.Text.Encoding]::ASCII.GetString($movementlabBytes,0,4) -ne 'FORM' -or [System.Text.Encoding]::ASCII.GetString($movementlabBytes,8,8) -ne 'ANIMSET6' -or [System.Text.Encoding]::ASCII.GetString($movementlabBytes,20,3) -ne 'FPS' -or [System.BitConverter]::ToUInt32($movementlabBytes,28) -ne 30) { throw "Unexpected clip format/FPS: $movementlabName. Expected the original 30 FPS file." }
    $movementlabBytes[28] = 6
    $movementlabBytes[29] = 0
    $movementlabBytes[30] = 0
    $movementlabBytes[31] = 0
}
$movementlabConfig = 'class CfgPatches { class MovementLabSlowCrouchClips { units[] = {}; weapons[] = {}; requiredVersion = 0.1; requiredAddons[] = {"DZ_Anims_Anm_Player"}; }; };'
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
Write-Host "Prepared $($movementlabFiles.Count) resources, preserving original standing/jump/landing clips. Six crouch clips retimed 30 -> 6 FPS."
Write-Host 'Original files were read only and remain unchanged.'
