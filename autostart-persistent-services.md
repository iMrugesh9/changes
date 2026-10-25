# Autostart & 24/7 Persistence for Core Services (Recipe Helper, Workout Helper, Pi-hole)

**Date:** 2026-10-25  
**System:** Lenovo G500 (Linux Mint 22.3 "Xia" / MATE Desktop)  
**Kernel:** Linux 6.14.0-37-generic  
**User:** `dex`  
**Timezone:** Asia/Kolkata (IST, UTC +05:30)

---

## 1. Objectives & Motivation

The system is configured to perform an automated reboot every morning at 05:00:00 IST (see [`power-management-daily-reboot.md`](./power-management-daily-reboot.md)).

Prior to this change:
* The **Recipe Helper** server (Flask on port `8080`) and **Workout Helper** server (Flask on port `8081`) were started manually via desktop launchers or terminal scripts. When the machine rebooted at 5:00 AM, both servers stopped and remained offline until manually launched.
* **Pi-hole** had a container restart policy of `unless-stopped`, meaning if stopped or interrupted during reboot, it would not guarantee recovery without manual intervention.

**Goals:**
1. Ensure **Recipe Helper**, **Workout Helper**, and **Pi-hole** automatically start upon boot/reboot before and without requiring user graphical login.
2. Ensure all three services automatically restart if they crash or exit unexpectedly (`Restart=always`).
3. Harmonize the desktop GUI scripts (`manage_server.sh`) with systemd so clicking Start/Stop/Restart in desktop menus properly controls the underlying systemd services.

---

## 2. Architecture & How Persistence Works

Because **user lingering** is enabled for user `dex` (`loginctl enable-linger dex`):
* Systemd initializes the user manager (`user@1000.service`) immediately at kernel boot alongside system daemons.
* All enabled units in `~/.config/systemd/user/default.target.wants/` launch immediately at boot—even before graphical desktop or display manager login.
* Combined with Docker's native `restart: always` engine policy, services run with dual resilience.

---

## 3. Changes Applied

### A. Recipe Helper Service (`recipe-helper.service`)

Created systemd user unit at `/home/dex/.config/systemd/user/recipe-helper.service`:
```ini
[Unit]
Description=Recipe Helper Web Server & Local Agent
Documentation=file:///home/dex/projects/personal-ai/README.md
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/dex/projects/personal-ai
ExecStart=/home/dex/projects/personal-ai/.venv/bin/python /home/dex/projects/personal-ai/server.py
Restart=always
RestartSec=5s
Environment=PYTHONUNBUFFERED=1
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

* **Port**: `8080` (Local: `http://localhost:8080`, LAN: `http://192.168.1.9:8080`)
* **Auto-restart**: Restarts within 5 seconds if terminated.

### B. Workout Helper Service (`workout-helper.service`)

Created systemd user unit at `/home/dex/.config/systemd/user/workout-helper.service`:
```ini
[Unit]
Description=Workout Helper Web Server & Local API
Documentation=file:///home/dex/projects/workout/README.md
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/dex/projects/workout
ExecStart=/home/dex/projects/workout/.venv/bin/python /home/dex/projects/workout/server.py
Restart=always
RestartSec=5s
Environment=PYTHONUNBUFFERED=1
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

* **Port**: `8081` (Local: `http://localhost:8081`, LAN: `http://192.168.1.9:8081`)
* **Auto-restart**: Restarts within 5 seconds if terminated.

### C. Pi-hole Service & Docker Policy

1. **Updated Docker Container Restart Policy**:
   ```bash
   docker update --restart=always pihole
   ```
   Updated `restart: always` in `/home/dex/projects/homelab/pi-hole/docker-compose.yml`.

2. **Created Systemd User Unit (`pihole.service`)**:
   Created at `/home/dex/.config/systemd/user/pihole.service`:
   ```ini
   [Unit]
   Description=Pi-hole DNS Ad Blocker Docker Compose Service
   Documentation=file:///home/dex/projects/homelab/pi-hole/README.md
   After=network-online.target
   Wants=network-online.target

   [Service]
   Type=oneshot
   RemainAfterExit=yes
   WorkingDirectory=/home/dex/projects/homelab/pi-hole
   ExecStart=/usr/bin/docker compose up -d
   ExecStop=/usr/bin/docker compose stop
   Restart=on-failure
   RestartSec=10s

   [Install]
   WantedBy=default.target
   ```

### D. Desktop Script Harmonization

Updated the management scripts:
* `/home/dex/projects/workout/manage_server.sh`
* `/home/dex/projects/personal-ai/manage_server.sh`

Both scripts now integrate with `systemctl --user`:
* `start`: Calls `systemctl --user start <service>` if unit exists.
* `stop`: Calls `systemctl --user stop <service>` so systemd does not automatically restart the process when intentionally stopped.
* `restart`: Calls `systemctl --user restart <service>`.
* `status`: Retrieves the PID and health from systemd or process table.

### E. Activation Commands

```bash
systemctl --user daemon-reload
systemctl --user enable --now recipe-helper.service workout-helper.service pihole.service
```

---

## 4. Verification & Status Monitoring

* **Check Service Status**:
  ```bash
  systemctl --user status recipe-helper.service workout-helper.service pihole.service
  ```

* **Check HTTP Endpoints**:
  ```bash
  curl -sI http://127.0.0.1:8080 | head -n 1   # Recipe Helper (HTTP 200 OK)
  curl -sI http://127.0.0.1:8081 | head -n 1   # Workout Helper (HTTP 200 OK)
  curl -sI http://127.0.0.1:80/admin/ | head -n 1 # Pi-hole Admin (HTTP 302 Found)
  ```

* **Check Docker Status**:
  ```bash
  docker ps --filter name=pihole
  ```

* **Follow Live Logs**:
  ```bash
  journalctl --user -u recipe-helper.service -f
  journalctl --user -u workout-helper.service -f
  journalctl --user -u pihole.service -f
  ```

---

## 5. Rollback / Restoration Instructions

To disable automatic startup of these services on boot:

```bash
systemctl --user disable --now recipe-helper.service workout-helper.service pihole.service
rm -f ~/.config/systemd/user/recipe-helper.service
rm -f ~/.config/systemd/user/workout-helper.service
rm -f ~/.config/systemd/user/pihole.service
systemctl --user daemon-reload
```
