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
echo Starting movement test v3. Steam must be running. F7 switches heavier with braking and vanilla.
start "" /D "%movementlabGameDir%" "%movementlabGameDir%\DayZDiag_x64.exe" "-mission=%movementlabTestDir%Missions\MovementLabMovementLogic.ChernarusPlus" "-profiles=%movementlabTestDir%Profiles\MovementLogic" -nosplash -noPause -filePatching -doLogs -scriptDebug=true
exit /b 0
:failed
pause
exit /b 1
