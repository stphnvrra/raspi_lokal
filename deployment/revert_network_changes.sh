#!/bin/bash
# Script to undo/revert changes made by setup_static_ip.sh and setup_dns_proxy.sh
# Run as root: sudo ./deployment/revert_network_changes.sh

# set -e  # Removed to prevent exiting on minor errors

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if [ "$EUID" -ne 0 ]; then
  log_error "Please run as root: sudo ./deployment/revert_network_changes.sh"
  exit 1
fi

log_info "-------------------------------------------------"
log_info "  LoKal Network Revert Script"
log_info "-------------------------------------------------"

# 1. Revert DNS/Proxy Changes
log_info "Checking for dnsmasq and nginx configurations..."

if [ -f /etc/dnsmasq.d/raspilokal.conf ]; then
    log_info "Removing raspilokal.conf from dnsmasq..."
    rm /etc/dnsmasq.d/raspilokal.conf
fi

if [ -f /etc/nginx/sites-enabled/lokal ]; then
    log_info "Removing Nginx lokal site configuration..."
    rm /etc/nginx/sites-enabled/lokal
    rm -f /etc/nginx/sites-available/lokal
    # Restore default if it was removed
    if [ ! -f /etc/nginx/sites-enabled/default ] && [ -f /etc/nginx/sites-available/default ]; then
        ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
    fi
fi

log_info "Restarting services to apply changes..."
systemctl restart dnsmasq || true
systemctl restart nginx || true

# 2. Revert Static IP Changes
INTERFACE="wlan0"

if command -v nmcli >/dev/null 2>&1; then
    log_info "NetworkManager detected. Reverting changes..."
    
    # 1. Specifically delete the LoKal Hotspot if it exists
    if nmcli con show "LoKal-Hotspot" >/dev/null 2>&1; then
        log_info "Removing LoKal-Hotspot connection..."
        nmcli con delete "LoKal-Hotspot" || true
    fi

    # 2. Revert the active connection on wlan0 to DHCP
    CON_NAME=$(nmcli -t -f NAME,DEVICE connection show --active | grep ":$INTERFACE" | cut -d: -f1 | head -n 1 || echo "")
    
    if [ -n "$CON_NAME" ]; then
        log_info "Setting connection '$CON_NAME' back to Automatic (DHCP)..."
        nmcli con mod "$CON_NAME" ipv4.method auto ipv4.addresses "" ipv4.gateway "" ipv4.dns "" || true
        log_info "Restarting connection..."
        nmcli con up "$CON_NAME" || true
    else
        log_warn "No active connection found on $INTERFACE. Attempting to bring up a default Wi-Fi..."
        # Try to find any other Wi-Fi connection that isn't the hotspot
        OTHER_CON=$(nmcli -t -f NAME connection show | grep -v "LoKal-Hotspot" | head -n 1 || echo "")
        if [ -n "$OTHER_CON" ]; then
            nmcli con up "$OTHER_CON" || true
        fi
    fi
    
elif [ -f /etc/dhcpcd.conf ]; then
    log_info "dhcpcd detected. Cleaning /etc/dhcpcd.conf..."
    # Remove the LoKal configuration block
    sed -i '/# LoKal Static IP Configuration/,+5d' /etc/dhcpcd.conf
    log_info "Configuration removed from /etc/dhcpcd.conf"
    systemctl restart dhcpcd
fi

log_info "================================================="
log_info "  Revert Complete!"
log_info "================================================="
log_info "  - Nginx/Dnsmasq proxy for raspilokal.com removed."
log_info "  - Network interface $INTERFACE set back to DHCP."
log_info "================================================="
log_info "  NOTE: Your IP address will likely change soon."
log_info "================================================="
