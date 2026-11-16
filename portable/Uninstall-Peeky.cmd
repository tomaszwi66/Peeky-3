@echo off
setlocal
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" -I "%~dp0Uninstall.py" %*
) else if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" -I "%~dp0Uninstall.py" %*
) else if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe" (
    "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe" -I "%~dp0Uninstall.py" %*
) else (
    py -3 -I "%~dp0Uninstall.py" %*
)
set "peeky_result=%errorlevel%"
if not "%peeky_result%"=="0" echo Removal did not finish. See the message above.
if "%~1"=="" pause
exit /b %peeky_result%
