"""Watchdog: keeps app_exams.py running. Restarts on crash."""
import subprocess, sys, os, time, logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("watchdog")

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_exams.py")

while True:
    logger.info("Starting app_exams.py...")
    proc = subprocess.Popen([sys.executable, SCRIPT], cwd=os.path.dirname(SCRIPT))
    proc.wait()
    code = proc.returncode
    logger.warning(f"app_exams.py exited with code {code}. Restarting in 3s...")
    time.sleep(3)
