@echo off
setlocal
call "%~dp0Launch-Test.cmd" baseline
if errorlevel 1 pause
exit /b
