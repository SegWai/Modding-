@echo off
setlocal
call "%~dp0Launch-Test.cmd" mod
if errorlevel 1 pause
exit /b
