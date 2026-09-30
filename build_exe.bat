@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ============================================================
REM ALIS DEJA VU - Build Windows Executable
REM ============================================================
REM
REM This script creates a standalone Windows .exe using PyInstaller
REM

cd /d "%~dp0" || (
    echo Error: Could not change to build directory
    pause
    exit /b 1
)

echo.
echo ============================================================
echo ALIS DEJA VU - Build System
echo ============================================================
echo.

REM Check Python availability
py -c "import sys; print(sys.version)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install PyInstaller if not present
echo Checking for PyInstaller...
py -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    py -m pip install PyInstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Install all dependencies
echo Installing application dependencies...
py -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Create build directory
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
mkdir dist

REM Run PyInstaller
echo.
echo Building executable...
echo.

py -m PyInstaller ^
    --name="ALIS DEJA VU" ^
    --icon="app/resources/app_icon.ico" ^
    --onefile ^
    --windowed ^
    --add-data="app/resources:resources" ^
    --add-data="app/ui/styles:ui/styles" ^
    --hidden-import=PySide6 ^
    --hidden-import=numpy ^
    --hidden-import=PIL ^
    --hidden-import=cv2 ^
    --collect-all=PySide6 ^
    app/main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Build completed successfully!
echo ============================================================
echo.
echo Executable location:
echo   dist\ALIS DEJA VU.exe
echo.
pause
exit /b 0
