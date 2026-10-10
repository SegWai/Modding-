@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "movementlabGameDir=D:\SteamLibrary\steamapps\common\DayZ"
set "movementlabTestDir=%~dp0"
if not exist "%movementlabGameDir%\DayZDiag_x64.exe" (
    echo DayZDiag_x64.exe was not found. Check movementlabGameDir in this launcher.
    goto failed
)
if not exist "%movementlabTestDir%Missions\MovementLabJogWalkBlend.ChernarusPlus\init.c" (
    echo Extract the entire ZIP together before launching.
    goto failed
)
if not exist "%movementlabTestDir%@MovementLabStartGate\Addons\MovementLabStartGate.pbo" (
    echo The included jog-to-walk blend script PBO is missing. Extract the entire ZIP together.
    goto failed
)
powershell.exe -NoProfile -NonInteractive -Command "if (Get-Process -Name DayZ_x64,DayZDiag_x64 -ErrorAction SilentlyContinue) { exit 1 }"
if errorlevel 1 (
    echo Close the running DayZ game first.
    goto failed
)
if not exist "%movementlabTestDir%Profiles\JogWalkBlend" mkdir "%movementlabTestDir%Profiles\JogWalkBlend"
if not exist "%movementlabTestDir%Profiles\JogWalkBlend" (
    echo Could not create the test profile folder.
    goto failed
)
echo Starting isolated jog-to-walk blend v1. Jog with W, then HOLD Ctrl to walk. F7 compares vanilla. Steam must be running.
start "" /D "%movementlabGameDir%" "%movementlabGameDir%\DayZDiag_x64.exe" "-mission=%movementlabTestDir%Missions\MovementLabJogWalkBlend.ChernarusPlus" "-mod=%movementlabTestDir%@MovementLabStartGate" "-profiles=%movementlabTestDir%Profiles\JogWalkBlend" -nosplash -noPause -filePatching -doLogs -scriptDebug=true
exit /b 0
:failed
pause
exit /b 1
