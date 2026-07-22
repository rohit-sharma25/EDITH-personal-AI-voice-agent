@echo off
title E.D.I.T.H. Local Assistant
echo Initializing E.D.I.T.H. Environment...

:: Navigate to the script's directory
cd /d "%~dp0"

:: Check if virtual environment exists
if not exist "edith\venv\Scripts\python.exe" (
    echo Error: Virtual environment not found in edith\venv
    pause
    exit /b 1
)

:: Run the python script
"edith\venv\Scripts\python.exe" -u "edith\run_edith.py"

pause
