@echo off
REM Whistle Assistant Launcher for Windows
REM This script activates the venv and runs the assistant

cd /d "%~dp0"

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Installing/updating dependencies...
pip install -q -e ".[mic]"

echo.
echo Starting Whistle Assistant...
echo Wake words: "Hey Assistant", "Okay Assistant", "Whistle", "Computer"
echo Press Ctrl+C to stop.
echo.

python -m whistle_assistant %*