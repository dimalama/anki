#!/bin/bash

# Script to update nginx configuration with Anki location blocks
# This script will backup the current config and add the Anki routes

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

NGINX_CONFIG="/etc/nginx/sites-available/optitrade"
BACKUP_FILE="/etc/nginx/sites-available/optitrade.backup.$(date +%Y%m%d_%H%M%S)"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Nginx Configuration Update for Anki${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}ERROR:${NC} This script must be run with sudo"
    echo "Usage: sudo ./update-nginx.sh"
    exit 1
fi

# Check if nginx config exists
if [ ! -f "$NGINX_CONFIG" ]; then
    echo -e "${RED}ERROR:${NC} Nginx config not found at $NGINX_CONFIG"
    exit 1
fi

# Check if Anki location already exists
if grep -q "location /anki" "$NGINX_CONFIG"; then
    echo -e "${YELLOW}WARNING:${NC} Anki location block already exists in nginx config"
    echo "No changes needed."
    exit 0
fi

# Backup current config
echo -e "${GREEN}==>${NC} Creating backup: $BACKUP_FILE"
cp "$NGINX_CONFIG" "$BACKUP_FILE"

# Create temporary file with new configuration
TEMP_FILE=$(mktemp)

# Read the original file and insert Anki configuration before the last closing brace
awk '
/^}$/ && !inserted {
    print "    # Anki Deck Generator app - Proxy to backend on port 8002"
    print "    location /anki {"
    print "        # Serve frontend static files"
    print "        alias /home/dima/Projects/anki/frontend/dist;"
    print "        try_files $uri $uri/ /anki/index.html;"
    print "        index index.html;"
    print ""
    print "        # Cache static assets"
    print "        location ~* /anki/.*\\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {"
    print "            alias /home/dima/Projects/anki/frontend/dist;"
    print "            expires 1y;"
    print "            add_header Cache-Control \"public, immutable\";"
    print "        }"
    print "    }"
    print ""
    print "    # Anki API endpoints - Proxy to FastAPI backend"
    print "    location /anki/api {"
    print "        rewrite ^/anki/api(.*)$ /api$1 break;"
    print ""
    print "        proxy_pass http://127.0.0.1:8002;"
    print "        proxy_http_version 1.1;"
    print ""
    print "        # Headers"
    print "        proxy_set_header Host $host;"
    print "        proxy_set_header X-Real-IP $remote_addr;"
    print "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;"
    print "        proxy_set_header X-Forwarded-Proto $scheme;"
    print "        proxy_set_header Connection \"\";"
    print ""
    print "        # Timeouts"
    print "        proxy_connect_timeout 300s;"
    print "        proxy_send_timeout 300s;"
    print "        proxy_read_timeout 300s;"
    print ""
    print "        # Buffering"
    print "        proxy_buffering off;"
    print "        proxy_request_buffering off;"
    print "    }"
    print ""
    print "    # Anki static files (generated .apkg files)"
    print "    location /anki/static {"
    print "        rewrite ^/anki/static(.*)$ /static$1 break;"
    print ""
    print "        proxy_pass http://127.0.0.1:8002;"
    print "        proxy_http_version 1.1;"
    print ""
    print "        proxy_set_header Host $host;"
    print "        proxy_set_header X-Real-IP $remote_addr;"
    print "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;"
    print "        proxy_set_header X-Forwarded-Proto $scheme;"
    print "    }"
    print ""
    inserted = 1
}
{ print }
' "$NGINX_CONFIG" > "$TEMP_FILE"

# Replace the original file
cp "$TEMP_FILE" "$NGINX_CONFIG"
rm "$TEMP_FILE"

echo -e "${GREEN}==>${NC} Nginx configuration updated"

# Test nginx configuration
echo -e "${GREEN}==>${NC} Testing nginx configuration..."
if nginx -t; then
    echo -e "${GREEN}==>${NC} Configuration test passed"
    echo -e "${GREEN}==>${NC} Reloading nginx..."
    systemctl reload nginx
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}Nginx configuration updated successfully!${NC}"
    echo -e "${GREEN}========================================${NC}\n"
    echo -e "Anki Deck Generator is now available at:"
    echo -e "${YELLOW}http://192.168.0.174/anki${NC}\n"
else
    echo -e "${RED}ERROR:${NC} Nginx configuration test failed"
    echo -e "${YELLOW}Restoring backup...${NC}"
    cp "$BACKUP_FILE" "$NGINX_CONFIG"
    echo -e "${YELLOW}Backup restored. Please check the configuration manually.${NC}"
    exit 1
fi
