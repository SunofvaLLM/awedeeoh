@echo off
:: Awedeeoh Project Installer for Windows
:: This script automates the setup process.
:: It must be run with Administrator privileges.

:: 1. Check for Administrator Privileges
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ======================================================
echo ==           Awedeeoh Installer for Windows         ==
echo ======================================================
echo.

:: 2. Check for Chocolatey Package Manager
echo Checking for Chocolatey...
where choco >nul 2>&1
if %errorlevel% neq 0 (
    echo Chocolatey not found. Installing Chocolatey...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Chocolatey. Please install it manually.
        pause
        exit /b
    )
    echo Chocolatey installed successfully.
) else (
    echo Chocolatey is already installed.
)
echo.

:: 3. Install Python using Chocolatey
echo Checking for Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing Python 3...
    choco install python -y
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Python. Please install it manually.
        pause
        exit /b
    )
    echo Python installed successfully.
) else (
    echo Python is already installed.
)
echo.

:: 4. Install Python dependencies using pip from requirements.txt
echo Installing required Python packages from requirements.txt...
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found in the current directory.
    pause
    exit /b
)
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install one or more Python packages.
    echo Please check the output above for errors.
    pause
    exit /b
)
echo.

echo ======================================================
echo ==         Installation Complete!                   ==
echo ======================================================
echo You can now run the application by executing:
echo python main.py
echo.
pause
