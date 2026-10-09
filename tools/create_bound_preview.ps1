# Create a separate preview whose walking slots already contain the test clip.
# Run locally in Windows PowerShell after Workbench has compiled the animation.
$ErrorActionPreference = 'Stop'
$movementlabRoot = 'D:\DayZProjects'
$movementlabFolder = Join-Path $movementlabRoot 'MovementLabWorkbench\TestAnimations'
$movementlabClip = Join-Path $movementlabFolder 'MovementLab_ArmLift_Test.anm'
$movementlabBase = Join-Path $movementlabRoot 'DZ\anims\workspaces\player\player_main\player_main.asi'
$movementlabInstance = Join-Path $movementlabFolder 'MovementLab_ArmLift_Bound.asi'
$movementlabWorkspace = Join-Path $movementlabFolder 'MovementLab_ArmLift_Bound.aw'

if (-not (Test-Path -LiteralPath $movementlabClip -PathType Leaf)) {
    throw 'The compiled MovementLab_ArmLift_Test.anm is missing.'
}
if ((Get-Item -LiteralPath $movementlabClip).Length -eq 0) {
    throw 'The compiled animation is empty. Check the Workbench import console.'
}
if ((Test-Path -LiteralPath $movementlabInstance) -or (Test-Path -LiteralPath $movementlabWorkspace)) {
    throw 'The Bound preview files already exist. They have been preserved; open MovementLab_ArmLift_Bound.aw.'
}

# Read real slot names from this installed version rather than guessing them.
$movementlabText = Get-Content -LiteralPath $movementlabBase -Raw
$movementlabText = [regex]::Replace($movementlabText, '(?m)^\s*//[^\r\n]*', '')
$movementlabPairs = [regex]::Matches($movementlabText, '"(?<slot>[^"\r\n]+)"\s+"(?<animation>[^"\r\n]+\.anm)"')
$movementlabSlots = @($movementlabPairs | Where-Object {
    $_.Groups['animation'].Value -match 'walk' -and
    $_.Groups['animation'].Value -notmatch 'walkie'
} | ForEach-Object {
    $_.Groups['slot'].Value
} | Sort-Object -Unique)
if ($movementlabSlots.Count -eq 0) {
    throw 'No walking assignments were found in player_main.asi. No preview files were written; report this message.'
}

$movementlabHeader = @'
$animsetinstance {
 #template "{F0C651DE8E24A5DE}DZ/anims/workspaces/player/player_main/player_main.ast"
 #nparents 1
 #parent "{0F5E6205A5E823C3}DZ/anims/workspaces/player/player_main/player_main.asi"
 $animations {
'@
$movementlabRows = @($movementlabSlots | ForEach-Object {
    '  "' + $_ + '" "MovementLabWorkbench/TestAnimations/MovementLab_ArmLift_Test.anm"'
})
$movementlabInstanceText = $movementlabHeader + "`n" + ($movementlabRows -join "`n") + "`n }`n}`n"
$movementlabWorkspaceText = @'
$animWorkspace {
 #animSetTemplate "{F0C651DE8E24A5DE}DZ/anims/workspaces/player/player_main/player_main.ast"
 #NanimSetInstances 1
 #animSetInstance "MovementLabWorkbench/TestAnimations/MovementLab_ArmLift_Bound.asi"
 #previewModel "{82410A0A5E1022A1}DZ/anims/workspaces/player/Models/player_f_editorpreview.xob"
 #previewModel "{D470A4E7581CCE23}DZ/anims/workspaces/player/Models/player_m_editorpreview.xob"
 #animGraph "{E23437DEB9E1712D}DZ/anims/workspaces/player/player_main/player_main.agr"
 #synctable "{8F89313B7FBB0B66}DZ/anims/workspaces/player/Player_SyncTable.asy"
}
'@

# Create only new files; never replace the user's existing instance/workspace.
$movementlabCreated = [System.Collections.Generic.List[string]]::new()
try {
    foreach ($movementlabOutput in @(
        @{ Path = $movementlabInstance; Text = $movementlabInstanceText },
        @{ Path = $movementlabWorkspace; Text = $movementlabWorkspaceText }
    )) {
        $movementlabStream = [IO.File]::Open($movementlabOutput.Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write)
        $movementlabCreated.Add($movementlabOutput.Path)
        try {
            $movementlabBytes = [Text.Encoding]::ASCII.GetBytes($movementlabOutput.Text)
            $movementlabStream.Write($movementlabBytes, 0, $movementlabBytes.Length)
        } finally {
            $movementlabStream.Dispose()
        }
    }
} catch {
    foreach ($movementlabCreatedPath in $movementlabCreated) {
        Remove-Item -LiteralPath $movementlabCreatedPath -ErrorAction SilentlyContinue
    }
    throw
}
Write-Host ('Created a separate preview with {0} walking slots assigned to the arm-lift clip.' -f $movementlabSlots.Count)
Write-Host 'Open MovementLab_ArmLift_Bound.aw and select the MovementLab_ArmLift_Bound instance.'
Write-Host ('Use this Anim Sets filter: {0}' -f $movementlabSlots[0])
Write-Host 'Select the assigned animation cell beside that source and press Play. The test lasts four seconds.'
