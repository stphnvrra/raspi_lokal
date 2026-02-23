# LoKal Deployment Guide for Raspberry Pi 4B

Complete step-by-step instructions for deploying the LoKal educational AI system to a Raspberry Pi 4B (4GB RAM).

---

## 📋 Pre-Deployment Checklist

Before starting, ensure you have:

- ✅ **Hardware**: Raspberry Pi 4B (4GB RAM minimum)
- ✅ **Operating System**: Raspberry Pi OS (64-bit recommended)
- ✅ **Network**: Internet connection for initial setup
- ✅ **Storage**: 16GB+ microSD card (32GB recommended)
- ✅ **Access**: SSH access or direct keyboard/monitor connection
- ✅ **Files**: This entire project folder

---

## 🔧 Hardware Requirements

| Component | Requirement |
|-----------|-------------|
| **Device** | Raspberry Pi 4B |
| **RAM** | 4GB minimum |
| **Storage** | 16GB+ microSD (32GB recommended for logs/audio) |
| **Python** | 3.9+ (included in Raspberry Pi OS) |
| **Network** | Required for initial setup only |

---

## 🚀 Deployment Steps

### Step 1: Prepare Your Raspberry Pi

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Verify Python version (should be 3.9+)
python3 --version
```

### Step 2: Transfer Project Files

**Option A - Using SCP (from your development machine):**
```bash
# From your development machine
cd "/Users/stephen/Documents/[00] School Works/4th Year/2nd Sem/It major 4"
scp -r "raspi LoKAl" pi@raspberrypi.local:/home/pi/lokal
```

**Option B - Using USB Drive:**
1. Copy the entire project folder to a USB drive
2. Insert USB into Raspberry Pi
3. Copy to `/home/pi/lokal`

**Option C - Using Git (if using version control):**
```bash
# On Raspberry Pi
cd /home/pi
git clone <your-repository-url> lokal
cd lokal
```

### Step 3: Run Automated Installation

```bash
# Navigate to project directory
cd /home/pi/lokal

# Make installation script executable
chmod +x deployment/install.sh

# Run the installer (this will take 15-30 minutes)
./deployment/install.sh
```

The installation script will automatically:
- Install system dependencies (Python, espeak, audio libraries)
- Create Python virtual environment
- Install Python packages
- Configure environment variables
- Run database migrations
- Install Ollama and download Qwen 2.5 0.5B model (~400MB)
- Download Vosk speech recognition model
- Set up systemd service for auto-start

### Step 4: Configure Environment Variables

```bash
# The installer creates .env from .env.example
# Edit if you need custom settings
nano /home/pi/lokal/.env
```

**Key settings to review:**
- `DJANGO_ALLOWED_HOSTS`: Add your Pi's IP address if needed
- `OLLAMA_MODEL`: Defaults to `qwen2.5:0.5b` (recommended)
- `TTS_RATE`: Speech speed (150 is default)

### Step 5: Start the Service

```bash
# Start the LoKal service
sudo systemctl start lokal

# Enable auto-start on boot
sudo systemctl enable lokal

# Check service status
sudo systemctl status lokal
```

You should see: `Active: active (running)`

### Step 6: Verify Installation

#### Test 1: Health Check
```bash
curl http://localhost:8000/api/health/
```

Expected output:
```json
{"status": "healthy", "ollama": "connected"}
```

#### Test 2: Ask a Question
```bash
curl -X POST http://localhost:8000/api/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is 2 plus 2?"}'
```

You should receive a JSON response with an AI-generated answer.

#### Test 3: Check Ollama Models
```bash
ollama list
```

You should see `qwen2.5:0.5b` in the list.

---

## 🌐 Accessing the Web Interface

### From the Raspberry Pi itself:
```
http://localhost:8000
```

### From another device on the same network:
```
http://<raspberry-pi-ip>:8000
```

**Find your Pi's IP address:**
```bash
hostname -I
```

---

## 🔍 Troubleshooting

### Service won't start

**Check logs:**
```bash
sudo journalctl -u lokal -f
```

**Common issues:**
- Ollama not running: `sudo systemctl start ollama`
- Port already in use: Check if another service is using port 8000
- Permission errors: Ensure files are owned by `pi` user

### Ollama connection fails

```bash
# Start Ollama service
sudo systemctl start ollama

# Check Ollama status
curl http://localhost:11434/api/tags

# If Ollama isn't installed:
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen2.5:0.5b
```

### Model not found

```bash
# Pull the model manually
ollama pull qwen2.5:0.5b

# Verify it's downloaded
ollama list
```

### Voice/TTS not working

```bash
# Install audio dependencies
sudo apt install espeak libespeak-dev portaudio19-dev -y

# Test TTS
espeak "Hello, this is a test"
```

### Database errors

```bash
cd /home/pi/lokal
source venv/bin/activate
python manage.py migrate
```

---

## 📊 Monitoring & Maintenance

### View Logs
```bash
# Application logs
tail -f /home/pi/lokal/logs/lokal.log

# Gunicorn logs
tail -f /home/pi/lokal/logs/gunicorn.log

# System service logs
sudo journalctl -u lokal -f
```

### Restart Service
```bash
sudo systemctl restart lokal
```

### Stop Service
```bash
sudo systemctl stop lokal
```

### Update Application
```bash
# Stop service
sudo systemctl stop lokal

# Pull latest changes (if using git)
cd /home/pi/lokal
git pull

# Or copy updated files via SCP

# Install any new dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart service
sudo systemctl start lokal
```

---

## 🔒 Security Recommendations

For production deployment:

1. **Change Secret Key**: Generate a new `DJANGO_SECRET_KEY` in `.env`
   ```bash
   python -c 'import secrets; print(secrets.token_urlsafe(50))'
   ```

2. **Disable Debug Mode**: Set `DJANGO_DEBUG=False` in `.env`

3. **Configure Firewall**:
   ```bash
   sudo ufw allow 8000/tcp
   sudo ufw enable
   ```

4. **Regular Updates**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

5. **Backup Database**:
   ```bash
   cp /home/pi/lokal/db.sqlite3 /home/pi/lokal_backup_$(date +%Y%m%d).sqlite3
   ```

---

## 📈 Performance Tips for 4GB RAM

The system is optimized for Raspberry Pi 4B (4GB RAM):

- **Gunicorn**: 2 workers, 2 threads per worker
- **Ollama**: Context window limited to 2048 tokens
- **Model**: Qwen 2.5 0.5B (~400MB) recommended
- **Batch size**: Limited to 256 for memory efficiency

**Monitor RAM usage:**
```bash
free -h
htop
```

If experiencing memory pressure:
- Reduce Gunicorn workers in `deployment/gunicorn.conf.py`
- Switch to smaller model: `qwen2.5:0.5b` (~400MB)
- Disable TTS if not needed

---

## 🆘 Getting Help

### Check System Status
```bash
# Service status
sudo systemctl status lokal

# Ollama status
sudo systemctl status ollama

# Disk space
df -h

# Memory usage
free -h

# Process list
ps aux | grep -E "(gunicorn|ollama)"
```

### Log Locations
- Application: `/home/pi/lokal/logs/lokal.log`
- Gunicorn: `/home/pi/lokal/logs/gunicorn.log`
- System service: `sudo journalctl -u lokal`

---

## ✅ Post-Deployment Checklist

After deployment, verify:

- [ ] Service is running: `sudo systemctl status lokal`
- [ ] Health endpoint responds: `curl http://localhost:8000/api/health/`
- [ ] Ollama is accessible: `curl http://localhost:11434/api/tags`
- [ ] Model is downloaded: `ollama list` shows `qwen2.5:0.5b`
- [ ] Web interface loads: Open `http://<pi-ip>:8000` in browser
- [ ] Chat functionality works: Ask a test question
- [ ] TTS works (if needed): Test the speak endpoint
- [ ] Service auto-starts on reboot: `sudo reboot` and verify

---

## 🎉 Deployment Complete!

Your LoKal educational AI system is now running on Raspberry Pi 4B. The system will automatically start on boot and is ready to serve students in offline environments.

**Default Access:**
- Web Interface: `http://<raspberry-pi-ip>:8000`
- API Endpoint: `http://<raspberry-pi-ip>:8000/api/`
- Health Check: `http://<raspberry-pi-ip>:8000/api/health/`
