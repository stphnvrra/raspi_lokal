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
    USE_HTTPS=true # Assume systemd is configured for HTTPS or we'll check the URL anyway
else
    echo "Starting LoKal server manually..."
    # Generate private key and self-signed certificate in one command
    # Valid for 365 days
    openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes -subj "/C=PH/ST=MetroManila/L=Manila/O=LoKal/OU=Education/CN=192.168.4.1" 2>/dev/null || true
    
    # Check for SSL certificates
    if [ -f "certs/cert.pem" ] && [ -f "certs/key.pem" ]; then
        echo "SSL certificates found. Starting in HTTPS mode..."
        python manage.py runsslserver --certificate certs/cert.pem --key certs/key.pem 0.0.0.0:8000 &
        USE_HTTPS=true
    else
        echo "SSL certificates not found. Starting in HTTP mode..."
        python manage.py runserver 0.0.0.0:8000 &
        USE_HTTPS=false
    fi
    SERVER_PID=$!
    # Wait for server to start
    echo "Waiting for server to start..."
    sleep 5
fi

# Open the browser automatically
echo "Opening browser..."
if [ "$USE_HTTPS" = true ]; then
    URL="https://localhost:8000"
else
    URL="http://localhost:8000"
fi

echo "Navigating to $URL"

# Common browser flags for development/Pi
BROWSER_FLAGS="--kiosk --ignore-certificate-errors"

if command -v chromium-browser &> /dev/null; then
    chromium-browser $BROWSER_FLAGS "$URL" &
elif command -v chromium &> /dev/null; then
    chromium $BROWSER_FLAGS "$URL" &
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
