#!/usr/bin/env python3
"""
Daemon that watches /home/dex/changes for .md file creations and modifications,
and automatically synchronizes changes to Git.
"""

import ctypes
import os
import select
import signal
import struct
import subprocess
import sys
import time

WATCH_DIR = "/home/dex/changes"
SYNC_SCRIPT = os.path.join(WATCH_DIR, "sync.sh")
DEBOUNCE_SECONDS = 3.0

# inotify mask constants
IN_CLOSE_WRITE = 0x00000008
IN_MOVED_TO = 0x00000080
IN_CREATE = 0x00000100
IN_DELETE = 0x00000200
IN_MOVED_FROM = 0x00000040

EVENT_MASK = IN_CLOSE_WRITE | IN_MOVED_TO | IN_CREATE | IN_DELETE | IN_MOVED_FROM
EVENT_STRUCT_FMT = "iIII"
EVENT_STRUCT_SIZE = struct.calcsize(EVENT_STRUCT_FMT)

running = True

def handle_signal(sig, frame):
    global running
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Received signal {sig}, stopping watcher...", flush=True)
    running = False

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

def run_sync():
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Triggering sync...", flush=True)
        res = subprocess.run([SYNC_SCRIPT], capture_output=True, text=True, check=False)
        if res.stdout:
            print(res.stdout.strip(), flush=True)
        if res.stderr:
            print(res.stderr.strip(), file=sys.stderr, flush=True)
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error during sync: {e}", file=sys.stderr, flush=True)

def main():
    libc = ctypes.CDLL("libc.so.6")
    fd = libc.inotify_init()
    if fd < 0:
        print("Failed to initialize inotify", file=sys.stderr, flush=True)
        sys.exit(1)

    wd = libc.inotify_add_watch(fd, WATCH_DIR.encode("utf-8"), EVENT_MASK)
    if wd < 0:
        print(f"Failed to add inotify watch on {WATCH_DIR}", file=sys.stderr, flush=True)
        os.close(fd)
        sys.exit(1)

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Monitoring {WATCH_DIR} for Markdown changes...", flush=True)
    
    poll = select.poll()
    poll.register(fd, select.POLLIN)

    pending_sync = False
    last_event_time = 0.0

    while running:
        timeout_ms = 1000  # 1 second poll
        events = poll.poll(timeout_ms)

        now = time.time()
        for pfd, evt in events:
            if evt & select.POLLIN:
                try:
                    data = os.read(fd, 4096)
                except OSError:
                    continue
                offset = 0
                while offset + EVENT_STRUCT_SIZE <= len(data):
                    wd_e, mask, cookie, length = struct.unpack_from(EVENT_STRUCT_FMT, data, offset)
                    offset += EVENT_STRUCT_SIZE
                    name = ""
                    if length > 0:
                        name_bytes = data[offset : offset + length]
                        name = name_bytes.split(b"\x00", 1)[0].decode("utf-8", errors="replace")
                        offset += length
                    
                    if name.endswith(".md") and not name.startswith("."):
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Detected change in: {name}", flush=True)
                        pending_sync = True
                        last_event_time = now

        if pending_sync and (time.time() - last_event_time >= DEBOUNCE_SECONDS):
            pending_sync = False
            run_sync()

    try:
        os.close(fd)
    except OSError:
        pass
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Watcher stopped cleanly.", flush=True)

if __name__ == "__main__":
    main()
