#!/bin/bash
# LoKal Startup Script for Raspberry Pi 4B
# Run this script to start the application

set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "======================================"
echo "  Starting LoKal..."
echo "======================================"
echo ""

# Start Ollama if not running
if ! systemctl is-active --quiet ollama; then
    echo "Starting Ollama service..."
    sudo systemctl start ollama
else
    echo "Ollama is already running."
fi

# Start Hotspot if not running
echo "Checking Wi-Fi Hotspot..."
if ! nmcli con show --active | grep -q "LoKal-Hotspot"; then
    echo "Activating LoKal Wi-Fi Hotspot..."
    sudo nmcli con up "LoKal-Hotspot" || echo "⚠ Failed to start hotspot. Is it configured?"
else
    echo "Wi-Fi Hotspot is already active."
fi

# Activate virtual environment
echo "Activating Python environment..."
source venv/bin/activate

# Check if Gunicorn/Systemd service is handled already
if systemctl is-active --quiet lokal; then
    echo "LoKal service is already running via systemd."
else
    echo "Starting LoKal server manually..."
    # Start the server in the background
    python manage.py runserver 0.0.0.0:8000 &
    SERVER_PID=$!
    # Wait for server to start
    echo "Waiting for server to start..."
    sleep 5
fi

# Open the browser automatically
echo "Opening browser..."
URL="http://raspilokal.com"
if ! curl -s --head $URL | head -n 1 | grep "200 OK" > /dev/null; then
    URL="http://localhost:8000"
fi

echo "Navigating to $URL"

if command -v chromium-browser &> /dev/null; then
    chromium-browser --kiosk "$URL" &
elif command -v chromium &> /dev/null; then
    chromium --kiosk "$URL" &
else
    echo "Chromium not found. Please open $URL manually."
fi

echo ""
echo "======================================"
echo "  LoKal is running!"
echo "======================================"
echo "  URL: $URL"
echo "  Press Ctrl+C and close browser to stop."
echo "======================================"
echo ""

# Wait for server process if we started it
if [ ! -z "$SERVER_PID" ]; then
    wait $SERVER_PID
else
    # Keep script alive so the terminal doesn't close immediately if run from desktop
    sleep 10
fi
