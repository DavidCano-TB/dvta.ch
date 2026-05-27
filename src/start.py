#!/usr/bin/env python3
"""
start.py — Launcher definitivo DVDcoin Bank
Uso: python start.py
Arranca main.py + ngrok y muestra la URL pública.
"""
import os, sys, time, subprocess, socket, urllib.request, json, signal, threading
from pathlib import Path

BASE = Path(__file__).parent.parent
GOLD = "\033[93m"; GREEN = "\033[92m"; RED = "\033[91m"; CYAN = "\033[96m"
DIM = "\033[2m"; RESET = "\033[0m"; BOLD = "\033[1m"

def ok(msg):  print(f"  {GREEN}✓{RESET}  {msg}")
def err(msg): print(f"  {RED}✗  {msg}{RESET}")
def info(msg):print(f"  {DIM}   {msg}{RESET}")
def step(msg):print(f"\n{GOLD}{BOLD}  {msg}{RESET}")

# ── Port helpers ────────────────────────────────────────────────────────────
def port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def kill_port(port: int):
    """Kill whatever is using the given port (Windows + Unix)."""
    if os.name == "nt":
        try:
            out = subprocess.check_output(
                f"netstat -aon | findstr \":{port} \"", shell=True, text=True
            )
            for line in out.splitlines():
                parts = line.split()
                if parts and parts[-1].isdigit():
                    pid = int(parts[-1])
                    if pid > 4:
                        subprocess.run(f"taskkill /PID {pid} /F", shell=True,
                                       capture_output=True)
        except Exception:
            pass
    else:
        try:
            subprocess.run(
                f"fuser -k {port}/tcp", shell=True, capture_output=True
            )
        except Exception:
            pass

def wait_for_server(port: int, timeout: int = 20) -> bool:
    """Wait until localhost:port responds or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if port_in_use(port):
            try:
                urllib.request.urlopen(f"http://localhost:{port}", timeout=2)
                return True
            except Exception:
                time.sleep(0.5)
                continue
        time.sleep(0.5)
    return False

# ── Read ngrok configuration ─────────────────────────────────────────────────
def get_ngrok_config() -> tuple:
    """Lee token y dominio desde conf/.ngrok_token
    Returns: (token, domain) tuple
    """
    token = ""
    domain = ""
    
    # Leer desde conf/.ngrok_token (ÚNICO ARCHIVO DE CONFIGURACIÓN)
    config_file = BASE / "conf" / ".ngrok_token"
    if config_file.exists():
        for line in config_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("NGROK_TOKEN="):
                token = line.split("=", 1)[1].strip()
            elif line.startswith("NGROK_DOMAIN="):
                domain = line.split("=", 1)[1].strip()
    
    # Fallback a variables de entorno si no se encontró en el archivo
    if not token:
        token = os.environ.get("NGROK_TOKEN", "")
    if not domain:
        domain = os.environ.get("NGROK_DOMAIN", "")
    
    return token, domain

# ── Get ngrok public URL via local API ───────────────────────────────────────
def get_ngrok_url(retries: int = 12) -> str:
    for _ in range(retries):
        try:
            data = json.loads(
                urllib.request.urlopen("http://localhost:4040/api/tunnels", timeout=2).read()
            )
            tunnels = data.get("tunnels", [])
            for t in tunnels:
                url = t.get("public_url", "")
                if url.startswith("https:"): return url
            if tunnels:
                return tunnels[0].get("public_url", "")
        except Exception:
            pass
        time.sleep(1)
    return ""

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        except Exception:
            pass
    
    print(f"""
{GOLD}{BOLD}
  ╔══════════════════════════════════════════════════╗
  ║       DVDcoin Bank — Launcher definitivo         ║
  ╚══════════════════════════════════════════════════╝
{RESET}""")

    procs = []  # track subprocesses for cleanup

    # ── 1. Check main.py exists ────────────────────────────────────────────
    if not (BASE / "main.py").exists():
        err("main.py no encontrado. Ejecuta desde la carpeta del proyecto.")
        sys.exit(1)

    # ── 2. Check deps ──────────────────────────────────────────────────────
    step("Verificando dependencias")
    try:
        import fastapi, uvicorn
        ok("fastapi + uvicorn OK")
    except ImportError:
        info("Instalando dependencias...")
        req_file = BASE / "requirements.txt"
        cmd = [sys.executable, "-m", "pip", "install",
               "-r", str(req_file) if req_file.exists() else "fastapi uvicorn[standard] python-jose bcrypt python-multipart slowapi",
               "--quiet"]
        r = subprocess.run(cmd)
        if r.returncode != 0:
            err("No se pudieron instalar las dependencias. Ejecuta: pip install -r requirements.txt")
            sys.exit(1)
        ok("Dependencias instaladas")

    # ── 3. Free port 8000 ──────────────────────────────────────────────────
    step("Preparando puerto 8000")
    if port_in_use(8000):
        info("Puerto 8000 ocupado, liberando...")
        kill_port(8000)
        time.sleep(1.5)
        if port_in_use(8000):
            err("No se pudo liberar el puerto 8000. Cierra otros procesos que lo usen.")
            sys.exit(1)
    ok("Puerto 8000 libre")

    # ── 4. Start server ────────────────────────────────────────────────────
    step("Arrancando servidor DVDcoin")
    log_file = open(BASE / "server.log", "w", encoding="utf-8")
    server_proc = subprocess.Popen(
        [sys.executable, str(BASE / "main.py")],  # Usar main.py en la raíz, no src/main.py
        stdout=log_file, stderr=log_file,
        cwd=str(BASE)
    )
    procs.append(server_proc)
    info("Esperando respuesta del servidor...")

    if not wait_for_server(8000, timeout=25):
        err("El servidor no arrancó en 25 segundos.")
        print(f"\n  {DIM}Últimas líneas de server.log:{RESET}")
        log_file.flush()
        try:
            lines = (BASE / "server.log").read_text(encoding="utf-8", errors="replace").splitlines()
            for l in lines[-15:]: print(f"    {l}")
        except Exception: pass
        print()
        server_proc.terminate()
        sys.exit(1)

    ok(f"Servidor activo en {CYAN}http://localhost:8000{RESET}")

    # ── 5. ngrok ───────────────────────────────────────────────────────────
    step("Configurando ngrok")
    token, domain = get_ngrok_config()
    if not token:
        info("Sin token ngrok — solo acceso local.")
        info(f"Para ngrok: guarda tu configuración en {BASE}/conf/.ngrok_token")
        info("Formato del archivo:")
        info("  NGROK_TOKEN=tu_token_aqui")
        info("  NGROK_DOMAIN=tu_dominio.ngrok-free.dev")
        print(f"\n{GOLD}{BOLD}  ► Abre: http://localhost:8000{RESET}\n")
        _open_browser("http://localhost:8000")
        _wait_signal(procs, log_file)
        return

    # Check ngrok binary
    ngrok_cmd = str(BASE / "ngrok.exe")  # Usar ngrok.exe en la carpeta del proyecto
    if not Path(ngrok_cmd).exists():
        # Try system ngrok
        try:
            subprocess.run(["ngrok", "version"], capture_output=True, check=True, timeout=5)
            ngrok_cmd = "ngrok"
            ok("ngrok encontrado en PATH")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            # Try common locations on Windows
            candidates = [
                Path(os.environ.get("USERPROFILE","")) / "ngrok" / "ngrok.exe",
                Path("C:/ngrok/ngrok.exe"),
            ]
            found = next((str(c) for c in candidates if c.exists()), None)
            if found:
                ngrok_cmd = found
                ok(f"ngrok en {found}")
            else:
                info("ngrok no encontrado. Descarga: https://ngrok.com/download")
                info("Descomprime ngrok.exe en la carpeta del proyecto.")
                print(f"\n{GOLD}{BOLD}  ► Acceso local: http://localhost:8000{RESET}\n")
                _open_browser("http://localhost:8000")
                _wait_signal(procs, log_file)
                return
    else:
        ok(f"ngrok encontrado: {ngrok_cmd}")

    # Configure auth token (skip if permission denied - token may already be configured)
    try:
        subprocess.run([ngrok_cmd, "config", "add-authtoken", token], 
                      capture_output=True, check=True, timeout=10)
        ok("Token de ngrok configurado")
    except (subprocess.CalledProcessError, PermissionError, subprocess.TimeoutExpired) as e:
        info(f"No se pudo configurar token (puede estar ya configurado): {type(e).__name__}")
        # Continue anyway - token may already be configured

    # Start ngrok with reserved domain (fallback to random if fails)
    import uuid
    ngrok_log_path = BASE / f"ngrok_{uuid.uuid4().hex[:8]}.log"
    ngrok_log = open(ngrok_log_path, "w", encoding="utf-8")
    
    # Try with reserved domain first (if configured)
    if domain:
        info(f"Usando dominio reservado: {domain}")
        try:
            ngrok_proc = subprocess.Popen(
                [ngrok_cmd, "http", "8000",
                 f"--domain={domain}",
                 "--log=stdout",
                 "--log-level=warn"],
                stdout=ngrok_log, stderr=ngrok_log
            )
            procs.append(ngrok_proc)
            info("Intentando conectar con dominio reservado...")
            time.sleep(3)
            
            # Check if ngrok started successfully
            if ngrok_proc.poll() is not None:
                # Process died, try without domain
                info("Dominio reservado no disponible, usando URL aleatoria...")
                ngrok_log.close()
                ngrok_log_path = BASE / f"ngrok_{uuid.uuid4().hex[:8]}.log"
                ngrok_log = open(ngrok_log_path, "w", encoding="utf-8")
                ngrok_proc = subprocess.Popen(
                    [ngrok_cmd, "http", "8000",
                     "--log=stdout",
                     "--log-level=warn"],
                    stdout=ngrok_log, stderr=ngrok_log
                )
                procs.append(ngrok_proc)
        except Exception as e:
            info(f"Error con dominio reservado: {e}")
            info("Usando URL aleatoria...")
            ngrok_proc = subprocess.Popen(
                [ngrok_cmd, "http", "8000",
                 "--log=stdout",
                 "--log-level=warn"],
                stdout=ngrok_log, stderr=ngrok_log
            )
            procs.append(ngrok_proc)
    else:
        # No domain configured, use random URL
        info("Sin dominio reservado, usando URL aleatoria...")
        ngrok_proc = subprocess.Popen(
            [ngrok_cmd, "http", "8000",
             "--log=stdout",
             "--log-level=warn"],
            stdout=ngrok_log, stderr=ngrok_log
        )
        procs.append(ngrok_proc)

    info("Esperando URL pública de ngrok...")
    public_url = get_ngrok_url(retries=15)

    print(f"""
{GOLD}{BOLD}  ╔══════════════════════════════════════════════════╗
  ║         ✓  DVDcoin Bank — ACTIVO                 ║
  ╚══════════════════════════════════════════════════╝{RESET}

  {BOLD}URL PÚBLICA:  {CYAN}{public_url or '(ver ngrok.log)'}  {RESET}
  {DIM}LOCAL:        http://localhost:8000{RESET}

  {DIM}Logs: server.log | ngrok.log{RESET}
  {DIM}Ctrl+C para detener todo.{RESET}
""")

    if public_url:
        _open_browser(public_url)

    _wait_signal(procs, log_file)


def _open_browser(url: str):
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception:
        pass


def _wait_signal(procs, log_file):
    """Wait for Ctrl+C or process death, then clean up."""
    def cleanup(*_):
        print(f"\n\n  {GOLD}Deteniendo...{RESET}")
        for p in procs:
            try: p.terminate()
            except Exception: pass
        try: log_file.close()
        except Exception: pass
        print(f"  {GREEN}✓ Servidor detenido.{RESET}\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # Monitor server process
    while True:
        time.sleep(3)
        for p in procs:
            if p.poll() is not None:
                print(f"\n  {RED}Proceso caído (exit {p.returncode}). Revisando log...{RESET}")
                try:
                    lines = Path("server.log").read_text(errors="replace").splitlines()
                    for l in lines[-10:]: print(f"    {l}")
                except Exception: pass
                cleanup()


if __name__ == "__main__":
    main()
