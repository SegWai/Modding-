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
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%movementlabTestDir%Prepare-Crouch-Clips.ps1"
if errorlevel 1 goto failed
echo Linked scroll: walk121 enters jog80; jog79 returns walk85; jog100 then101 enters sprint; sprint99 returns jog100. Steam must be running.
start "" /D "%movementlabGameDir%" "%movementlabGameDir%\DayZDiag_x64.exe" "-mission=%movementlabTestDir%Missions\MovementLabMovementLogic.ChernarusPlus" "-mod=%movementlabTestDir%@MovementLabStartGate;%movementlabTestDir%@MovementLabSlowCrouchClips" "-profiles=%movementlabTestDir%Profiles\MovementLogic" -nosplash -noPause -filePatching -doLogs -scriptDebug=true
exit /b 0
:failed
pause
exit /b 1
