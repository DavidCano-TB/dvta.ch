"""
service_launcher.py — Launcher silencioso para el servicio Windows DVDcoinBank
Arranca main.py + ngrok sin ventana, sin interacción, con logs a archivo.
"""
import os, sys, time, subprocess, socket, urllib.request, json, signal
from pathlib import Path

BASE    = Path(__file__).parent
PYTHON  = sys.executable
LOG     = BASE / "server.log"
NGROK_LOG = BASE / "ngrok.log"

def port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0

def kill_port(port):
    try:
        out = subprocess.check_output(
            f'netstat -aon | findstr ":{port} "', shell=True, text=True, errors="ignore"
        )
        for line in out.splitlines():
            parts = line.split()
            if parts and parts[-1].isdigit():
                pid = int(parts[-1])
                if pid > 4:
                    subprocess.run(f"taskkill /PID {pid} /F", shell=True, capture_output=True)
    except Exception:
        pass

def get_ngrok_token():
    for p in [BASE/"conf"/".ngrok_token", BASE/"conf"/"deploy.env"]:
        if p.exists():
            txt = p.read_text(encoding="utf-8", errors="ignore").strip()
            if p.name == ".ngrok_token" and txt:
                return txt
            for line in txt.splitlines():
                if line.startswith("NGROK_TOKEN="):
                    return line.split("=",1)[1].strip().strip('"')
    return os.environ.get("NGROK_TOKEN", "")

def find_ngrok():
    for candidate in [
        BASE / "ngrok.exe",
        Path(os.environ.get("USERPROFILE","")) / "ngrok" / "ngrok.exe",
        Path("C:/ngrok/ngrok.exe"),
    ]:
        if candidate.exists():
            return str(candidate)
    try:
        subprocess.run(["ngrok", "version"], capture_output=True, check=True)
        return "ngrok"
    except Exception:
        return None

def wait_server(timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen("http://localhost:8000/api/health", timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False

def main():
    log = open(LOG, "w", encoding="utf-8", buffering=1)

    def log_write(msg):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg}\n"
        log.write(line)
        log.flush()

    log_write("=== DVDcoin service_launcher starting ===")

    # Kill anything on port 8000
    if not port_free(8000):
        log_write("Port 8000 busy, killing...")
        kill_port(8000)
        time.sleep(2)

    # Start main.py
    log_write(f"Starting main.py with {PYTHON}")
    server = subprocess.Popen(
        [PYTHON, str(BASE / "main.py")],
        stdout=log, stderr=log,
        cwd=str(BASE),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform=="win32" else 0,
    )
    log_write(f"Server PID: {server.pid}")

    # Wait for server
    if not wait_server(30):
        log_write("ERROR: Server did not start in 30s")
        server.terminate()
        sys.exit(1)
    log_write("Server OK at http://localhost:8000")

    # Start ngrok
    token = get_ngrok_token()
    ngrok_bin = find_ngrok()
    ngrok_proc = None

    if token and ngrok_bin:
        log_write(f"Starting ngrok with {ngrok_bin}")
        # Configure token
        subprocess.run([ngrok_bin, "config", "add-authtoken", token], capture_output=True)
        # Kill any existing ngrok
        subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"], capture_output=True)
        time.sleep(1)
        ngrok_log_f = open(NGROK_LOG, "w", encoding="utf-8")
        ngrok_proc = subprocess.Popen(
            [ngrok_bin, "http", "8000", "--log=stdout", "--log-level=warn"],
            stdout=ngrok_log_f, stderr=ngrok_log_f,
        )
        log_write(f"ngrok PID: {ngrok_proc.pid}")
        # Wait for URL
        time.sleep(5)
        try:
            data = json.loads(urllib.request.urlopen("http://localhost:4040/api/tunnels", timeout=5).read())
            for t in data.get("tunnels", []):
                url = t.get("public_url","")
                if url.startswith("https:"):
                    log_write(f"ngrok URL: {url}")
                    break
        except Exception as e:
            log_write(f"ngrok URL check: {e}")
    else:
        log_write("ngrok not configured (no token or binary) — local only")

    log_write("Launcher ready. Monitoring...")

    # Monitor loop — restart server if it dies
    def cleanup(*_):
        log_write("Shutdown signal received")
        if ngrok_proc:
            try: ngrok_proc.terminate()
            except: pass
        try: server.terminate()
        except: pass
        log.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    while True:
        time.sleep(10)
        if server.poll() is not None:
            log_write(f"Server died (exit {server.returncode}), restarting...")
            kill_port(8000)
            time.sleep(2)
            server = subprocess.Popen(
                [PYTHON, str(BASE / "main.py")],
                stdout=log, stderr=log,
                cwd=str(BASE),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform=="win32" else 0,
            )
            log_write(f"Server restarted PID: {server.pid}")

if __name__ == "__main__":
    main()
