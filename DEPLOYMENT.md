# Anki Deck Generator - Server Deployment

This application is now configured for deployment on your Xubuntu home server at `192.168.0.174`.

## Quick Start

```bash
cd /home/dima/Projects/anki
./deployment/deploy.sh
```

After the script completes, update nginx configuration:

```bash
sudo ./deployment/update-nginx.sh
```

Access the application at: **http://192.168.0.174/anki**

## Documentation

Comprehensive deployment documentation is available in the `deployment/` directory:

- **[deployment/QUICK-START.md](deployment/QUICK-START.md)** - Quick deployment guide
- **[deployment/README.md](deployment/README.md)** - Complete deployment documentation
- **[deployment/DEPLOYMENT-CHECKLIST.md](deployment/DEPLOYMENT-CHECKLIST.md)** - Step-by-step checklist

## Architecture

The application runs alongside your existing applications:

```
Nginx (Port 80)
├── / → OptiTrade (port 8001)
├── /ezhome → Ezhome (port 8000)
└── /anki → Anki Deck Generator (port 8002)
     ├── Frontend: React SPA served by nginx
     └── Backend: FastAPI on port 8002
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
cd /home/dima/Projects/anki
./deployment/deploy.sh
```

## Ports

| Application | Backend Port | Access URL |
|-------------|--------------|------------|
| OptiTrade | 8001 | http://192.168.0.174/ |
| Ezhome | 8000 | http://192.168.0.174:8000/ |
| **Anki** | **8002** | **http://192.168.0.174/anki** |

## Support

For detailed troubleshooting and configuration options, see:
- [deployment/README.md](deployment/README.md)
- Backend logs: `sudo journalctl -u anki-backend -f`
- Nginx logs: `sudo tail -f /var/log/nginx/optitrade.error.log`
