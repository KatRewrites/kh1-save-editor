@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  KH1 Save Editor - Windows EXE Builder
echo ============================================
echo.

set "PYTHON_CMD="
where py >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=py -3"

if not defined PYTHON_CMD (
    where python >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo ERROR: Python 3 was not found.
    echo Install it from https://www.python.org/downloads/windows/
    echo Enable "Add python.exe to PATH" during installation.
    pause
    exit /b 1
)

%PYTHON_CMD% -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.8 or newer is required.
    pause
    exit /b 1
)

%PYTHON_CMD% -c "import tkinter"
if errorlevel 1 (
    echo ERROR: tkinter is missing from this Python installation.
    pause
    exit /b 1
)

echo Installing or updating PyInstaller...
%PYTHON_CMD% -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo ERROR: PyInstaller installation failed.
    pause
    exit /b 1
)

echo.
echo Running tests...
%PYTHON_CMD% -m unittest discover -s tests -v
if errorlevel 1 (
    echo ERROR: Tests failed. The executable will not be built.
    pause
    exit /b 1
)

echo.
echo Building standalone executable...
%PYTHON_CMD% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name "KH1_Save_Editor" ^
    kh1_save_editor.py

if not exist "dist\KH1_Save_Editor.exe" (
    echo.
    echo BUILD FAILED. Review the output above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  BUILD COMPLETE
echo  dist\KH1_Save_Editor.exe
echo ============================================
echo.
pause
