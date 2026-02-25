#!/bin/bash
# LoKal - SSL Certificate Generation Script
# Generates a self-signed certificate for local HTTPS access

# Create certs directory if it doesn't exist
mkdir -p certs
cd certs

echo "Generating self-signed SSL certificate..."

# Generate private key and self-signed certificate in one command
# Valid for 365 days
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=PH/ST=MetroManila/L=Manila/O=LoKal/OU=Education/CN=192.168.4.1"

echo ""
echo "======================================"
echo "  SSL Certificate Generated!"
echo "======================================"
echo "The following files were created in the certs/ directory:"
echo "  - cert.pem (Certificate)"
echo "  - key.pem (Private Key)"
echo ""
echo "To run LoKal with HTTPS in development, use:"
echo "  python manage.py runsslserver --certificate certs/cert.pem --key certs/key.pem 0.0.0.0:8000"
echo ""
echo "NOTE: Your browser will show a security warning. Click 'Advanced' and 'Proceed anyway'."
