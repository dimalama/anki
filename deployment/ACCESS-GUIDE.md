# Access Guide - Anki Deck Generator

## Application URLs

After deployment, the Anki Deck Generator will be accessible at:

### Main Application
**URL**: `http://192.168.0.174/anki`

This is the main web interface where you can:
- Create and manage Anki decks
- Import CSV files
- Add cards manually
- Generate .apkg files
- Download decks for Anki

### API Documentation
**Swagger UI**: `http://192.168.0.174/anki/api/docs`
**ReDoc**: `http://192.168.0.174/anki/api/redoc`

Interactive API documentation for developers.

### Health Check
**URL**: `http://192.168.0.174/anki/api/health`

Returns `{"status": "healthy"}` if the backend is running correctly.

## All Applications on Server

Your server hosts three applications:

| Application | URL | Description |
|-------------|-----|-------------|
| **OptiTrade** | http://192.168.0.174/ | Stock trading analysis tool |
| **Ezhome** | http://192.168.0.174:8000/ | Home management app |
| **Anki** | http://192.168.0.174/anki | Anki deck generator |

## Network Access

All applications are configured to be accessible only from:
- Localhost (127.0.0.1)
- Local network (192.168.0.0/24)

External access is blocked by nginx configuration.

## Accessing from Other Devices

From any device on your local network (192.168.0.x):

1. **Desktop/Laptop**: Open browser to `http://192.168.0.174/anki`
2. **Mobile**: Open browser to `http://192.168.0.174/anki`
3. **Tablet**: Open browser to `http://192.168.0.174/anki`

## Troubleshooting Access

### Cannot access the application

1. **Check if backend is running**:
   ```bash
   sudo systemctl status anki-backend
   ```

2. **Check if nginx is running**:
   ```bash
   sudo systemctl status nginx
   ```

3. **Verify network connectivity**:
   ```bash
   ping 192.168.0.174
   ```

4. **Check backend directly**:
   ```bash
   curl http://localhost:8002/api/health
   ```

5. **Check nginx logs**:
   ```bash
   sudo tail -f /var/log/nginx/optitrade.error.log
   ```

### Getting 404 errors

- Verify nginx configuration includes `/anki` location blocks
- Check frontend was built: `ls -la /home/dima/Projects/anki/frontend/dist/`
- Reload nginx: `sudo systemctl reload nginx`

### Getting 502 Bad Gateway

- Backend service is not running or crashed
- Check logs: `sudo journalctl -u anki-backend -f`
- Restart backend: `sudo systemctl restart anki-backend`

### API calls failing (CORS errors)

- Check backend `.env` file includes server IP in CORS_ORIGINS
- Restart backend after changing .env: `sudo systemctl restart anki-backend`

## Port Information

The backend runs on **port 8002** internally, but you don't need to access it directly. Nginx handles all routing through port 80.

## Development Access

When running in development mode:

- **Frontend**: `http://localhost:5173` (Vite dev server)
- **Backend**: `http://localhost:8002` (Direct FastAPI access)

Production uses nginx routing at `/anki` path.
