@echo off
REM Sombra Desktop - Windows Build Script
REM Run this on Windows machine with Python 3.10+ installed

setlocal enabledelayedexpansion

echo ========================================
echo    Sombra Desktop - Windows Build
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+
    exit /b 1
)

REM Create venv if not exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate venv
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -e ".[dev]"

REM Install PyInstaller explicitly
pip install pyinstaller>=6.0.0

REM Check for .env file
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Copy .env.example to .env and configure before running the app.
    echo.
    if exist ".env.example" (
        copy .env.example .env
        echo Created .env from .env.example - please edit it!
    )
)

REM Build with PyInstaller
echo.
echo Building executable...
pyinstaller --clean --noconfirm sombra.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    exit /b 1
)

echo.
echo ========================================
echo    Build Complete!
echo ========================================
echo.
echo Output: dist\Sombra\
echo Executable: dist\Sombra\Sombra.exe
echo.
echo To create installer, run:
echo   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
echo.

pause
