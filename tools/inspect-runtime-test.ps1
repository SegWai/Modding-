# Read-only report for the next offline animation test.
# Copy this text into Windows PowerShell. No administrator rights are needed.
$movementlabProbeRoot = 'D:\DayZProjects'
$movementlabProbeInstance = Join-Path $movementlabProbeRoot 'MovementLabWorkbench\TestAnimations\MovementLab_ArmLift_Preview.asi'
$movementlabProbeBase = Join-Path $movementlabProbeRoot 'DZ\anims\workspaces\player\player_main\player_main.asi'

Write-Host 'Saved arm-lift assignment:'
if (Test-Path -LiteralPath $movementlabProbeInstance -PathType Leaf) {
    $movementlabProbeAssignments = @(Select-String -LiteralPath $movementlabProbeInstance -Pattern 'MovementLab_ArmLift_Test\.anm' | Select-Object -ExpandProperty Line)
    if ($movementlabProbeAssignments.Count -gt 0) {
        $movementlabProbeAssignments | Select-Object -First 3
    } else {
        Write-Host 'No arm-lift assignment saved in MovementLab_ArmLift_Preview.asi yet.'
    }
} else {
    Write-Host 'MovementLab_ArmLift_Preview.asi was not found at the expected path.'
}

Write-Host 'Installed gesture mappings:'
if (Test-Path -LiteralPath $movementlabProbeBase -PathType Leaf) {
    $movementlabProbeGestures = @(Select-String -LiteralPath $movementlabProbeBase -Pattern 'greet|wave|sos' | Select-Object -ExpandProperty Line)
    if ($movementlabProbeGestures.Count -gt 0) {
        $movementlabProbeGestures | Select-Object -First 12
    } else {
        Write-Host 'No greet/wave/sos names found. The gesture naming needs inspection.'
    }
} else {
    Write-Host 'player_main.asi was not found at the expected path.'
}

Write-Host 'Diagnostic executable:'
$movementlabProbeExecutables = @(
    foreach ($movementlabProbeInstall in @(
        'D:\SteamLibrary\steamapps\common\DayZ',
        'D:\SteamLibrary\steamapps\common\DayZ Tools'
    )) {
        if (Test-Path -LiteralPath $movementlabProbeInstall -PathType Container) {
            Get-ChildItem -LiteralPath $movementlabProbeInstall -Recurse -File -Filter 'DayZDiag*.exe' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
        }
    }
)
if ($movementlabProbeExecutables.Count -gt 0) {
    $movementlabProbeExecutables
} else {
    Write-Host 'No DayZDiag executable found in the two expected installation folders.'
}
