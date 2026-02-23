#!/bin/bash
# Setup script for LoKal desktop launcher and autostart

echo "Setting up LoKal launcher..."

# Make start script executable
chmod +x /home/pi/lokal/start_lokal.sh
echo "✓ Made start_lokal.sh executable"

# Copy desktop file to user's desktop
if [ -d "/home/pi/Desktop" ]; then
    cp /home/pi/lokal/LoKal.desktop /home/pi/Desktop/
    chmod +x /home/pi/Desktop/LoKal.desktop
    echo "✓ Added LoKal shortcut to Desktop"
else
    echo "⚠ Desktop directory not found, skipping desktop shortcut"
fi

# Copy to applications directory for launcher menu
mkdir -p /home/pi/.local/share/applications
cp /home/pi/lokal/LoKal.desktop /home/pi/.local/share/applications/
chmod +x /home/pi/.local/share/applications/LoKal.desktop
echo "✓ Added LoKal to application menu"

# Optional: Setup autostart (commented out by default)
# Uncomment the lines below if you want LoKal to start automatically on boot
# echo ""
# echo "Setting up autostart..."
# mkdir -p /home/pi/.config/autostart
# cp /home/pi/lokal/LoKal.desktop /home/pi/.config/autostart/
# echo "✓ LoKal will start automatically on login"

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo "You can now:"
echo "1. Double-click 'LoKal Educational AI' icon on Desktop"
echo "2. Find 'LoKal Educational AI' in application menu"
echo "3. Run: /home/pi/lokal/start_lokal.sh"
echo ""
echo "To enable autostart on boot, edit this script"
echo "and uncomment the autostart section, then run again."
echo "=========================================="
