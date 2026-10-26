@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Build-Left-Walk-Blender.ps1" %*
pause
