@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0" || (echo Failed to enter project directory.&pause&exit /b 1)
py --version >nul 2>&1
if errorlevel 1 (echo Python Launcher ^(py^) was not found. Install Python 3.9+ with the Windows launcher.&pause&exit /b 1)
py -m pip --version >nul 2>&1
if errorlevel 1 (echo pip is unavailable for the selected Python installation.&pause&exit /b 1)
py -m app.main
if errorlevel 1 (echo.&echo ALIS DEJA VU stopped with an error.&pause&exit /b 1)
