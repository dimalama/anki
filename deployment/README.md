# Anki Deck Generator - Deployment Guide

This guide covers deploying the Anki Deck Generator to your Xubuntu home server alongside OptiTrade and Ezhome applications.

## Current Server Setup

Your server (192.168.0.174) currently hosts:
- **OptiTrade**: `http://192.168.0.174/` (backend on port 8001)
- **Ezhome**: `http://192.168.0.174:8000/` (proxied at `/ezhome`)

After deployment, Anki will be available at:
- **Anki Deck Generator**: `http://192.168.0.174/anki` (backend on port 8002)

## Architecture

```
Internet/Local Network
         ↓
    Nginx (Port 80)
    ├── / → OptiTrade (Frontend + API at /api)
    ├── /ezhome → Ezhome app (port 8000)
    └── /anki → Anki Deck Generator
         ├── /anki → Frontend (React SPA)
         ├── /anki/api → Backend API (FastAPI on port 8002)
         └── /anki/static → Generated .apkg files
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- uv (Python package manager)
- Nginx (already configured)
- Git

## Quick Deployment

Run the automated deployment script:

```bash
cd /home/dima/Projects/anki
./deployment/deploy.sh
```

This script will:
1. Pull latest changes from Git
2. Set up Python backend with virtual environment
3. Install backend dependencies
4. Build frontend production bundle
5. Install systemd service
6. Configure and restart services

## Manual Deployment Steps

If you prefer manual deployment or need to troubleshoot:

### 1. Backend Setup

```bash
cd /home/dima/Projects/anki/backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
uv sync
# or: pip install -r requirements.txt

# Test backend
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### 2. Frontend Setup

```bash
cd /home/dima/Projects/anki/frontend

# Install dependencies
npm install

# Build production version
npm run build

# Output will be in: frontend/dist/
```

### 3. Install Systemd Service

```bash
# Copy service file
sudo cp /home/dima/Projects/anki/deployment/anki-backend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable anki-backend
sudo systemctl start anki-backend

# Check status
sudo systemctl status anki-backend
```

### 4. Update Nginx Configuration

Add the location blocks from `deployment/nginx-anki-location.conf` to your existing nginx configuration:

```bash
# Edit nginx config
sudo nano /etc/nginx/sites-available/optitrade

# Add the location blocks for /anki, /anki/api, and /anki/static
# (see nginx-anki-location.conf for the exact configuration)

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

## Port Allocation

| Application | Backend Port | Access URL |
|-------------|--------------|------------|
| OptiTrade | 8001 | http://192.168.0.174/ |
| Ezhome | 8000 | http://192.168.0.174:8000/ |
| **Anki** | **8002** | **http://192.168.0.174/anki** |

## Service Management

### View Logs
```bash
# Backend logs
sudo journalctl -u anki-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/optitrade.access.log
sudo tail -f /var/log/nginx/optitrade.error.log
```

### Restart Services
```bash
# Restart backend
sudo systemctl restart anki-backend

# Reload nginx
sudo systemctl reload nginx
```

### Check Service Status
```bash
# Backend status
sudo systemctl status anki-backend

# Nginx status
sudo systemctl status nginx
```

## Updating the Application

To update after making code changes:

```bash
cd /home/dima/Projects/anki

# Pull latest changes
git pull

# Update backend
cd backend
source .venv/bin/activate
uv sync
cd ..

# Rebuild frontend
cd frontend
npm install
npm run build
cd ..

# Restart backend service
sudo systemctl restart anki-backend
```

Or simply run the deployment script again:
```bash
./deployment/deploy.sh
```

## Directory Structure

```
/home/dima/Projects/anki/
├── backend/
│   ├── .venv/                    # Python virtual environment
│   ├── app/                      # Backend source code
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── api/                 # API endpoints
│   │   ├── core/                # Configuration
│   │   ├── models/              # Pydantic models
│   │   └── services/            # Business logic
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── dist/                     # Built frontend (served by nginx)
│   ├── src/                      # Frontend source
│   ├── package.json
│   └── vite.config.ts           # Configured with /anki base path
├── deployment/
│   ├── README.md                # This file
│   ├── deploy.sh                # Automated deployment script
│   ├── anki-backend.service     # Systemd service file
│   └── nginx-anki-location.conf # Nginx location blocks
├── apkg/                         # Generated Anki deck files
├── csv/                          # CSV files for deck generation
└── media/                        # Media files (images, audio)
```

## Troubleshooting

### Backend won't start
```bash
# Check logs
sudo journalctl -u anki-backend -n 50

# Check if port 8002 is available
sudo lsof -i :8002

# Test manually
cd /home/dima/Projects/anki/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### Frontend shows 404 or blank page
- Verify frontend was built: `ls -la /home/dima/Projects/anki/frontend/dist/`
- Check nginx configuration: `sudo nginx -t`
- Verify base path in vite.config.ts is set to `/anki/`
- Check nginx error logs: `sudo tail -f /var/log/nginx/optitrade.error.log`

### API requests fail (CORS errors)
- Check backend is running: `sudo systemctl status anki-backend`
- Verify nginx proxy configuration for `/anki/api`
- Check backend logs: `sudo journalctl -u anki-backend -f`

### Changes not reflecting
- Rebuild frontend: `cd frontend && npm run build`
- Restart backend: `sudo systemctl restart anki-backend`
- Clear browser cache (Ctrl+Shift+R)
- Check nginx is serving correct directory

## Development vs Production

### Development Mode
```bash
# Terminal 1 - Backend
cd /home/dima/Projects/anki/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

# Terminal 2 - Frontend
cd /home/dima/Projects/anki/frontend
npm run dev
# Access at: http://localhost:5173
```

### Production Mode
- Backend runs as systemd service on port 8002
- Frontend served as static files by nginx at `/anki`
- Access at: `http://192.168.0.174/anki`

## Security Considerations

1. **Network Access**: Nginx is configured to allow only local network (192.168.0.0/24)
2. **File Permissions**: Ensure `.env` files are not world-readable
3. **Updates**: Keep dependencies updated regularly
4. **Backups**: Consider backing up the `apkg/` directory with generated decks

## API Documentation

Once deployed, API documentation is available at:
- **Swagger UI**: `http://192.168.0.174/anki/api/docs`
- **ReDoc**: `http://192.168.0.174/anki/api/redoc`

## Support

For issues:
1. Check service logs: `sudo journalctl -u anki-backend -f`
2. Verify nginx config: `sudo nginx -t`
3. Check service status: `sudo systemctl status anki-backend`
4. Review nginx logs: `sudo tail -f /var/log/nginx/optitrade.error.log`
