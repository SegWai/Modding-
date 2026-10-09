@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "movementlabClipSource=D:\DayZProjects\MovementLabWorkbench\TestAnimations\MovementLab_ArmLift_Test.anm"
set "movementlabClipTarget=%~dp0MovementLabRuntimeTest\Animations\MovementLab_ArmLift_Test.anm"
set "movementlabAddonDir=%~dp0@MovementLabRuntimeTest\Addons"

if not exist "%movementlabClipSource%" (
    echo The compiled arm-lift animation is missing from the Workbench test folder.
    goto failed
)
for %%A in ("%movementlabClipSource%") do if %%~zA EQU 0 (
    echo The compiled animation is empty.
    goto failed
)
if not exist "%~dp0MovementLabRuntimeTest\Animations\MovementLab_ArmLift_Greeting.asi" (
    echo The mod source is missing. Extract the entire ZIP together.
    goto failed
)
if exist "%movementlabClipTarget%" (
    fc /b "%movementlabClipSource%" "%movementlabClipTarget%" >nul
    if errorlevel 1 (
        echo A different animation already exists in the destination. It has been preserved.
        goto failed
    )
) else (
    copy /b "%movementlabClipSource%" "%movementlabClipTarget%" >nul
    if errorlevel 1 goto failed
)
if not exist "%movementlabAddonDir%" mkdir "%movementlabAddonDir%"
if not exist "%movementlabAddonDir%" goto failed
echo The existing compiled animation is ready in the new mod source folder.
echo Next, pack MovementLabRuntimeTest into @MovementLabRuntimeTest\Addons using Addon Builder.
pause
exit /b 0

:failed
echo Preparation stopped. Send the message above so we can fix it.
pause
exit /b 1
