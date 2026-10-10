@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "movementlabGameDir=D:\SteamLibrary\steamapps\common\DayZ"
set "movementlabTestDir=%~dp0"
if not exist "%movementlabGameDir%\DayZDiag_x64.exe" (
    echo DayZDiag_x64.exe was not found. Check movementlabGameDir in this launcher.
    goto failed
)
if not exist "%movementlabTestDir%Missions\MovementLabMovementLogic.ChernarusPlus\init.c" (
    echo Extract the entire ZIP together before launching.
    goto failed
)
if not exist "%movementlabTestDir%@MovementLabStartGate\Addons\MovementLabStartGate.pbo" (
    echo The included walking-start script PBO is missing. Extract the entire ZIP together.
    goto failed
)
powershell.exe -NoProfile -NonInteractive -Command "if (Get-Process -Name DayZ_x64,DayZDiag_x64 -ErrorAction SilentlyContinue) { exit 1 }"
if errorlevel 1 (
    echo Close the running DayZ game first.
    goto failed
)
if not exist "%movementlabTestDir%Profiles\MovementLogic" mkdir "%movementlabTestDir%Profiles\MovementLogic"
if not exist "%movementlabTestDir%Profiles\MovementLogic" (
    echo Could not create the test profile folder.
    goto failed
)
echo Starting v15: original v11 movement plus v14 moving reversals. Steam must be running. The walking-start script mod is included.
start "" /D "%movementlabGameDir%" "%movementlabGameDir%\DayZDiag_x64.exe" "-mission=%movementlabTestDir%Missions\MovementLabMovementLogic.ChernarusPlus" "-mod=%movementlabTestDir%@MovementLabStartGate" "-profiles=%movementlabTestDir%Profiles\MovementLogic" -nosplash -noPause -filePatching -doLogs -scriptDebug=true
exit /b 0
:failed
pause
exit /b 1
