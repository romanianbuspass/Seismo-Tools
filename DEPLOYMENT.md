# Deployment & Operations

## System Requirements

### Minimum
- **OS:** Windows 10+, Ubuntu 18.04+, Raspberry Pi OS (latest)
- **Python:** 3.10+
- **Node.js:** 14.0+ (SeedLink Monitor only)
- **RAM:** 512 MB
- **Storage:** 1 GB (plus archive space for seismic data)

### Recommended
- **OS:** Windows 11 Pro, Ubuntu 22.04 LTS
- **Python:** 3.12
- **Node.js:** 18 LTS
- **RAM:** 2 GB+
- **Storage:** SSD (10+ GB) for seismic archives

---

## Windows Deployment

### Step 1: Install Python 3.12

1. Download from [python.org](https://www.python.org) or use Anaconda
2. During install: **check "Add Python to PATH"**
3. Verify:
   ```cmd
   python --version
   ```

### Step 2: GPS Traveler Setup

```cmd
cd D:\GaiaGuard\gps_traveler_app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Launch (Batch Script)

Create `D:\GaiaGuard\start_gps_traveler.bat`:
```batch
@echo off
cd /d D:\GaiaGuard\gps_traveler_app
call venv\Scripts\activate
python app.py
pause
```

Double-click to run. Browser opens at `http://127.0.0.1:5000`.

### Step 4: Configure Serial Port

1. Open Windows Device Manager
2. Expand "Ports (COM & LPT)"
3. Identify your STGNSS port (e.g., "COM3")
4. Update in web UI: Data Source panel

### Step 5: SeedLink Monitor (Optional)

```cmd
cd slinktool-4.5.0\gui
npm install
npm start
```

Runs on `http://127.0.0.1:3000`.

---

## Linux / Raspberry Pi Deployment

### Step 1: Install Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3.12 python3.12-venv python3-pip curl
```

**Raspberry Pi:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip
```

### Step 2: GPS Traveler Setup

```bash
cd ~/seismo-tools/gps_traveler_app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Launch as Service (systemd)

Create `/etc/systemd/system/gps-traveler.service`:
```ini
[Unit]
Description=GPS/GNSS Test Traveler
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/seismo-tools/gps_traveler_app
ExecStart=/home/pi/seismo-tools/gps_traveler_app/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable & start:
```bash
sudo systemctl enable gps-traveler
sudo systemctl start gps-traveler
sudo systemctl status gps-traveler
```

View logs:
```bash
sudo journalctl -u gps-traveler -f
```

### Step 4: Serial Port Access

```bash
# Find STGNSS port
ls -la /dev/tty*

# Grant user access
sudo usermod -a -G dialout $USER
# Log out & back in
```

---

## Docker (Optional)

### Build Image

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY gps_traveler_app /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```

Build & run:
```bash
docker build -t gps-traveler .
docker run -p 5000:5000 --device=/dev/ttyUSB0 gps-traveler
```

---

## Backup & Restore

### Database Backup

**Windows:**
```cmd
xcopy "D:\GaiaGuard\gps_traveler_app\travelers.db" "D:\Backups\travelers_backup.db"
```

**Linux:**
```bash
cp ~/seismo-tools/gps_traveler_app/travelers.db ~/backups/travelers_backup.db
```

### Restore from Backup

```bash
cp ~/backups/travelers_backup.db ~/seismo-tools/gps_traveler_app/travelers.db
```

### Archive Export

All snapshots are JSON-exportable via the web UI:
1. Click snapshot in "Stored Travelers"
2. Right-click "Download JSON" → Save

---

## Troubleshooting

### GPS App Won't Start

**Error: `ModuleNotFoundError: No module named 'flask'`**
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Error: `Address already in use (port 5000)`**
- App already running on another terminal
- Or kill the process:
  ```bash
  # Windows
  netstat -ano | findstr :5000
  taskkill /PID <PID> /F
  
  # Linux
  lsof -i :5000
  kill -9 <PID>
  ```

### Serial Port Not Found

**Windows:**
- Check Device Manager for actual COM port
- Verify USB-to-serial driver installed
- Try different USB port on hub

**Linux:**
```bash
# Find device
ls /dev/tty*

# Check permissions
groups  # Should include 'dialout'
```

### Database Corruption

If `travelers.db` becomes unreadable:
```bash
# Backup corrupted DB
mv travelers.db travelers.db.corrupt

# Restart app (creates fresh DB)
python app.py
```

Restore from backup if needed:
```bash
cp travelers.db.corrupt travelers.db
# Use DB repair tools (sqlite3-tools)
```

---

## Performance Tuning

### Reduce Raw Log Size
Edit `traveler_state.py`:
```python
RAW_LOG_LIMIT = 100  # Default 200
```

### Archive Cleanup
For long-running SeedLink monitoring, clean old archives:
```bash
# Keep only last 90 days
find /data/SDS -mtime +90 -delete
```

### Database Index Optimization

```bash
sqlite3 travelers.db
> CREATE INDEX idx_serial ON snapshots(id);
> PRAGMA optimize;
```

---

## Monitoring & Alerts

### Health Check Script (Cron)

Create `check_gps_traveler.sh`:
```bash
#!/bin/bash
curl -s http://127.0.0.1:5000/api/status || echo "GPS Traveler DOWN" | mail -s "Alert" admin@example.com
```

Add to crontab:
```bash
*/5 * * * * /home/pi/check_gps_traveler.sh
```

### Logging

GPS Traveler logs to console. Redirect to file:
```bash
# Linux
nohup python app.py > gps_traveler.log 2>&1 &

# Windows (batch)
python app.py >> gps_traveler.log 2>&1
```

View logs:
```bash
tail -f gps_traveler.log
```

---

## Security Considerations

- **No authentication** on API (assume local network only)
- **HTTPS optional**: Use reverse proxy (nginx) in production
- **Database**: Keep backups in secure location
- **Serial access**: Restrict `/dev/ttyUSB0` permissions on Linux
- **Firewall**: Block external access to ports 5000 & 3000

### Production Setup (nginx reverse proxy)

```nginx
server {
    listen 80;
    server_name gps.internal.network;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
    }
}
```

---

**Last Updated:** 12 Mar 2026
