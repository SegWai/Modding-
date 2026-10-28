@echo off
setlocal EnableExtensions DisableDelayedExpansion
echo Starting ambidextrous shoulder test. Configure the side mouse button in DayZ Controls.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Launch-Test.ps1"
if errorlevel 1 pause
