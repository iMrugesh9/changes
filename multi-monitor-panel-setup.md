# Extended Display & Multi-Monitor Panel Setup Context

**Date:** 2026-10-24  
**System:** Linux Mint 22.3 (Zena) / MATE Desktop  
**Display Server:** X11  
**Window Manager:** Marco  
**User:** `dex`  
**Timezone:** Asia/Kolkata (IST, UTC +05:30)

---

## 1. Context & Objectives

* **Initial Setup & Problem:**
  * The user has a laptop with an extended external monitor attached (`HDMI-1` alongside `LVDS-1`).
  * Only a single panel existed on the laptop screen. Whenever applications were launched, their windows opened on the laptop screen, and their taskbar icons/tabs appeared exclusively on the laptop screen's panel—even when the user was working primarily on the extended display.
* **Goals:**
  1. Have a full panel on the extended display featuring all the same core tools and options (Mint Menu, quick launchers, window list/taskbar, clock, desktop toggle).
  2. Ensure applications launched on a specific screen open on that screen.
  3. Understand and configure window list/taskbar behavior across multiple monitors.
  4. Enable hotkeys for shifting active windows between displays seamlessly.

---

## 2. Display Hardware Geometry

Detected via `xrandr --listmonitors`:
* **Monitor 0 (`LVDS-1`):** Laptop built-in display — 1366×768 at `+0+0` (Primary)
* **Monitor 1 (`HDMI-1`):** External display — 1920×1080 at `+1366+0` (Extended)

---

## 3. Changes Applied

### A. Extended Display Panel Creation (`bottom-ext`)
Created a dedicated toplevel panel docked to the bottom edge of `HDMI-1` (`monitor=1`) with the following applets and launchers configured via `dconf`:

| Object ID | Type / Applet IID | Purpose / Target |
| :--- | :--- | :--- |
| `menu-bar-ext` | `MintMenuAppletFactory::MintMenuApplet` | Linux Mint application menu on the extended monitor |
| `show-desktop-ext` | `WnckletFactory::ShowDesktopApplet` | Minimize all windows / reveal desktop |
| `launcher-firefox-ext` | Launcher | Firefox (`/usr/share/applications/firefox.desktop`) |
| `launcher-terminal-ext` | Launcher | MATE Terminal (`/usr/share/applications/mate-terminal.desktop`) |
| `launcher-caja-ext` | Launcher | Caja File Manager (`/usr/share/applications/caja-browser.desktop`) |
| `window-list-ext` | `WnckletFactory::WindowListApplet` | Window list taskbar for managing active windows |
| `clock-ext` | `ClockAppletFactory::ClockApplet` | Right-aligned 24-hour clock |

*Note: In the X11 protocol, the Notification Area / System Tray is restricted by specification (XEmbed / StatusNotifier) to a single instance across the desktop session, so it remains hosted on the primary laptop panel.*

### B. Pointer-Based Window Placement
Updated Marco window manager placement mode to follow cursor position:
```bash
gsettings set org.mate.Marco.general placement-mode 'pointer'
gsettings set org.mate.Marco.general center-new-windows false
```
*Effect:* New windows now open on whichever display the mouse pointer currently resides on, preventing them from always defaulting to the center of the laptop display.

### C. Multi-Monitor Window Shift Shortcuts
Enabled keybindings in Marco to move windows between displays using the keyboard:
```bash
gsettings set org.mate.Marco.window-keybindings move-to-monitor-e '<Super><Shift>Right'
gsettings set org.mate.Marco.window-keybindings move-to-monitor-w '<Super><Shift>Left'
```
* Shortcuts:
  * <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>→</kbd>: Move active window to Extended Display (`HDMI-1`)
  * <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>←</kbd>: Move active window to Laptop Display (`LVDS-1`)

---

## 4. Multi-Monitor Architecture & Taskbar Isolation Notes

* **MATE Native Behavior:** The standard MATE Window List applet is powered by `libwnck`. `libwnck` manages tasks on a per-*workspace* level rather than per-*physical monitor*. As a result, both panels show running applications from the current workspace, allowing window switching from either display.
* **Strict Taskbar Isolation Alternatives:** If the user requires strict taskbar button isolation (so an application's tab appears *exclusively* on the monitor where its window is rendered):
  1. **Linux Mint Cinnamon:** Linux Mint's flagship Cinnamon edition natively supports per-monitor panel isolation in the GUI (Right-click panel → *Grouped Window List* settings → toggle off *"Show windows from all monitors"*). Can be installed alongside MATE via `sudo apt install cinnamon`.
  2. **Tint2:** A lightweight, standalone panel capable of running alongside MATE with `taskbar_hide_different_monitor = 1`.

---

## 5. Inspection & Verification Commands

* **Check active panel windows and positions:**
  ```bash
  python3 -c "
  import gi; gi.require_version('Wnck', '3.0'); from gi.repository import Wnck
  s = Wnck.Screen.get_default(); s.force_update()
  for w in s.get_windows():
      if 'Panel' in w.get_name(): print(w.get_name(), w.get_geometry())
  "
  ```

* **Inspect current MATE panel dconf configuration:**
  ```bash
  dconf dump /org/mate/panel/
  ```

* **Inspect Marco window placement settings:**
  ```bash
  gsettings get org.mate.Marco.general placement-mode
  gsettings get org.mate.Marco.general center-new-windows
  ```

* **Inspect monitor move shortcuts:**
  ```bash
  gsettings get org.mate.Marco.window-keybindings move-to-monitor-e
  gsettings get org.mate.Marco.window-keybindings move-to-monitor-w
  ```

---

## 6. Rollback / Restoration Instructions

To revert these changes and return to the single-panel laptop setup:

1. **Remove the extended panel and its objects:**
   ```bash
   dconf write /org/mate/panel/general/toplevel-id-list "['bottom']"
   dconf write /org/mate/panel/general/object-id-list "['menu-bar', 'show-desktop', 'separator', 'launcher-firefox', 'launcher-terminal', 'launcher-caja', 'window-list', 'notification-area', 'xapp-status', 'clock', 'object-0']"
   dconf reset -f /org/mate/panel/toplevels/bottom-ext/
   dconf reset -f /org/mate/panel/objects/menu-bar-ext/
   dconf reset -f /org/mate/panel/objects/show-desktop-ext/
   dconf reset -f /org/mate/panel/objects/launcher-firefox-ext/
   dconf reset -f /org/mate/panel/objects/launcher-terminal-ext/
   dconf reset -f /org/mate/panel/objects/launcher-caja-ext/
   dconf reset -f /org/mate/panel/objects/window-list-ext/
   dconf reset -f /org/mate/panel/objects/clock-ext/
   ```

2. **Reset Marco placement and keybinding settings:**
   ```bash
   gsettings reset org.mate.Marco.general placement-mode
   gsettings reset org.mate.Marco.general center-new-windows
   gsettings reset org.mate.Marco.window-keybindings move-to-monitor-e
   gsettings reset org.mate.Marco.window-keybindings move-to-monitor-w
   ```
