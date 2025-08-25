#!/bin/bash

echo "Building Dialogue Venture Game Engine..."
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Using Python: $($PYTHON_CMD --version)"

# Check if PyInstaller is installed
if ! $PYTHON_CMD -c "import PyInstaller" &> /dev/null; then
    echo "Installing PyInstaller..."
    $PYTHON_CMD -m pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build the executable
echo "Building executable..."
$PYTHON_CMD -m PyInstaller build_config.spec

# Check if build was successful
if [ -f "dist/DialogueVenture" ] || [ -f "dist/DialogueVenture.exe" ]; then
    echo ""
    echo "========================================"
    echo "BUILD SUCCESSFUL!"
    echo "========================================"
    if [ -f "dist/DialogueVenture.exe" ]; then
        echo "Executable created: dist/DialogueVenture.exe"
        echo "File size: $(wc -c < dist/DialogueVenture.exe) bytes"
    else
        echo "Executable created: dist/DialogueVenture"
        echo "File size: $(wc -c < dist/DialogueVenture) bytes"
    fi
    echo ""
    echo "You can now run the executable from the dist/ directory"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "BUILD FAILED!"
    echo "========================================"
    echo "Check the output above for errors."
    exit 1
fi