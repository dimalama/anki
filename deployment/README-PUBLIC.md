# Anki Deck Generator - Deployment Guide

This guide covers deploying the Anki Deck Generator to a Linux server with nginx and systemd.

## Architecture

```
Internet/Local Network
         ↓
    Nginx (Port 80)
    └── /anki → Anki Deck Generator
         ├── /anki → Frontend (React SPA)
         ├── /anki/api → Backend API (FastAPI on port 8002)
         └── /anki/static → Generated .apkg files
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- uv (Python package manager) or pip
- Nginx
- Git

## Quick Deployment

Run the automated deployment script:

```bash
cd /path/to/anki
./deployment/deploy.sh
```

This script will:
1. Pull latest changes from Git
2. Set up Python backend with virtual environment
3. Install backend dependencies
4. Build frontend production bundle
5. Install systemd service
6. Restart backend service
7. Check nginx configuration

### Manual Deployment

If you prefer to deploy manually:

#### 1. Backend Setup

```bash
cd /path/to/anki/backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# OR with uv:
uv sync
```

#### 2. Frontend Setup

```bash
cd /path/to/anki/frontend

# Install dependencies
npm install

# Build production bundle
npm run build
```

#### 3. Systemd Service

```bash
# Edit the service file first to replace YOUR_USERNAME with your actual username
nano deployment/anki-backend.service

# Copy service file
sudo cp deployment/anki-backend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable anki-backend
sudo systemctl start anki-backend

# Check status
sudo systemctl status anki-backend
```

#### 4. Nginx Configuration

Edit the nginx configuration file and add the location blocks from `deployment/nginx-anki-location.conf`.

**Important**: Replace `/home/YOUR_USERNAME/Projects/anki` with your actual project path in the nginx config.

```bash
# Edit nginx config (adjust path to your nginx site config)
sudo nano /etc/nginx/sites-available/default

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

## Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

Update the `CORS_ORIGINS` to include your server's IP address.

### Port Configuration

The application uses port **8002** for the backend API. Make sure this port is available and not used by other services.

```bash
# Check if port is in use
sudo lsof -i :8002
```

## Service Management

### View Logs

```bash
# Backend logs
sudo journalctl -u anki-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Services

```bash
# Restart backend
sudo systemctl restart anki-backend

# Reload nginx
sudo systemctl reload nginx
```

### Stop Services

```bash
sudo systemctl stop anki-backend
```

## Updates

To update after making code changes:

```bash
cd /path/to/anki

# Pull latest changes
git pull

# Run deployment script
./deployment/deploy.sh
```

## Directory Structure

```
/path/to/anki/
├── backend/
│   ├── .venv/                    # Python virtual environment
│   ├── app/                      # Backend source code
│   ├── .env                      # Environment variables (create from .env.example)
│   └── requirements.txt
├── frontend/
│   ├── dist/                     # Production build (generated)
│   ├── src/                      # Frontend source code
│   └── package.json
├── deployment/
│   ├── deploy.sh                 # Automated deployment script
│   ├── update-nginx.sh           # Nginx configuration helper
│   ├── anki-backend.service      # Systemd service file
│   └── nginx-anki-location.conf  # Nginx location blocks
├── apkg/                         # Generated Anki deck files
├── csv/                          # CSV input files
└── media/                        # Media files for cards
```

## Troubleshooting

### Backend not starting

```bash
# Check logs
sudo journalctl -u anki-backend -n 50

# Check if port is already in use
sudo lsof -i :8002

# Test manually
cd /path/to/anki/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### Frontend shows 404 or blank page

- Verify frontend was built: `ls -la /path/to/anki/frontend/dist/`
- Check nginx configuration: `sudo nginx -t`
- Verify base path in vite.config.ts is set to `/anki/`
- Check nginx error logs: `sudo tail -f /var/log/nginx/error.log`

### API calls failing (CORS errors)

- Check backend `.env` file has correct `CORS_ORIGINS`
- Ensure your server IP is included in `CORS_ORIGINS`
- Restart backend after changing `.env`: `sudo systemctl restart anki-backend`

### 502 Bad Gateway

- Backend service is not running: `sudo systemctl status anki-backend`
- Backend crashed: Check logs with `sudo journalctl -u anki-backend -n 50`
- Port mismatch: Verify nginx proxies to port 8002

## Development Mode

For local development:

```bash
# Terminal 1 - Backend
cd /path/to/anki/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

# Terminal 2 - Frontend
cd /path/to/anki/frontend
npm run dev
# Access at: http://localhost:5173
```

### Production Mode

- Backend runs as systemd service on port 8002
- Frontend served as static files by nginx at `/anki`
- Access at: `http://YOUR_SERVER_IP/anki`

## Security Considerations

- Backend only listens on `127.0.0.1` (localhost)
- All external access goes through nginx reverse proxy
- CORS is configured to only allow specific origins
- Service runs with limited user permissions

## API Documentation

Once deployed, API documentation is available at:
- **Swagger UI**: `http://YOUR_SERVER_IP/anki/api/docs`
- **ReDoc**: `http://YOUR_SERVER_IP/anki/api/redoc`

## Support

For issues or questions:
- Check the logs first
- Review the troubleshooting section
- Ensure all prerequisites are installed
- Verify file permissions are correct
