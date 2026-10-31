#!/bin/bash
# Whistle Assistant Launcher for Linux/macOS

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install/update dependencies
echo "Installing/updating dependencies..."
pip install -q -e ".[mic]"

echo
echo "Starting Whistle Assistant..."
echo "Wake words: \"Hey Assistant\", \"Okay Assistant\", \"Whistle\", \"Computer\""
echo "Press Ctrl+C to stop."
echo

python -m whistle_assistant "$@"