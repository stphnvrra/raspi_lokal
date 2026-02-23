# LoKal Backend - Django Project for Raspberry Pi 4B

A production-ready Django backend for LoKal, an offline educational AI device.

## Requirements

- Python 3.9+
- Raspberry Pi 4B (4GB RAM)
- Ollama (for local AI)

## Quick Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver 0.0.0.0:8000
```

## Production Deployment

See `deployment/README.md` for production setup with Gunicorn and systemd.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ask/` | Submit text question |
| POST | `/api/ask/voice/` | Submit voice audio |
| POST | `/api/tts/` | Text to speech |
| GET | `/api/conversations/` | List conversations |
| GET | `/api/health/` | Health check |

## Ollama Setup

Install Ollama on Raspberry Pi and pull the recommended model:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Llama 3.2 1B (recommended for 4GB RAM)
ollama pull llama3.2:1b
```
