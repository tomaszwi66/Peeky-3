@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
    py -3.11 -m venv ".venv"
    if errorlevel 1 (
        echo Install Python 3.11 for Windows x64 from python.org with the Python launcher.
        pause
        exit /b 1
    )
)
".venv\Scripts\python.exe" "Setup.py"
if errorlevel 1 (
    echo Setup did not complete. See the error above.
    pause
    exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" "%~dp0Start.pyw"
