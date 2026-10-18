@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Collect-Ragdoll-Assets.ps1" %*
pause
