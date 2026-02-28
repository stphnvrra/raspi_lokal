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

# URLs
URL="http://${LOKAL_IP}:8000"
LOCAL_URL="http://127.0.0.1:8000"
CHECK_URL="http://127.0.0.1:8000"

# ── Start the server ──
if systemctl is-active --quiet lokal; then
    echo "LoKal systemd service detected. Restarting to pick up latest config..."
    sudo systemctl restart lokal
    sleep 3
else
    echo "Starting LoKal server manually..."
    python manage.py runserver 0.0.0.0:8000 &
    SERVER_PID=$!
fi

# ── Wait for the server to actually respond ──
echo "Waiting for server to be ready at $CHECK_URL ..."
MAX_WAIT=30
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -sk --connect-timeout 2 "$CHECK_URL" >/dev/null 2>&1; then
        echo "✓ Server is ready!"
        break
    fi
    sleep 2
    WAITED=$((WAITED + 2))
    echo "  Still waiting... (${WAITED}s / ${MAX_WAIT}s)"
done

# If systemd failed, fall back to manual server
if [ $WAITED -ge $MAX_WAIT ]; then
    echo "⚠ Server not responding. Stopping systemd and starting manually..."
    sudo systemctl stop lokal 2>/dev/null || true
    python manage.py runserver 0.0.0.0:8000 &
    SERVER_PID=$!
    sleep 5
    if curl -sk --connect-timeout 2 "$CHECK_URL" >/dev/null 2>&1; then
        echo "✓ Server is ready (manual mode)!"
    else
        echo "⚠ Server still not responding. Opening browser anyway..."
    fi
fi

# ── Open Chromium browser ──
echo "Opening browser to $LOCAL_URL ..."
BROWSER_FLAGS="--kiosk --ignore-certificate-errors --no-first-run --disable-translate"

if command -v chromium-browser &> /dev/null; then
    chromium-browser $BROWSER_FLAGS "$LOCAL_URL" &
elif command -v chromium &> /dev/null; then
    chromium $BROWSER_FLAGS "$LOCAL_URL" &
else
    echo "⚠ Chromium not found. Please open $LOCAL_URL manually."
fi

echo ""
echo "======================================"
echo "  LoKal is running!"
echo "======================================"
echo "  Local URL (this Pi): $LOCAL_URL"
echo "  Hotspot URL (others): $URL"
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
