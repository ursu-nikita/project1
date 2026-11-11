@echo off
cd /d "%~dp0.."
set PYTHONUTF8=1
for %%C in (test cycle minimal depth filter) do (
    py -3 src\main.py examples\%%C.ini
    if errorlevel 1 exit /b 1
)
py -3 -m unittest discover -s tests -v
pause
