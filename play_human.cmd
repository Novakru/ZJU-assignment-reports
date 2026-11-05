@echo off
cd /d "%~dp0"
python submission\uttt.py human --games 10 --output experients\assignment2\human_games.json
if errorlevel 1 goto done
powershell -NoProfile -ExecutionPolicy Bypass -File report\build.ps1
:done
pause
