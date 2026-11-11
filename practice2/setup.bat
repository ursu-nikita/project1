@echo off
cd /d "%~dp0"
if not exist tools mkdir tools
powershell -NoProfile -Command "Invoke-WebRequest 'https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar' -OutFile 'tools/plantuml.jar'"
pause
