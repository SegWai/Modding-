@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "movementlabGameDir=D:\SteamLibrary\steamapps\common\DayZ"
set "movementlabTestDir=%~dp0"
set "movementlabMode=%~1"

if /I "%movementlabMode%"=="baseline" goto check_game
if /I "%movementlabMode%"=="mod" goto check_game
echo Open Launch-Baseline.cmd or Launch-With-Mod.cmd.
exit /b 1

:check_game
if not exist "%movementlabGameDir%\DayZDiag_x64.exe" (
    echo DayZDiag_x64.exe was not found in the configured DayZ folder.
    exit /b 1
)
if not exist "%movementlabTestDir%Missions\MovementLabOffline.ChernarusPlus\init.c" (
    echo The test mission is missing. Extract the entire ZIP together.
    exit /b 1
)
powershell.exe -NoProfile -NonInteractive -Command "if (Get-Process -Name DayZ_x64,DayZDiag_x64 -ErrorAction SilentlyContinue) { exit 1 }"
if errorlevel 1 (
    echo Close any running DayZ game first, then open this launcher again.
    exit /b 1
)
if /I "%movementlabMode%"=="mod" goto launch_mod

:launch_baseline
if not exist "%movementlabTestDir%Profiles\Baseline" mkdir "%movementlabTestDir%Profiles\Baseline"
if not exist "%movementlabTestDir%Profiles\Baseline" (
    echo Could not create the baseline profile folder.
    exit /b 1
)
echo Starting the offline baseline. Steam must be running.
start "" /D "%movementlabGameDir%" "%movementlabGameDir%\DayZDiag_x64.exe" "-mission=%movementlabTestDir%Missions\MovementLabOffline.ChernarusPlus" "-profiles=%movementlabTestDir%Profiles\Baseline" -nosplash -noPause -filePatching -doLogs -scriptDebug=true
exit /b 0

:launch_mod
if exist "%movementlabTestDir%@MovementLabRuntimeTest\Addons\MovementLabRuntimeTest.pbo\" (
    echo The expected PBO path is a directory, not a file. Use the Addons directory as the builder destination.
    exit /b 1
)
if not exist "%movementlabTestDir%@MovementLabRuntimeTest\Addons\MovementLabRuntimeTest.pbo" (
    echo The test PBO is missing. Prepare the animation and pack the source with Addon Builder first.
    exit /b 1
)
if not exist "%movementlabTestDir%Profiles\WithMod" mkdir "%movementlabTestDir%Profiles\WithMod"
if not exist "%movementlabTestDir%Profiles\WithMod" (
    echo Could not create the test profile folder.
    exit /b 1
)
echo Starting the offline arm-lift test. Steam must be running.
start "" /D "%movementlabGameDir%" "%movementlabGameDir%\DayZDiag_x64.exe" "-mission=%movementlabTestDir%Missions\MovementLabOffline.ChernarusPlus" "-mod=%movementlabTestDir%@MovementLabRuntimeTest" "-profiles=%movementlabTestDir%Profiles\WithMod" -nosplash -noPause -filePatching -doLogs -scriptDebug=true
exit /b 0
