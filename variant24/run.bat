@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONUTF8=1
py -3 --version >nul 2>&1
if errorlevel 1 (
    echo Python 3 could not be started. Install Python 3 with the Python Launcher.
    pause
    exit /b 1
)
py -3 src\emulator.py --vfs vfs\sample.json
if errorlevel 1 (
    echo.
    echo Emulator stopped with an error. See the message above.
)
echo.
pause
