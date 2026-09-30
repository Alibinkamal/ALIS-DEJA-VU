@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ============================================================
REM ALIS DEJA VU - Windows Application Launcher
REM ============================================================
REM
REM This script launches the application using the Windows Python Launcher
REM It supports paths with spaces and Unicode/Arabic characters
REM

cd /d "%~dp0" || (
    echo Error: Could not change to application directory
    pause
    exit /b 1
)

REM Check if Python is available
py -c "import sys; print(sys.version)" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Python is not installed or not available
    echo ============================================================
    echo.
    echo Please install Python 3.9 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add python.exe to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed
py -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing required dependencies...
    echo.
    py -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        echo Please check your internet connection and try again
        pause
        exit /b 1
    )
)

REM Launch the application
echo.
echo ============================================================
echo ALIS DEJA VU - Starting...
echo ============================================================
echo.

py -m app.main

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    echo Please check the error message above
    pause
    exit /b 1
)

exit /b 0
