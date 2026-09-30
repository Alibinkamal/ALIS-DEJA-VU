@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0" || (echo Failed to enter project directory.&pause&exit /b 1)
py --version >nul 2>&1
if errorlevel 1 (echo Python Launcher ^(py^) was not found.&pause&exit /b 1)
py -m pip install --upgrade pyinstaller
if errorlevel 1 (echo Failed to install PyInstaller.&pause&exit /b 1)
py -m pip install -r requirements.txt
if errorlevel 1 (echo Failed to install dependencies.&pause&exit /b 1)
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
py -m PyInstaller --noconfirm --clean --name="ALIS DEJA VU" --onefile --windowed --add-data="%CD%\resources;resources" --collect-submodules=rawpy app/main.py
if errorlevel 1 (echo Build failed.&pause&exit /b 1)
echo.
echo Build complete: dist\ALIS DEJA VU.exe
pause
