#!/bin/bash
# LoKal Backend Installation Script for Raspberry Pi 4B
# Run this script from the project directory on your Raspberry Pi

set -e

echo "============================================"
echo "LoKal Backend Installation Script"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# If script is in deployment folder, the project root is one level up
if [[ "$SCRIPT_DIR" == */deployment ]]; then
    SOURCE_DIR="$(dirname "$SCRIPT_DIR")"
else
    SOURCE_DIR="$SCRIPT_DIR"
fi

# Target installation directory
INSTALL_DIR="/home/lokal/Desktop/loKal"

PYTHON_VERSION="python3"

log_info "Source directory: $SOURCE_DIR"
log_info "Installation directory: $INSTALL_DIR"
log_info "Current user: $USER"

# Update system
log_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
log_info "Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    espeak \
    libespeak-dev \
    portaudio19-dev \
    libffi-dev \
    libssl-dev \
    build-essential \
    wget \
    unzip \
    curl

# Copy project files to installation directory if needed
if [ "$SOURCE_DIR" != "$INSTALL_DIR" ]; then
    log_info "Copying project files to $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR"
    # Copy all files except venv and __pycache__
    rsync -av --exclude='venv' --exclude='__pycache__' --exclude='.git' "$SOURCE_DIR/" "$INSTALL_DIR/"
fi

# Navigate to installation directory
cd "$INSTALL_DIR"

# Create virtual environment
log_info "Creating Python virtual environment..."
$PYTHON_VERSION -m venv venv
source venv/bin/activate

# Upgrade pip
log_info "Upgrading pip (with retries)..."
pip install --upgrade --default-timeout=100 --retries 10 --no-cache-dir pip wheel setuptools

# Install Python dependencies
log_info "Installing Python dependencies (with retries)..."
pip install --default-timeout=100 --retries 10 --no-cache-dir -r requirements.txt

# Create logs directory
mkdir -p logs

# Create models directory
mkdir -p models

# Create media directory
mkdir -p media

# Setup environment file
if [ ! -f .env ]; then
    log_info "Creating .env file from template..."
    if [ -f deployment/.env.example ]; then
        cp deployment/.env.example .env
    else
        # Create .env manually if template doesn't exist
        cat > .env << EOF
# LoKal Backend Environment Configuration

# Django Settings
DJANGO_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,raspberrypi.local,0.0.0.0

# Ollama Settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:0.5b
OLLAMA_TIMEOUT=120

# Text-to-Speech Settings
TTS_RATE=150
TTS_VOLUME=1.0

# Vosk Speech-to-Text Model Path
VOSK_MODEL_PATH=$INSTALL_DIR/models/vosk-model-small-en-us-0.15
EOF
    fi
    log_warn "Created .env file - edit if needed: $INSTALL_DIR/.env"
else
    log_info ".env file already exists, skipping..."
fi

# Update VOSK_MODEL_PATH in .env to use correct path
sed -i "s|VOSK_MODEL_PATH=.*|VOSK_MODEL_PATH=$INSTALL_DIR/models/vosk-model-small-en-us-0.15|" .env

# Run database migrations
log_info "Running database migrations..."
python manage.py migrate

# Collect static files
log_info "Collecting static files..."
python manage.py collectstatic --noinput || true

# Install Ollama
if ! command -v ollama &> /dev/null; then
    log_info "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    log_info "Ollama is already installed, skipping..."
fi

# Start Ollama service
log_info "Starting Ollama service..."
sudo systemctl enable ollama || true
sudo systemctl start ollama || true
sleep 5

# Check if model exists
log_info "Checking for Qwen 2.5 0.5B model..."
if ollama list | grep -q "qwen2.5:0.5b"; then
    log_info "Model qwen2.5:0.5b already exists, skipping pull..."
else
    # Pull qwen2.5:0.5b (optimized for 4GB RAM stability, with retries)
    log_info "Pulling Qwen 2.5 0.5B model (this may take a while, with retries)..."
    MAX_RETRIES=5
    RETRY_COUNT=0
    until ollama pull qwen2.5:0.5b || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
        RETRY_COUNT=$((RETRY_COUNT + 1))
        log_warn "Ollama pull failed. Retrying ($RETRY_COUNT/$MAX_RETRIES)..."
        sleep 5
    done

    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        log_error "Failed to pull Ollama model after $MAX_RETRIES attempts. Please check your internet connection."
        exit 1
    fi
fi

# Download Vosk model
log_info "Downloading Vosk speech recognition model..."
cd models
if [ ! -d "vosk-model-small-en-us-0.15" ]; then
    log_info "Downloading Vosk model (resume enabled)..."
    wget -q --show-progress --continue --tries=10 https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip -q vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip
else
    log_info "Vosk model already exists, skipping..."
fi
cd "$INSTALL_DIR"

# Generate SSL certificates for HTTPS (required for microphone access on client devices)
log_info "Generating SSL certificates..."
mkdir -p "$INSTALL_DIR/certs"
if [ ! -f "$INSTALL_DIR/certs/cert.pem" ] || [ ! -f "$INSTALL_DIR/certs/key.pem" ]; then
    openssl req -x509 -newkey rsa:2048 \
        -keyout "$INSTALL_DIR/certs/key.pem" \
        -out "$INSTALL_DIR/certs/cert.pem" \
        -days 365 -nodes \
        -subj "/C=PH/ST=MetroManila/L=Manila/O=LoKal/OU=Education/CN=192.168.4.1" 2>/dev/null
    log_info "SSL certificates generated."
else
    log_info "SSL certificates already exist, skipping..."
fi

# Setup systemd service (update paths for current user)
log_info "Setting up systemd service..."
cat > /tmp/lokal.service << EOF
[Unit]
Description=LoKal Educational AI Backend
After=network.target ollama.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$INSTALL_DIR/venv/bin/gunicorn --config $INSTALL_DIR/deployment/gunicorn.conf.py lokal_backend.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo cp /tmp/lokal.service /etc/systemd/system/lokal.service
sudo systemctl daemon-reload
sudo systemctl enable lokal

# Setup Wi-Fi Hotspot (Standalone mode)
log_info "Setting up Wi-Fi Hotspot..."
sudo bash "$INSTALL_DIR/deployment/setup_hotspot.sh" || log_warn "Hotspot setup failed, skipping..."

# Setup Desktop Launcher and Autostart
log_info "Setting up Desktop Launcher and Autostart..."
sudo bash "$INSTALL_DIR/deployment/setup_autostart.sh" || log_warn "Autostart setup failed, skipping..."

# Final Summary
log_info "============================================"
log_info "     Installation & Setup Complete!"
log_info "============================================"
log_info ""
log_info "Project Directory: $INSTALL_DIR"
log_info "IP Address:        192.168.4.1"
log_info "Hotspot SSID:      LoKal-AI-Hotspot"
log_info ""
log_info "Access the application:"
log_info "1. Connect your device to the 'LoKal-AI-Hotspot' Wi-Fi."
log_info "2. Open your browser and go to:"
log_info "   https://192.168.4.1:8000"
log_info ""
log_info "On the Raspberry Pi Desktop:"
log_info "- Double-click the 'LoKal' icon to start."
log_info "- The system is also set to start on boot."
log_info ""
log_info "============================================"
