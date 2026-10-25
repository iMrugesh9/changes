# Linux System Changes & Configuration Documentation

This repository maintains an organized, version-controlled record of all system configuration changes, service automations, hardware adjustments, and administrative tweaks made to this Linux workstation.

---

## 🖥️ Machine Profile

| Property | Value |
| :--- | :--- |
| **Hardware** | Lenovo G500 |
| **Operating System** | Linux Mint 22.3 "Xia" / MATE Desktop Environment |
| **Display Server** | X11 / Marco Window Manager |
| **Primary User** | `dex` |
| **Timezone** | Asia/Kolkata (`IST`, `UTC +05:30`) |

---

## 📚 Documented System Changes

| Document | Category | Summary |
| :--- | :--- | :--- |
| [**`power-management-daily-reboot.md`**](./power-management-daily-reboot.md) | Power & Automation | Laptop 24/7 uptime setup: masked sleep/suspend/hibernate targets, MATE lid-switch handlers, user lingering, and daily 05:00 AM systemd reboot timer. |
| [**`multi-monitor-panel-setup.md`**](./multi-monitor-panel-setup.md) | Desktop & Display | Dual-monitor configuration (`LVDS-1` + `HDMI-1`) with independent MATE panels, custom applets/launchers, and multi-monitor window management. |

---

## ✍️ Contribution & Documentation Standard

When introducing a new system modification, create a new Markdown file adhering to the naming standard `{change-name}.md`:

### File Naming Convention
* Use descriptive, kebab-case names: `{change-name}.md` (e.g., `docker-rootless-setup.md`, `custom-audio-profile.md`).

### Recommended Document Template
Every change document should follow this consistent structure:
```markdown
# <Feature / Change Title>

**Date:** YYYY-MM-DD  
**System:** Linux Mint 22.3 MATE  
**User:** dex  

---

## 1. Objectives & Motivation
* What problem was solved or what capability was enabled?
* What are the specific goals?

## 2. Changes Applied
* Step-by-step breakdown of actions taken.
* Include configuration files, exact CLI commands, and dconf/gsettings paths.

## 3. Verification & Monitoring
* Commands to verify the service, timer, or configuration status.

## 4. Rollback / Restoration Instructions
* Exact steps to cleanly revert the changes if needed.
```

---

## 🔄 Automatic Git Synchronization

This directory is monitored by a lightweight background file watcher (`changes-sync.py`) configured as a systemd user service (`changes-git-sync.service`).

* **Trigger**: Any new `{change}.md` file creation or edit in this folder automatically triggers git commit and push.
* **Debounce**: A short 3-second debounce window ensures bulk writes and edits finish cleanly before committing.
* **Manual Sync**: You can also run the helper script at any time:
  ```bash
  ./sync.sh
  ```
* **Service Management**:
  ```bash
  systemctl --user status changes-git-sync.service   # View watcher status
  systemctl --user restart changes-git-sync.service  # Restart watcher
  journalctl --user -u changes-git-sync.service -f   # Follow real-time logs
  ```
