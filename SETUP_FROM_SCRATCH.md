# 🚀 LoKal: Zero-to-Hero Setup Guide (Raspberry Pi 4B)

Follow these steps to set up the LoKal educational AI system from scratch in an offline environment.

---

## 📦 Phase 1: Hardware & OS Preparation

1. **Get a Raspberry Pi 4B** (4GB RAM recommended).
2. **Flash Raspberry Pi OS (64-bit)** onto a 16GB+ microSD card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
3. **Finish First Boot**: Connect a monitor/keyboard or use SSH to set up your username (e.g., `pi`) and password.

---

## 📂 Phase 2: Transfer Project Files

1. **Connect the Pi to your computer** (via Wi-Fi or Ethernet).
2. **Transfer the folder**:
   - **Option A (SCP)**: Run this from your computer:
     ```bash
     scp -r "/path/to/lokal_v3" pi@raspberrypi.local:/home/lokal/Desktop/loKal
     ```
   - **Option B (USB)**: Copy the folder to a USB drive and paste it into `/home/lokal/Desktop/loKal` on the Pi.

---

## 🛠️ Phase 3: Automated Installation

On the Raspberry Pi, open a terminal and run:

```bash
cd /home/lokal/Desktop/loKal

# 1. Make the installer executable
chmod +x deployment/install.sh

# 2. Run the installer (takes ~20 mins)
./deployment/install.sh
```

**This script will automatically:**
- Install Python, FFmpeg, and audio libraries.
- Install **Ollama** and the **AI Model** (Qwen 2.5 0.5B).
- Download the **Speech Recognition** model (Vosk).
- Set up the database and static files.

---

---

## 🌐 Phase 4: Networking (Choose ONE Option)

### Option A: Wi-Fi Hotspot Mode (Recommended/Standalone)
This turns your Pi into its own Wi-Fi router. Devices connect directly to it.
```bash
# On the Raspberry Pi
chmod +x deployment/setup_hotspot.sh
sudo ./deployment/setup_hotspot.sh
```
*   **Result**: Pi broadcasts `LoKal-AI-Hotspot`.
*   **Connection**: Join the Wi-Fi using password `lokal1234`.
*   **Browse**: Go to `http://raspilokal.com` (no extra setup needed!).

### Option B: Existing Router Mode (Advanced)
Use this if you want the Pi to stay connected to your current Wi-Fi router.
1. **Set Static IP**:
   ```bash
   chmod +x deployment/setup_static_ip.sh
   sudo ./deployment/setup_static_ip.sh
   ```
2. **Setup DNS Proxy**:
   ```bash
   chmod +x deployment/setup_dns_proxy.sh
   sudo ./deployment/setup_dns_proxy.sh
   ```
3. **Configure Devices**:
   - Join your router's Wi-Fi.
   - Set your phone's **DNS** to **Manual** and enter the **Pi's IP address**.
   - Browse: `http://raspilokal.com`

---

## 🔄 Phase 6: Auto-Start on Boot

To make the system start automatically when the Pi turns on:

```bash
# On the Raspberry Pi
chmod +x deployment/setup_autostart.sh
sudo ./deployment/setup_autostart.sh
```

---

## 🖱️ Phase 7: One-Click Startup (Desktop Icon)

Once setup is complete, you don't need to use the terminal anymore!

1. **Find the Icon**: Look for the **LoKal** icon on your Raspberry Pi desktop.
2. **Double-Click**: It will automatically:
   - Start the **Ollama** AI service.
   - Start the **LoKal Backend** (Django).
   - Open **Chromium** in full-screen (kiosk) mode at `http://raspilokal.com`.

---

## ✅ Final Check
Run `sudo systemctl status lokal` to ensure everything is running perfectly!
