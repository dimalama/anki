# Deployment Setup Summary

## Overview

The Anki Deck Generator application has been configured for deployment on your Xubuntu home server at `192.168.0.174`. The deployment setup follows the same pattern as your existing OptiTrade and Ezhome applications.

## What Has Been Created

### 1. Deployment Scripts
- **`deploy.sh`** - Automated deployment script that handles:
  - Git pull
  - Backend virtual environment setup
  - Dependency installation (using uv or pip)
  - Frontend build
  - Systemd service installation
  - Service restart

- **`update-nginx.sh`** - Automated nginx configuration updater
  - Backs up current nginx config
  - Adds Anki location blocks
  - Tests and reloads nginx

### 2. Configuration Files
- **`anki-backend.service`** - Systemd service file
  - Runs backend on port 8002
  - Auto-restart on failure
  - Starts on boot

- **`nginx-anki-location.conf`** - Nginx location blocks
  - Routes `/anki` to frontend
  - Routes `/anki/api` to backend (port 8002)
  - Routes `/anki/static` for .apkg downloads

### 3. Documentation
- **`README.md`** - Complete deployment guide
- **`QUICK-START.md`** - Quick reference guide
- **`DEPLOYMENT-CHECKLIST.md`** - Step-by-step checklist
- **`ACCESS-GUIDE.md`** - How to access the application
- **`SUMMARY.md`** - This file

### 4. Application Updates
- **`frontend/vite.config.ts`** - Updated with:
  - Base path: `/anki/`
  - Development proxy for API calls

- **`backend/.env.example`** - Updated with:
  - Production server IP in CORS origins

## Deployment Architecture

```
Server: 192.168.0.174
├── Nginx (Port 80)
│   ├── / → OptiTrade (backend: 8001)
│   ├── /ezhome → Ezhome (backend: 8000)
│   └── /anki → Anki Deck Generator (backend: 8002)
│
└── Systemd Services
    ├── optitrade-backend (port 8001)
    ├── ezhome (port 8000, Docker)
    └── anki-backend (port 8002) ← NEW
```

## How to Deploy

### Option 1: Fully Automated (Recommended)

```bash
# Step 1: Deploy application
cd /home/dima/Projects/anki
./deployment/deploy.sh

# Step 2: Update nginx
sudo ./deployment/update-nginx.sh

# Step 3: Access application
# Open browser to: http://192.168.0.174/anki
```

### Option 2: Manual Deployment

Follow the step-by-step guide in `deployment/QUICK-START.md`

## What Happens During Deployment

1. **Backend Setup**
   - Creates Python virtual environment at `backend/.venv`
   - Installs dependencies from `requirements.txt` or `pyproject.toml`
   - Creates necessary directories (apkg, csv, media, config, templates)

2. **Frontend Build**
   - Installs npm dependencies
   - Builds production bundle to `frontend/dist/`
   - Assets are optimized and minified

3. **Service Installation**
   - Copies systemd service file to `/etc/systemd/system/`
   - Enables service for auto-start on boot
   - Starts the backend service on port 8002

4. **Nginx Configuration**
   - Adds location blocks for `/anki`, `/anki/api`, `/anki/static`
   - Tests configuration validity
   - Reloads nginx to apply changes

## Port Allocation

| Application | Port | Status |
|-------------|------|--------|
| OptiTrade | 8001 | Existing |
| Ezhome | 8000 | Existing |
| **Anki** | **8002** | **New** |

## Access URLs

After deployment:
- **Application**: http://192.168.0.174/anki
- **API Docs**: http://192.168.0.174/anki/api/docs
- **Health Check**: http://192.168.0.174/anki/api/health

## Service Management

```bash
# Start/Stop/Restart
sudo systemctl start anki-backend
sudo systemctl stop anki-backend
sudo systemctl restart anki-backend

# View logs
sudo journalctl -u anki-backend -f

# Check status
sudo systemctl status anki-backend
```

## File Locations

```
/home/dima/Projects/anki/
├── backend/
│   ├── .venv/                           # Virtual environment
│   ├── app/                             # Backend source
│   └── .env                             # Configuration (create from .env.example)
├── frontend/
│   ├── dist/                            # Built frontend (served by nginx)
│   └── vite.config.ts                   # Updated with /anki base path
├── deployment/
│   ├── deploy.sh                        # Main deployment script
│   ├── update-nginx.sh                  # Nginx updater script
│   ├── anki-backend.service             # Systemd service
│   ├── nginx-anki-location.conf         # Nginx config
│   └── *.md                             # Documentation
├── apkg/                                # Generated deck files
├── csv/                                 # CSV input files
└── media/                               # Media files

System Files:
├── /etc/systemd/system/anki-backend.service
└── /etc/nginx/sites-available/optitrade (updated with /anki locations)
```

## Next Steps

1. **Run deployment script**:
   ```bash
   cd /home/dima/Projects/anki
   ./deployment/deploy.sh
   ```

2. **Update nginx** (if not done automatically):
   ```bash
   sudo ./deployment/update-nginx.sh
   ```

3. **Verify deployment**:
   - Check service: `sudo systemctl status anki-backend`
   - Check logs: `sudo journalctl -u anki-backend -n 20`
   - Open browser: `http://192.168.0.174/anki`

4. **Test functionality**:
   - Create a deck
   - Add cards
   - Generate .apkg file
   - Download deck

## Troubleshooting

If you encounter issues, refer to:
- `deployment/README.md` - Comprehensive troubleshooting guide
- `deployment/DEPLOYMENT-CHECKLIST.md` - Step-by-step verification
- Backend logs: `sudo journalctl -u anki-backend -f`
- Nginx logs: `sudo tail -f /var/log/nginx/optitrade.error.log`

## Maintenance

### Update Application
```bash
cd /home/dima/Projects/anki
./deployment/deploy.sh
```

### View Logs
```bash
# Backend
sudo journalctl -u anki-backend -f

# Nginx
sudo tail -f /var/log/nginx/optitrade.access.log
```

### Restart Services
```bash
sudo systemctl restart anki-backend
sudo systemctl reload nginx
```

## Key Features

✅ **Auto-start on boot** - Service enabled in systemd
✅ **Auto-restart on failure** - Systemd handles crashes
✅ **Local network only** - Nginx restricts access
✅ **Integrated with existing apps** - Shares nginx with OptiTrade/Ezhome
✅ **Easy updates** - Single script deployment
✅ **Comprehensive logging** - Systemd journal + nginx logs

## Support

For questions or issues:
1. Check the documentation in `deployment/`
2. Review logs for error messages
3. Verify all services are running
4. Ensure port 8002 is not in use by other services
