@echo off
echo Building Dialogue Venture Game Engine...
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
echo Building executable...
python -m PyInstaller build_config.spec

REM Check if build was successful
if exist "dist\DialogueVenture.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo Executable created: dist\DialogueVenture.exe
    echo File size: 
    for %%A in ("dist\DialogueVenture.exe") do echo %%~zA bytes
    echo.
    echo You can now run: dist\DialogueVenture.exe
    echo ========================================
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Check the output above for errors.
)

pause