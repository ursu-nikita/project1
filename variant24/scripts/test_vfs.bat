@echo off
cd /d "%~dp0.."
for %%F in (minimal files sample) do (
  echo ==== %%F ====
  echo vfs-info | python src\emulator.py --vfs vfs\%%F.json
)
