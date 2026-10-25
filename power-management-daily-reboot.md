# Power Management & Daily Reboot Setup

**Date:** 2026-10-24  
**System:** Lenovo G500 (Linux Mint 22.3 "Xia" / MATE Desktop)  
**Kernel:** Linux 6.14.0-37-generic  
**User:** `dex`  
**Timezone:** Asia/Kolkata (IST, UTC +05:30)

---

## 1. Objectives

1. **Keep Laptop Active 24/7**: Ensure the laptop never enters sleep, suspend, or hibernation modes when idle or when the laptop lid is closed.
2. **Automated Daily Reboot at 5:00 AM**: Ensure all system processes restart cleanly every day at 05:00:00 IST.

---

## 2. Changes Applied

### A. Sleep, Suspend, and Hibernate Prevention

1. **Masked Systemd Sleep Targets**:
   Prevented the kernel and systemd from entering any power-saving sleep states:
   ```bash
   systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
   ```
   *Result:* Symlinks created pointing `/etc/systemd/system/*.target` to `/dev/null`. Any API call or event attempting to suspend or hibernate is rejected with `Access denied`.

2. **Configured MATE Power Manager**:
   Disabled sleep and suspend actions on lid switch and power/sleep buttons:
   ```bash
   gsettings set org.mate.power-manager button-lid-ac 'nothing'
   gsettings set org.mate.power-manager button-lid-battery 'nothing'
   gsettings set org.mate.power-manager button-suspend 'nothing'
   gsettings set org.mate.power-manager button-hibernate 'nothing'
   ```

3. **Enabled User Lingering**:
   Ensures user session services and timers stay active across logouts, restarts, or before graphical logins:
   ```bash
   loginctl enable-linger dex
   ```

### B. Daily 5:00 AM Restart Setup

Created a systemd user service and timer:

1. **Service File**: `/home/dex/.config/systemd/user/daily-reboot.service`
   ```ini
   [Unit]
   Description=Daily 5 AM System Reboot
   Documentation=man:systemctl(1)

   [Service]
   Type=oneshot
   ExecStart=/usr/bin/systemctl reboot
   ```

2. **Timer File**: `/home/dex/.config/systemd/user/daily-reboot.timer`
   ```ini
   [Unit]
   Description=Daily 5 AM System Reboot Timer
   Documentation=man:systemd.timer(5)

   [Timer]
   OnCalendar=*-*-* 05:00:00
   Persistent=false

   [Install]
   WantedBy=timers.target
   ```

3. **Activated the Timer**:
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable --now daily-reboot.timer
   ```
   *Verified trigger:* Scheduled for `05:00:00 IST` every day.

---

## 3. Useful Commands & Monitoring

* **Check reboot timer status**:
  ```bash
  systemctl --user list-timers daily-reboot.timer
  systemctl --user status daily-reboot.timer
  ```

* **Check masked targets status**:
  ```bash
  systemctl status sleep.target suspend.target hibernate.target hybrid-sleep.target
  ```

* **Verify lingering**:
  ```bash
  loginctl show-user dex | grep Linger
  ```

---

## 4. Optional Further Hardening (Root-level Lid Switch Ignore)

To have `systemd-logind` ignore lid switches directly at the daemon level (regardless of desktop environment status), run:

```bash
sudo mkdir -p /etc/systemd/logind.conf.d
sudo bash -c 'cat <<EOF > /etc/systemd/logind.conf.d/ignore-lid-switch.conf
[Login]
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
EOF'
sudo systemctl restart systemd-logind
```

---

## 5. Rollback / Restoration Instructions

To revert these changes in the future:

1. **Disable the daily reboot timer**:
   ```bash
   systemctl --user disable --now daily-reboot.timer
   rm ~/.config/systemd/user/daily-reboot.timer ~/.config/systemd/user/daily-reboot.service
   systemctl --user daemon-reload
   ```

2. **Unmask sleep targets**:
   ```bash
   systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target
   ```

3. **Reset MATE power management settings**:
   ```bash
   gsettings reset org.mate.power-manager button-lid-ac
   gsettings reset org.mate.power-manager button-lid-battery
   gsettings reset org.mate.power-manager button-suspend
   gsettings reset org.mate.power-manager button-hibernate
   ```
