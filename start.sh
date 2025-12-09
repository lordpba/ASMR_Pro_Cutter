#!/bin/bash
set -e

# Name of the virtual environment directory
VENV_DIR=".venv"

# Check if the virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Virtual environment found."
fi

# Activate the virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install/Update dependencies
echo "📦 Installing/Updating dependencies..."
# We use -e (editable) so you can modify the code and see changes immediately
pip install -e .

# Start the application
echo "🚀 Starting ASMR Pro Cutter..."
python gui.py
