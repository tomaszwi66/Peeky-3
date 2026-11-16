@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -File "%~dp0Install.ps1"
if errorlevel 1 (
    echo Installation stopped. See the message above.
    pause
    exit /b 1
)
echo Installation complete. Open Peeky 3 from your desktop.
pause
