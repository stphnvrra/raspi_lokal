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

# Start server if systemd is not handling it
if systemctl is-active --quiet lokal; then
    echo "LoKal service is already running via systemd."
else
    echo "Starting LoKal server manually..."
    python manage.py runserver 0.0.0.0:8000 &
    SERVER_PID=$!
fi

# URL is always HTTP
URL="http://${LOKAL_IP}:8000"

# ── Wait for the server to actually respond ──
CHECK_URL="http://127.0.0.1:8000"
echo "Waiting for server to be ready at $CHECK_URL ..."
MAX_WAIT=60
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    # Use curl to check if the server is responding (ignore SSL errors for self-signed cert)
    if curl -sk --connect-timeout 2 "$CHECK_URL" >/dev/null 2>&1; then
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
