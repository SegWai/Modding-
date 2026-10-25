@echo off
setlocal EnableExtensions DisableDelayedExpansion
echo Mosin ADS lean test v4
echo 1. Custom pose test - F7 native comparison, F8 third-person inspection
echo 2. Native workspace baseline - use this if option 1 crashes at startup
choice /c 12 /n /m "Choose 1 or 2: "
set "mlLeanMode="
if errorlevel 2 set "mlLeanMode=-NativeBaseline"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Launch-Test.ps1" %mlLeanMode%
if errorlevel 1 pause
