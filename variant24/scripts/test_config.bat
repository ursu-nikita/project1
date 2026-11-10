@echo off
cd /d "%~dp0.."
python src/emulator.py --config config.json --vfs vfs/files.json --script scripts/stage2.txt
