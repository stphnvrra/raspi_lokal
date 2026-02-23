#!/bin/bash
# Setup script for LoKal desktop launcher and autostart

echo "Setting up LoKal launcher..."

# Make start script executable
chmod +x /home/lokal/Desktop/loKal/start_lokal.sh
echo "✓ Made start_lokal.sh executable"

# Copy desktop file to user's desktop
if [ -d "/home/lokal/Desktop" ]; then
    cp /home/lokal/Desktop/loKal/LoKal.desktop /home/lokal/Desktop/
    chmod +x /home/lokal/Desktop/LoKal.desktop
    # Mark as trusted (needed for some Raspbian versions)
    gio set /home/lokal/Desktop/LoKal.desktop metadata::trusted true || true
    echo "✓ Added LoKal shortcut to Desktop"
else
    echo "⚠ Desktop directory not found, skipping desktop shortcut"
fi

# Copy to applications directory for launcher menu
mkdir -p /home/lokal/.local/share/applications
cp /home/lokal/Desktop/loKal/LoKal.desktop /home/lokal/.local/share/applications/
chmod +x /home/lokal/.local/share/applications/LoKal.desktop
echo "✓ Added LoKal to application menu"

# Optional: Setup autostart (commented out by default)
# Uncomment the lines below if you want LoKal to start automatically on boot
# echo ""
# echo "Setting up autostart..."
# mkdir -p /home/lokal/.config/autostart
# cp /home/lokal/Desktop/loKal/LoKal.desktop /home/lokal/.config/autostart/
# echo "✓ LoKal will start automatically on login"

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo "You can now:"
echo "1. Double-click 'LoKal' icon on Desktop"
echo "2. Find 'LoKal' in application menu"
echo "3. Run: /home/lokal/Desktop/loKal/start_lokal.sh"
echo ""
echo "To enable autostart on boot, edit this script"
echo "and uncomment the autostart section, then run again."
echo "=========================================="
