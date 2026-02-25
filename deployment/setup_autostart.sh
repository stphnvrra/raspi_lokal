#!/bin/bash
# Setup script for LoKal desktop launcher and autostart
# Run as: sudo ./deployment/setup_autostart.sh

echo "-------------------------------------------------"
echo "  LoKal Launcher Setup"
echo "-------------------------------------------------"

# 1. Configuration
PROJECT_DIR="/home/lokal/Desktop/loKal"
DESKTOP_DIR="/home/lokal/Desktop"
DESKTOP_FILE="$DESKTOP_DIR/LoKal.desktop"
ICON_PATH="$PROJECT_DIR/static/img/logo.png"
START_SCRIPT="$PROJECT_DIR/start_lokal.sh"

# 2. Make start script executable
if [ -f "$START_SCRIPT" ]; then
    chmod +x "$START_SCRIPT"
    echo "✓ Made start_lokal.sh executable"
else
    echo "⚠ start_lokal.sh not found at $START_SCRIPT"
fi

# 3. Create Desktop file
if [ -d "$DESKTOP_DIR" ]; then
    echo "Creating Desktop shortcut..."
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=LoKal
Comment=Start LoKal Educational AI
Exec=$START_SCRIPT
Icon=$ICON_PATH
Terminal=true
Type=Application
Categories=Education;Development;
EOF
    
    # Set permissions
    chmod +x "$DESKTOP_FILE"
    
    # Mark as trusted (Required for Raspberry Pi OS Bookworm/LXDE)
    if command -v gio >/dev/null 2>&1; then
        echo "Marking desktop file as trusted..."
        gio set "$DESKTOP_FILE" metadata::trusted true || true
    fi
    
    # Optional: Also copy to Applications menu
    mkdir -p /home/lokal/.local/share/applications/
    cp "$DESKTOP_FILE" /home/lokal/.local/share/applications/
    
    echo "✓ LoKal shortcut created on Desktop and Menu"
else
    echo "⚠ Desktop directory not found. Shortcut skipped."
fi

echo "-------------------------------------------------"
echo "  Setup Complete!"
echo "-------------------------------------------------"
echo "  You can now double-click the 'LoKal' icon"
echo "  on your desktop to start the entire system."
echo "-------------------------------------------------"
