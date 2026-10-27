@echo off
setlocal EnableExtensions DisableDelayedExpansion
echo Starting lean v138. Ctrl+F8: arm comparison. L: record/stop. Colon: loop. Hold L: clear.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Launch-Test.ps1"
if errorlevel 1 pause
