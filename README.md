# 🤖 LoKal: Offline Educational AI for Remote Learning

LoKal is a production-ready, standalone educational AI system designed specifically for **Raspberry Pi 4B**. It provides students in remote areas with access to an intelligent assistant (Math, Science, English) without requiring an internet connection.

![LoKal Logo](static/img/logo.png)

---

## 🌟 Key Features

*   **Offline First**: Runs completely offline using **Ollama** and **Qwen 2.5 0.5B** AI models.
*   **Voice Interactive**: Includes **Speech-to-Text (Vosk)** and **Text-to-Speech (pyttsx3)**.
*   **Standalone Hotspot**: Automatically turns the Raspberry Pi into a Wi-Fi Access Point.
*   **Secure Access**: Implements **HTTPS** to ensure microphone access works on all mobile devices.
*   **Responsive UI**: Optimized for 7-inch Raspberry Pi displays (800x480) and mobile phones.
*   **One-Click Startup**: Includes a desktop launcher and auto-start on boot functionality.

---

## 🛠️ Hardware Requirements

*   **Device**: Raspberry Pi 4B (4GB or 8GB RAM recommended).
*   **Storage**: 16GB+ MicroSD Card (Class 10).
*   **Display**: Raspberry Pi Touch Display (Optional) or any HDMI monitor.
*   **Microphone**: USB Microphone for voice interaction.

---

## 🚀 One-Command Installation (Zero-to-Hero)

The installation process is now fully automated. On a fresh Raspberry Pi OS (64-bit), run:

```bash
# 1. Clone or copy this folder to Desktop
cd /home/lokal/Desktop/loKal

# 2. Run the unified installer
sudo ./deployment/install.sh
```

**What this does:**
1.  Installs all system dependencies (Python, FFmpeg, etc.).
2.  Sets up the AI environment (Ollama + Models).
3.  Configures the **Wi-Fi Hotspot** (`LoKal-AI-Hotspot`).
4.  Creates the **Desktop Icon**.
5.  Generates **SSL Certificates** for secure access.

---

## 📱 How to Connect & Use

### From the Raspberry Pi:
- Simply double-click the **LoKal** icon on the desktop.
- It will automatically start the services and open the browser.

### From a Mobile Phone/Tablet:
1.  **Join Wi-Fi**: Connect to `LoKal-AI-Hotspot` (Password: `lokal1234`).
2.  **Browse**: Open your browser and go to:
    > **https://192.168.4.1:8000**
3.  **Security Note**: Since we use self-signed certificates, click **"Advanced"** and **"Proceed Anyway"** to enable the microphone.

---

## 📁 Project Structure

```text
loKal/
├── api/                # Django REST API (AI, TTS, STT logic)
├── deployment/         # Installation and networking scripts
├── lokal_backend/      # Core Django settings
├── static/             # CSS, JS, and Images
├── templates/          # HTML Templates (Responsive)
├── models/             # Vosk Speech models
├── certs/              # SSL Certificates
├── lokal.sqlite3       # Database (Tracked)
└── start_lokal.sh      # Main startup script
```

---

## 🎓 About the Project
This project was developed as part of **IT Major 4** requirements for the **4th Year, 2nd Semester**. It aims to bridge the digital divide by providing intelligent educational tools to the most remote communities.

---

## 📜 License
This project is intended for educational purposes.
