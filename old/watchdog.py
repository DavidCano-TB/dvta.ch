"""
DVDcoin Bank — Watchdog
Checks every 10 minutes that the server responds on http://localhost:8000
If it fails twice in a row, kills any existing process on port 8000
and relaunches main.py.

Run this in the background (started by START_DVDCOIN.bat).
"""

import subprocess
import sys
import time
import os
import urllib.request
import urllib.error
import signal
import logging

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
SERVER_SCRIPT = os.path.join(BASE_DIR, "main.py")
CHECK_URL     = "http://localhost:8000/"
CHECK_EVERY   = 600        # seconds between checks (10 minutes)
FAIL_LIMIT    = 2          # consecutive failures before restart
TIMEOUT       = 10         # HTTP timeout in seconds
LOG_FILE      = os.path.join(BASE_DIR, "watchdog.log")
PID_FILE      = os.path.join(BASE_DIR, "watchdog.pid")

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WATCHDOG] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("watchdog")

# ── State ─────────────────────────────────────────────────────────────────────
_server_proc = None   # current subprocess handle
_failures    = 0

# ── Helpers ───────────────────────────────────────────────────────────────────

def is_alive(proc):
    """Return True if the subprocess is still running."""
    return proc is not None and proc.poll() is None


def check_http():
    """Return True if the server responds with HTTP 200."""
    try:
        req = urllib.request.urlopen(CHECK_URL, timeout=TIMEOUT)
        return req.status == 200
    except Exception:
        return False


def kill_port_8000():
    """Kill whatever is listening on port 8000 (Windows netstat + taskkill)."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if ":8000" in line and "LISTENING" in line:
                parts = line.split()
                pid = parts[-1]
                if pid.isdigit():
                    log.info("Killing PID %s on port 8000", pid)
                    subprocess.run(["taskkill", "/F", "/PID", pid],
                                   capture_output=True)
    except Exception as e:
        log.warning("kill_port_8000 error: %s", e)


def start_server():
    """Launch main.py as a detached subprocess."""
    global _server_proc
    kill_port_8000()
    time.sleep(2)
    log.info("Starting server: python %s", SERVER_SCRIPT)
    _server_proc = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT],
        cwd=BASE_DIR,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        if sys.platform == "win32" else 0,
    )
    log.info("Server PID: %s", _server_proc.pid)
    # Give it time to boot
    time.sleep(5)


def write_own_pid():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    global _failures

    write_own_pid()
    log.info("Watchdog started (PID %s). Checks every %ds.", os.getpid(), CHECK_EVERY)

    # Start server immediately on launch
    start_server()

    while True:
        time.sleep(CHECK_EVERY)

        # If the process died on its own, restart immediately
        if not is_alive(_server_proc):
            log.warning("Server process died unexpectedly — restarting.")
            _failures = 0
            start_server()
            continue

        # HTTP health check
        ok = check_http()
        if ok:
            if _failures > 0:
                log.info("Server healthy again (was %d failures).", _failures)
            else:
                log.info("Health check OK.")
            _failures = 0
        else:
            _failures += 1
            log.warning("Health check FAILED (%d/%d).", _failures, FAIL_LIMIT)
            if _failures >= FAIL_LIMIT:
                log.error("Failure limit reached — restarting server.")
                _failures = 0
                # Kill and restart
                try:
                    if is_alive(_server_proc):
                        _server_proc.terminate()
                        _server_proc.wait(timeout=5)
                except Exception:
                    pass
                start_server()


if __name__ == "__main__":
    main()
