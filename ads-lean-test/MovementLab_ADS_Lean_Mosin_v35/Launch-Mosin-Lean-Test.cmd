@echo off
setlocal EnableExtensions DisableDelayedExpansion
echo Starting Mosin ADS lean v35. In game: F7 compare, F8 inspect, F9 measurements, F10 NPC pause.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Launch-Test.ps1"
if errorlevel 1 pause
