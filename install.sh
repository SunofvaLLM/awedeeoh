#!/bin/bash
# Awedeeoh Project Installer for macOS / Linux
# This script automates the setup process using Homebrew.

echo "======================================================"
echo "==         Awedeeoh Installer for macOS / Linux     =="
echo "======================================================"
echo ""

# 1. Check for Homebrew Package Manager (macOS only)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Checking for Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Please install it first."
        echo "You can install it by running the following command in your terminal:"
        echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        exit 1
    fi
    echo "Homebrew is installed."
    echo ""
fi


# 2. Install Python 3
echo "Checking for Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install python
    else
        # For Debian/Ubuntu based systems
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    fi
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install Python. Please install it manually."
        exit 1
    fi
    echo "Python 3 installed successfully."
else
    echo "Python 3 is already installed."
fi
echo ""

# 3. Install Python dependencies using pip from requirements.txt
echo "Installing required Python packages from requirements.txt..."
if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found in the current directory."
    exit 1
fi

python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install one or more Python packages."
    echo "Please check the output above for errors."
    exit 1
fi
echo ""

echo "======================================================"
echo "==            Installation Complete!                =="
echo "======================================================"
echo "You can now run the application by executing:"
echo "python3 main.py"
echo ""
