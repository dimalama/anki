# Quick Start Deployment Guide

## One-Command Deployment

```bash
cd /home/dima/Projects/anki && ./deployment/deploy.sh
```

## What You Need to Do After Running the Script

### 1. Update Nginx Configuration

The script will warn you if nginx configuration needs updating. Add these location blocks to `/etc/nginx/sites-available/optitrade`:

```bash
sudo nano /etc/nginx/sites-available/optitrade
```

Add the following **before** the closing `}` of the main server block (after the `/ezhome` location):

```nginx
    # Anki Deck Generator app - Proxy to backend on port 8002
    location /anki {
        # Serve frontend static files
        alias /home/dima/Projects/anki/frontend/dist;
        try_files $uri $uri/ /anki/index.html;
        index index.html;

        # Cache static assets
        location ~* /anki/.*\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            alias /home/dima/Projects/anki/frontend/dist;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Anki API endpoints - Proxy to FastAPI backend
    location /anki/api {
        rewrite ^/anki/api(.*)$ /api$1 break;

        proxy_pass http://127.0.0.1:8002;
        proxy_http_version 1.1;

        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";

        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        # Buffering
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Anki static files (generated .apkg files)
    location /anki/static {
        rewrite ^/anki/static(.*)$ /static$1 break;

        proxy_pass http://127.0.0.1:8002;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
```

### 2. Test and Reload Nginx

```bash
# Test configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

### 3. Verify Deployment

```bash
# Check backend service
sudo systemctl status anki-backend

# Check backend logs
sudo journalctl -u anki-backend -f

# Test in browser
# Open: http://192.168.0.174/anki
```

## Quick Reference

### Service Commands
```bash
# Start
sudo systemctl start anki-backend

# Stop
sudo systemctl stop anki-backend

# Restart
sudo systemctl restart anki-backend

# Status
sudo systemctl status anki-backend

# Logs
sudo journalctl -u anki-backend -f
```

### Update Application
```bash
cd /home/dima/Projects/anki
./deployment/deploy.sh
```

### Access URLs
- **Application**: http://192.168.0.174/anki
- **API Docs**: http://192.168.0.174/anki/api/docs
- **Health Check**: http://192.168.0.174/anki/api/health

## Troubleshooting

### Service won't start
```bash
sudo journalctl -u anki-backend -n 50
```

### Port already in use
```bash
sudo lsof -i :8002
```

### Nginx errors
```bash
sudo tail -f /var/log/nginx/optitrade.error.log
```
