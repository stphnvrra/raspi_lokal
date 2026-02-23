#!/bin/bash
# LoKal Startup Script for Raspberry Pi 4B
# Run this script to start the application

set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Cleanup function to stop background processes
cleanup() {
    echo ""
    echo "Stopping LoKal..."
    if [ ! -z "$SERVER_PID" ]; then kill $SERVER_PID 2>/dev/null; fi
    # We don't necessarily want to kill Ollama as it might be used by other apps,
    # but for a dedicated Pi setup, we'll leave it running or the user can stop it.
    exit
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

echo "======================================"
echo "  Starting LoKal..."
echo "======================================"
echo ""

# 1. Check virtual environment
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment (venv) not found."
    echo "Please run ./install_raspi.sh first."
    exit 1
fi

# 2. Check Vosk model (required for STT)
if [ ! -d "models/vosk-model-small-en-us-0.15" ]; then
    echo "Warning: Vosk STT model not found in models/ directory."
    echo "Speech-to-Text may not work correctly."
fi

# 3. Start Ollama if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 5
else
    echo "Ollama is already running."
fi

# Activate virtual environment
echo "Activating Python environment..."
source venv/bin/activate

# Start the server in the background
echo ""
echo "Starting LoKal server..."
python manage.py runserver 0.0.0.0:8000 &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Open the browser automatically (only if DISPLAY is set)
if [ ! -z "$DISPLAY" ]; then
    echo "Opening browser..."
    if command -v chromium-browser &> /dev/null; then
        chromium-browser --kiosk "http://localhost:8000/" &
    elif command -v chromium &> /dev/null; then
        chromium --kiosk "http://localhost:8000/" &
    else
        echo "Chromium not found. Please open http://localhost:8000/ manually."
    fi
else
    echo "No display detected. Skipping browser auto-open."
fi

echo ""
echo "======================================"
echo "  LoKal is running!"
echo "======================================"
echo "  URL: http://localhost:8000/"
echo "  Press Ctrl+C to stop."
echo "======================================"
echo ""

# Wait for server process
wait $SERVER_PID
