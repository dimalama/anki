# Anki Deck Generator - Server Deployment

This application is configured for deployment on a Linux server with nginx and systemd.

## Quick Start

```bash
cd /path/to/anki
./deployment/deploy.sh
```

After the script completes, update nginx configuration:

```bash
sudo ./deployment/update-nginx.sh
```

Access the application at: **http://YOUR_SERVER_IP/anki**

## Documentation

Comprehensive deployment documentation is available in the `deployment/` directory:

- **[deployment/QUICK-START.md](deployment/QUICK-START.md)** - Quick deployment guide
- **[deployment/README.md](deployment/README.md)** - Complete deployment documentation
- **[deployment/DEPLOYMENT-CHECKLIST.md](deployment/DEPLOYMENT-CHECKLIST.md)** - Step-by-step checklist

## Architecture

The application runs alongside your existing applications:

```
Nginx (Port 80)
└── /anki → Anki Deck Generator (port 8002)
     ├── Frontend: React SPA served by nginx
     └── Backend API: FastAPI on port 8002
```

## Key Files

- `deployment/deploy.sh` - Automated deployment script
- `deployment/update-nginx.sh` - Nginx configuration updater
- `deployment/anki-backend.service` - Systemd service file
- `deployment/nginx-anki-location.conf` - Nginx location blocks
- `frontend/vite.config.ts` - Configured with `/anki` base path

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

## Updating

To update the application after code changes:

```bash
cd /path/to/anki
./deployment/deploy.sh
```

## Ports

| Application | Backend Port | Access URL |
|-------------|--------------|------------|
| **Anki** | **8002** | **http://YOUR_SERVER_IP/anki** |

## Support

For detailed troubleshooting and configuration options, see:
- [deployment/README.md](deployment/README.md)
- Backend logs: `sudo journalctl -u anki-backend -f`
- Nginx logs: `sudo tail -f /var/log/nginx/error.log`
