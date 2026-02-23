#!/bin/bash
# Setup script for LoKal desktop launcher and autostart
# Run as: sudo ./deployment/setup_autostart.sh

echo "-------------------------------------------------"
echo "  LoKal Launcher Setup"
echo "-------------------------------------------------"

# 1. Make start script executable
if [ -f "/home/lokal/Desktop/loKal/start_lokal.sh" ]; then
    chmod +x /home/lokal/Desktop/loKal/start_lokal.sh
    echo "✓ Made start_lokal.sh executable"
else
    echo "⚠ start_lokal.sh not found at /home/lokal/Desktop/loKal/"
fi

# 2. Copy and Trust Desktop file
if [ -d "/home/lokal/Desktop" ]; then
    echo "Configuring Desktop shortcut..."
    
    # Sanitize the file (remove Windows line endings just in case)
    sed 's/\r$//' /home/lokal/Desktop/loKal/LoKal.desktop > /home/lokal/Desktop/LoKal.desktop
    
    # Set permissions
    chmod +x /home/lokal/Desktop/LoKal.desktop
    
    # Mark as trusted (Required for Raspberry Pi OS Bookworm/LXDE)
    if command -v gio >/dev/null 2>&1; then
        echo "Marking desktop file as trusted..."
        gio set /home/lokal/Desktop/LoKal.desktop metadata::trusted true || true
    fi
    
    # Optional: Also copy to Applications menu
    mkdir -p /home/lokal/.local/share/applications/
    cp /home/lokal/Desktop/LoKal.desktop /home/lokal/.local/share/applications/
    
    echo "✓ LoKal shortcut added to Desktop and Menu"
else
    echo "⚠ Desktop directory not found. Shortcut skipped."
fi

echo "-------------------------------------------------"
echo "  Setup Complete!"
echo "-------------------------------------------------"
echo "  You can now double-click the 'LoKal' icon"
echo "  on your desktop to start the entire system."
echo "-------------------------------------------------"
