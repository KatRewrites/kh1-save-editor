@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if not errorlevel 1 (
    py -3 kh1_save_editor.py
    if errorlevel 1 pause
    exit /b
)

where python >nul 2>&1
if not errorlevel 1 (
    python kh1_save_editor.py
    if errorlevel 1 pause
    exit /b
)

echo.
echo Python 3 was not found.
echo Install Python from https://www.python.org/downloads/windows/
echo Enable "Add python.exe to PATH", then run this file again.
echo.
pause
exit /b 1
