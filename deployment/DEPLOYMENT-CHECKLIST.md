# Deployment Checklist

Use this checklist to ensure successful deployment of the Anki Deck Generator.

## Pre-Deployment

- [ ] Server has Python 3.10+ installed
- [ ] Server has Node.js 18+ installed
- [ ] Server has nginx installed and running
- [ ] Server has uv installed (or pip as fallback)
- [ ] Git repository is cloned at `/home/dima/Projects/anki`
- [ ] Port 8002 is available (not used by other services)

## Deployment Steps

### 1. Run Deployment Script
```bash
cd /home/dima/Projects/anki
./deployment/deploy.sh
```

- [ ] Script completed without errors
- [ ] Backend virtual environment created
- [ ] Backend dependencies installed
- [ ] Frontend built successfully
- [ ] Systemd service installed
- [ ] Backend service started successfully

### 2. Update Nginx Configuration

**Option A: Automated (Recommended)**
```bash
sudo ./deployment/update-nginx.sh
```

**Option B: Manual**
- [ ] Edit `/etc/nginx/sites-available/optitrade`
- [ ] Add location blocks from `deployment/nginx-anki-location.conf`
- [ ] Test config: `sudo nginx -t`
- [ ] Reload nginx: `sudo systemctl reload nginx`

### 3. Verify Deployment

- [ ] Backend service is running: `sudo systemctl status anki-backend`
- [ ] Backend responds: `curl http://localhost:8002/api/health`
- [ ] Nginx configuration is valid: `sudo nginx -t`
- [ ] Nginx is running: `sudo systemctl status nginx`

### 4. Test Application

- [ ] Open browser to `http://192.168.0.174/anki`
- [ ] Application loads without errors
- [ ] Can navigate through the UI
- [ ] API calls work (check browser console)
- [ ] Can create/view decks
- [ ] Can generate .apkg files

### 5. Check Logs

```bash
# Backend logs (should show no errors)
sudo journalctl -u anki-backend -n 50

# Nginx access logs (should show requests to /anki)
sudo tail -n 20 /var/log/nginx/optitrade.access.log

# Nginx error logs (should be empty or minimal)
sudo tail -n 20 /var/log/nginx/optitrade.error.log
```

- [ ] No critical errors in backend logs
- [ ] Requests to `/anki` appear in nginx access logs
- [ ] No 404 or 502 errors in nginx error logs

## Post-Deployment

### Service Auto-Start
- [ ] Backend service enabled: `sudo systemctl is-enabled anki-backend`
- [ ] Service will start on boot

### Directory Permissions
- [ ] Backend can write to `/home/dima/Projects/anki/apkg`
- [ ] Backend can read from `/home/dima/Projects/anki/csv`
- [ ] Backend can read from `/home/dima/Projects/anki/media`

### Environment Configuration
- [ ] `.env` file exists in `/home/dima/Projects/anki/backend/`
- [ ] CORS origins include production server IP
- [ ] All required directories are created

## Troubleshooting

If any step fails, refer to:
- `deployment/README.md` - Full deployment guide
- `deployment/QUICK-START.md` - Quick reference
- Backend logs: `sudo journalctl -u anki-backend -f`
- Nginx logs: `sudo tail -f /var/log/nginx/optitrade.error.log`

## Current Server Configuration

After successful deployment:

| Application | URL | Backend Port |
|-------------|-----|--------------|
| OptiTrade | http://192.168.0.174/ | 8001 |
| Ezhome | http://192.168.0.174:8000/ | 8000 |
| **Anki** | **http://192.168.0.174/anki** | **8002** |

## Maintenance Commands

```bash
# Update application
cd /home/dima/Projects/anki && ./deployment/deploy.sh

# Restart backend
sudo systemctl restart anki-backend

# View logs
sudo journalctl -u anki-backend -f

# Reload nginx
sudo systemctl reload nginx
```
