#!/bin/bash
# LoKal Startup Script for Raspberry Pi 4B
# Run this script to start the application

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# LoKal Hotspot IP address
LOKAL_IP="192.168.4.1"

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

# Determine protocol and start server if needed
USE_HTTPS=false

if systemctl is-active --quiet lokal; then
    echo "LoKal service is already running via systemd."
    USE_HTTPS=true
else
    echo "Starting LoKal server manually..."

    # Ensure certs directory exists
    mkdir -p certs

    # Generate self-signed certificate if not present
    if [ ! -f "certs/cert.pem" ] || [ ! -f "certs/key.pem" ]; then
        echo "Generating SSL certificates..."
        openssl req -x509 -newkey rsa:2048 -keyout certs/key.pem -out certs/cert.pem \
            -days 365 -nodes \
            -subj "/C=PH/ST=MetroManila/L=Manila/O=LoKal/OU=Education/CN=$LOKAL_IP" 2>/dev/null || true
    fi

    # Start the server
    if [ -f "certs/cert.pem" ] && [ -f "certs/key.pem" ]; then
        echo "Starting in HTTPS mode..."
        python manage.py runsslserver --certificate certs/cert.pem --key certs/key.pem 0.0.0.0:8000 &
        USE_HTTPS=true
    else
        echo "Starting in HTTP mode..."
        python manage.py runserver 0.0.0.0:8000 &
        USE_HTTPS=false
    fi
    SERVER_PID=$!
fi

# Build the URL using the actual RPi IP
if [ "$USE_HTTPS" = true ]; then
    URL="https://${LOKAL_IP}:8000"
else
    URL="http://${LOKAL_IP}:8000"
fi

# ── Wait for the server to actually respond ──
echo "Waiting for server to be ready at $URL ..."
MAX_WAIT=60
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    # Use curl to check if the server is responding (ignore SSL errors for self-signed cert)
    if curl -sk --connect-timeout 2 "$URL" >/dev/null 2>&1; then
        echo "✓ Server is ready!"
        break
    fi
    sleep 2
    WAITED=$((WAITED + 2))
    echo "  Still waiting... (${WAITED}s / ${MAX_WAIT}s)"
done

if [ $WAITED -ge $MAX_WAIT ]; then
    echo "⚠ Server did not respond within ${MAX_WAIT}s. Opening browser anyway..."
fi

# ── Open Chromium browser ──
echo "Opening browser to $URL ..."
BROWSER_FLAGS="--kiosk --ignore-certificate-errors --no-first-run --disable-translate"

if command -v chromium-browser &> /dev/null; then
    chromium-browser $BROWSER_FLAGS "$URL" &
elif command -v chromium &> /dev/null; then
    chromium $BROWSER_FLAGS "$URL" &
else
    echo "⚠ Chromium not found. Please open $URL manually."
fi

echo ""
echo "======================================"
echo "  LoKal is running!"
echo "======================================"
echo "  URL: $URL"
echo "  Press Ctrl+C to stop."
echo "======================================"
echo ""

# Keep script alive so the terminal (and browser) stay open
if [ ! -z "$SERVER_PID" ]; then
    # We started the server ourselves — wait for it
    wait $SERVER_PID
else
    # Systemd is managing the server — just keep the terminal open
    echo "Press Enter to close this window..."
    read -r
fi
