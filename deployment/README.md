# Deployment Configuration for Raspberry Pi 4B

This directory contains files for deploying LoKal backend on a Raspberry Pi 4B.

## Quick Deployment

1. Copy the entire project to your Raspberry Pi
2. Create virtual environment and install dependencies
3. Copy `.env.example` to `.env` and configure
4. Run migrations
5. Set up systemd service

```bash
# On Raspberry Pi
cd /home/pi/lokal
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp deployment/.env.example .env
# Edit .env with your settings

python manage.py migrate
python manage.py collectstatic --noinput

# Install systemd service
sudo cp deployment/lokal.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lokal
sudo systemctl start lokal
```

## Setting up Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Llama 3.2 1B (recommended for 4GB RAM)
ollama pull llama3.2:1b

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama
```

## Setting up Vosk (Speech-to-Text)

```bash
# Download small English model
mkdir -p ~/lokal/models
cd ~/lokal/models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

## Verifying Installation

```bash
# Check service status
sudo systemctl status lokal

# Test health endpoint
curl http://localhost:8000/api/health/

# Check logs
sudo journalctl -u lokal -f
```
