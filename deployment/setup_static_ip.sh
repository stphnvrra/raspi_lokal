#!/bin/bash
# Script to set a static IP on Raspberry Pi (Bookworm/NetworkManager or Bullseye/dhcpcd)
# Run as root: sudo ./deployment/setup_static_ip.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if [ "$EUID" -ne 0 ]; then
  log_error "Please run as root: sudo ./deployment/setup_static_ip.sh"
  exit 1
fi

# Configuration (Edit these or pass as arguments)
INTERFACE="wlan0" # Default to Wi-Fi
STATIC_IP=${1:-"192.168.1.100"}
GATEWAY=${2:-"192.168.1.1"}
DNS_SERVERS=${3:-"8.8.8.8,1.1.1.1"} # External DNS for setup, will be overridden by dnsmasq for clients

log_info "Configuration:"
log_info "  Interface: $INTERFACE"
log_info "  Static IP: $STATIC_IP/24"
log_info "  Gateway:   $GATEWAY"

# Detect Network Manager or dhcpcd
if command -v nmcli >/dev/null 2>&1; then
    log_info "NetworkManager detected. Configuring using nmcli..."
    
    # Get current connection name for the interface
    CON_NAME=$(nmcli -t -f NAME,DEVICE connection show --active | grep ":$INTERFACE" | cut -d: -f1 || echo "")
    
    if [ -z "$CON_NAME" ]; then
        log_warn "No active connection found for $INTERFACE. Creating/Modifying default..."
        CON_NAME=$INTERFACE
    fi

    nmcli con mod "$CON_NAME" ipv4.addresses "$STATIC_IP/24"
    nmcli con mod "$CON_NAME" ipv4.gateway "$GATEWAY"
    nmcli con mod "$CON_NAME" ipv4.dns "$DNS_SERVERS"
    nmcli con mod "$CON_NAME" ipv4.method manual
    
    log_info "Restarting connection..."
    nmcli con up "$CON_NAME"
    
elif [ -f /etc/dhcpcd.conf ]; then
    log_info "dhcpcd detected. Configuring /etc/dhcpcd.conf..."
    
    # Check if already configured
    if grep -q "interface $INTERFACE" /etc/dhcpcd.conf; then
        log_warn "Static IP configuration already exists in /etc/dhcpcd.conf. Please edit manually to avoid duplicates."
    else
        cat >> /etc/dhcpcd.conf << EOF

# LoKal Static IP Configuration
interface $INTERFACE
static ip_address=$STATIC_IP/24
static routers=$GATEWAY
static domain_name_servers=$DNS_SERVERS
EOF
        log_info "Configuration added to /etc/dhcpcd.conf"
        systemctl restart dhcpcd
    fi
else
    log_error "Neither NetworkManager (nmcli) nor dhcpcd found. Unsupported OS version."
    exit 1
fi

log_info "================================================="
log_info "  Static IP Configuration Complete!"
log_info "================================================="
log_info "  New IP: $STATIC_IP"
log_info "  Interface: $INTERFACE"
log_info ""
log_info "  NOTE: If you lose connection, reconnect to the "
log_info "  network using the new IP address."
log_info "================================================="
