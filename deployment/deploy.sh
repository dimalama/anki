#!/bin/bash

# Anki Deck Generator Deployment Script for Ubuntu Server
# This script automates the deployment process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/home/$(whoami)/Projects/anki"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
VENV_DIR="$BACKEND_DIR/.venv"
SERVICE_NAME="anki-backend"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Anki Deck Generator Deployment Script${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Function to print status messages
print_status() {
    echo -e "${GREEN}==>${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

# Check if running on Ubuntu/Debian
if [ ! -f /etc/debian_version ]; then
    print_error "This script is designed for Ubuntu/Debian systems"
    exit 1
fi

# Navigate to app directory
if [ ! -d "$APP_DIR" ]; then
    print_error "App directory not found: $APP_DIR"
    exit 1
fi

cd "$APP_DIR"

# Pull latest changes
print_status "Pulling latest changes from Git..."
git pull || {
    print_warning "Git pull failed. Continuing with local version..."
}

# Backend setup
print_status "Setting up Python backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating Python virtual environment..."
    cd "$BACKEND_DIR"
    python3 -m venv .venv
    cd "$APP_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install/update dependencies
print_status "Installing Python dependencies..."
cd "$BACKEND_DIR"
if command -v uv &> /dev/null; then
    export UV_HTTP_TIMEOUT=300
    uv sync
else
    print_warning "uv not found, using pip..."
    pip install -r requirements.txt
fi
cd "$APP_DIR"

# Frontend setup
print_status "Building frontend..."
cd "$FRONTEND_DIR"

# Install dependencies
print_status "Installing frontend dependencies..."
npm install

# Build production version
print_status "Building production frontend..."
npm run build

cd "$APP_DIR"

# Create necessary directories
print_status "Setting up directory structure..."
mkdir -p "$APP_DIR/apkg"
mkdir -p "$APP_DIR/csv"
mkdir -p "$APP_DIR/media"

# Check if .env file exists in backend
if [ ! -f "$BACKEND_DIR/.env" ]; then
    if [ -f "$BACKEND_DIR/.env.example" ]; then
        print_warning ".env file not found in backend"
        print_status "Creating .env from .env.example..."
        cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
        print_warning "Please edit .env file if needed"
        echo -e "${YELLOW}Run: nano $BACKEND_DIR/.env${NC}"
    fi
fi

# Setup systemd service
print_status "Setting up systemd service..."

# Check if service file exists in deployment directory
if [ -f "$APP_DIR/deployment/anki-backend.service" ]; then
    # Install service file
    sudo cp "$APP_DIR/deployment/anki-backend.service" /etc/systemd/system/anki-backend.service
    sudo systemctl daemon-reload

    print_status "Systemd service installed"
else
    print_warning "Service file not found in deployment directory"
fi

# Restart service if it exists
if systemctl list-unit-files | grep -q "$SERVICE_NAME.service"; then
    print_status "Restarting backend service..."
    sudo systemctl restart "$SERVICE_NAME"
    sudo systemctl enable "$SERVICE_NAME"

    # Wait a moment and check status
    sleep 2
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_status "Backend service is running"
    else
        print_error "Backend service failed to start"
        print_status "Check logs with: sudo journalctl -u $SERVICE_NAME -n 50"
        exit 1
    fi
else
    print_warning "Service not installed. Please install manually:"
    echo -e "${YELLOW}sudo cp deployment/anki-backend.service /etc/systemd/system/${NC}"
    echo -e "${YELLOW}sudo systemctl daemon-reload${NC}"
    echo -e "${YELLOW}sudo systemctl enable anki-backend${NC}"
    echo -e "${YELLOW}sudo systemctl start anki-backend${NC}"
fi

# Check nginx configuration
print_status "Checking nginx configuration..."
if grep -q "location /anki" /etc/nginx/sites-available/default 2>/dev/null || grep -q "location /anki" /etc/nginx/sites-enabled/* 2>/dev/null; then
    sudo nginx -t && {
        print_status "Reloading nginx..."
        sudo systemctl reload nginx
    } || {
        print_error "Nginx configuration test failed"
        print_status "Fix nginx config and run: sudo nginx -t"
    }
else
    print_warning "Nginx configuration for /anki not found"
    print_status "To set up nginx:"
    echo -e "${YELLOW}1. Add the location blocks from deployment/nginx-anki-location.conf${NC}"
    echo -e "${YELLOW}2. to your nginx site configuration${NC}"
    echo -e "${YELLOW}3. sudo nginx -t${NC}"
    echo -e "${YELLOW}4. sudo systemctl reload nginx${NC}"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

print_status "Service status:"
sudo systemctl status "$SERVICE_NAME" --no-pager || true

echo -e "\n${GREEN}Useful commands:${NC}"
echo -e "  View logs:    ${YELLOW}sudo journalctl -u $SERVICE_NAME -f${NC}"
echo -e "  Restart:      ${YELLOW}sudo systemctl restart $SERVICE_NAME${NC}"
echo -e "  Stop:         ${YELLOW}sudo systemctl stop $SERVICE_NAME${NC}"
echo -e "  Status:       ${YELLOW}sudo systemctl status $SERVICE_NAME${NC}"
echo -e "  Nginx logs:   ${YELLOW}sudo tail -f /var/log/nginx/access.log${NC}"
echo -e "\n${GREEN}Access the application at:${NC}"
echo -e "  ${YELLOW}http://YOUR_SERVER_IP/anki${NC}"
echo ""
