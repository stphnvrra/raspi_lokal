#!/bin/bash
# Script to setup dnsmasq and nginx for local offline access via raspilokal.com
# Run this on your Raspberry Pi

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check for root
if [ "$EUID" -ne 0 ]; then
  log_error "Please run as root (sudo ./deployment/setup_dns_proxy.sh)"
  exit 1
fi

PI_IP=$(hostname -I | awk '{print $1}')
log_info "Detected Raspberry Pi IP: $PI_IP"

log_info "Installing dnsmasq and nginx..."
apt-get update
apt-get install -y dnsmasq nginx

# 1. Configure dnsmasq
log_info "Configuring dnsmasq..."
cat > /etc/dnsmasq.d/raspilokal.conf << EOF
address=/raspilokal.com/$PI_IP
interface=eth0
interface=wlan0
EOF

systemctl restart dnsmasq
log_info "dnsmasq configured: raspilokal.com now points to $PI_IP on this Pi."

# 2. Configure Nginx as reverse proxy
log_info "Configuring Nginx..."
cat > /etc/nginx/sites-available/lokal << EOF
server {
    listen 80;
    server_name raspilokal.com $PI_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files if needed
    location /static/ {
        alias /home/lokal/Desktop/loKal/staticfiles/;
    }

    # Media files if needed
    location /media/ {
        alias /home/lokal/Desktop/loKal/media/;
    }
}
EOF

ln -sf /etc/nginx/sites-available/lokal /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx
log_info "Nginx configured: Traffic to http://raspilokal.com (port 80) is now forwarded to port 8000."

log_info "================================================="
log_info "  Offline DNS Setup Complete!"
log_info "================================================="
log_info "  Domain: http://raspilokal.com"
log_info "  IP Address: $PI_IP"
log_info ""
log_info "  IMPORTANT NEXT STEPS:"
log_info "  1. On your Router: Set the primary DNS server to $PI_IP"
log_info "  2. OR on your Phone: Go to Wi-Fi settings for this network,"
    log_info "     set DNS to Manual, and add $PI_IP"
log_info "================================================="
