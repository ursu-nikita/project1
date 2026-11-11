@echo off
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONUTF8=1
if "%~1"=="" (
    py -3 src\main.py examples\test.ini
) else (
    py -3 src\main.py "%~1"
)
pause
