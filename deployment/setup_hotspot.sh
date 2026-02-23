#!/bin/bash
# Script to turn your Raspberry Pi into a standalone Wi-Fi Hotspot (AP Mode)
# Works on Raspberry Pi OS (Bookworm) using NetworkManager (nmcli)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if [ "$EUID" -ne 0 ]; then
  log_error "Please run as root: sudo ./deployment/setup_hotspot.sh"
  exit 1
fi

# Configuration
SSID=${1:-"LoKal-AI-Hotspot"}
PASSWORD=${2:-"lokal1234"}
HOTSPOT_IP="192.168.4.1"

log_info "-------------------------------------------------"
log_info "  LoKal Wi-Fi Hotspot Setup"
log_info "-------------------------------------------------"
log_info "  SSID:     $SSID"
log_info "  Password: $PASSWORD"
log_info "  Pi IP:    $HOTSPOT_IP"
log_info "-------------------------------------------------"

# 1. Install necessary tools
log_info "Installing dnsmasq..."
apt-get update -y && apt-get install -y dnsmasq

# 2. Check for Network Manager (nmcli)
if ! command -v nmcli >/dev/null 2>&1; then
    log_error "NetworkManager (nmcli) not found. This script is intended for Raspberry Pi OS (Bookworm)."
    exit 1
fi

# 3. Create the Hotspot connection
log_info "Creating Hotspot connection using nmcli..."
nmcli con add type wifi ifname wlan0 con-name "LoKal-Hotspot" autoconnect yes ssid "$SSID"
nmcli con modify "LoKal-Hotspot" 802-11-wireless.mode ap 802-11-wireless.band bg
nmcli con modify "LoKal-Hotspot" 802-11-wireless-security.key-mgmt wpa-psk
nmcli con modify "LoKal-Hotspot" 802-11-wireless-security.psk "$PASSWORD"
nmcli con modify "LoKal-Hotspot" ipv4.method manual ipv4.addresses "$HOTSPOT_IP/24"
nmcli con modify "LoKal-Hotspot" ipv6.method ignore

# 4. Configure dnsmasq for DHCP and local DNS
log_info "Configuring dnsmasq for Hotspot..."
cat > /etc/dnsmasq.d/lokal-hotspot.conf << EOF
# DHCP Configuration
interface=wlan0
dhcp-range=192.168.4.10,192.168.4.100,255.255.255.0,24h
dhcp-option=option:router,$HOTSPOT_IP
dhcp-option=option:dns-server,$HOTSPOT_IP

# LoKal Domain Mapping
address=/raspilokal.com/$HOTSPOT_IP
EOF

# 5. Restart services
log_info "Restarting services..."
systemctl restart dnsmasq
nmcli con up "LoKal-Hotspot"

log_info "================================================="
log_info "  Wi-Fi Hotspot Setup Complete!"
log_info "================================================="
log_info "  1. Connect your device to: $SSID"
log_info "  2. Password: $PASSWORD"
log_info "  3. Browse: http://raspilokal.com"
log_info "================================================="
log_info "  NOTE: This will disable Wi-Fi internet access "
log_info "  on the Pi as it is now acting as an Access Point."
log_info "================================================="
