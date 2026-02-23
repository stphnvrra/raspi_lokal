#!/bin/bash
# LoKal Installation Script for Raspberry Pi 4B
# Run this script after copying the project to your Raspberry Pi

set -e  # Exit on error

echo "======================================"
echo "  LoKal Installation for Raspberry Pi"
echo "======================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This script is designed for Raspberry Pi."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "[1/7] Updating system packages..."
sudo apt-get update

echo ""
echo "[2/7] Installing system dependencies..."
sudo apt-get install -y python3-pip python3-venv ffmpeg espeak portaudio19-dev wget unzip

echo ""
echo "[3/7] Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed."
fi

echo ""
echo "[4/7] Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo ""
echo "[5/7] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "[6/7] Downloading Ollama model (this may take a few minutes)..."
ollama pull qwen2.5:0.5b

echo ""
echo "[7/7] Downloading Vosk speech recognition model..."
mkdir -p models
cd models
if [ ! -d "vosk-model-small-en-us-0.15" ]; then
    wget -q --show-progress https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip -q vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip
    echo "Vosk model downloaded and extracted."
else
    echo "Vosk model already exists, skipping."
fi
cd "$SCRIPT_DIR"

echo ""
echo "======================================"
echo "  Installation Complete!"
echo "======================================"
echo ""
echo "To start LoKal, run:"
echo "  ./start_lokal.sh"
echo ""
echo "Or manually:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver 0.0.0.0:8000"
echo ""
echo "Then open Chromium and go to: http://localhost:8000/"
