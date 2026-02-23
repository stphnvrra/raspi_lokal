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
log_info "Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
log_info "Starting Ollama service..."
sudo systemctl enable ollama || true
sudo systemctl start ollama || true
sleep 5

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

# Make start script executable
chmod +x start_lokal.sh

log_info "============================================"
log_info "Installation complete!"
log_info "============================================"
log_info ""
log_info "Installation directory: $INSTALL_DIR"
log_info ""
log_info "Next steps:"
log_info "1. Start the service: sudo systemctl start lokal"
log_info "2. Check status: sudo systemctl status lokal"
log_info "3. Or run directly: ./start_lokal.sh"
log_info ""
log_info "Test the API:"
log_info "  curl http://localhost:8000/api/health/"
log_info ""
