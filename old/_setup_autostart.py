"""
DVDcoin Bank — Setup autostart + cleanup
Ejecutar como Administrador para que la tarea programada funcione.
"""
import os, sys, subprocess, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

# ── Archivos a borrar ─────────────────────────────────────────────────────────
JUNK = [
    "_audit.py","_check_final.py","_check_injected_script.py","_check_injection.py",
    "_check_rooms.py","_check_served.py","_check.py","_check2.py","_check3.py",
    "_chk_video.py","_chk3.py","_chk4.py","_deep_audit.py","_diag_full.py",
    "_diag_rooms.py","_diag.py","_diag2.py","_do_restart.ps1","_final_audit.py",
    "_final_test.py","_final_verify.py","_final.py","_find_js_error.py",
    "_find_login_bug.py","_find_real_error.py","_fix_messaging.py",
    "_kill_restart.bat","_member_test.py","_restart_main2.bat","_restart.py",
    "_rooms_diag.py","_s6.txt","_syntax_check.py","_test_create_room.py",
    "_test_room.py","_test_rooms_live.py","_test_ws_room.py","_ver.py",
    "_verify_all.py","_verify_db.py","_version_check.py",
    "test_local_video.html","test_video_login.html","test_video_system.py",
    "test_webrtc_simple.html","test_websocket.html",
    "CRITICAL_FIXES_APPLIED.md","DIAGNOSTICO_USUARIO.md","FIX_NGROK_DEFINITIVO.bat",
    "FIX_NGROK.bat","FIX_TODO.bat","IMPLEMENTATION_CHECKLIST.md",
    "IMPLEMENTATION_SUMMARY.md","INFRASTRUCTURE_DIAGNOSIS.md","INSTALL_WATCHDOG.bat",
    "INSTRUCCIONES_FINALES.md","JITSI_VIDEO_DISPLAY_FIX.md","NO_SLEEP_UNINSTALL.bat",
    "NO_SLEEP.bat","no_sleep.log","nunca-apagar.cmd","probar_ngrok_simple.bat",
    "README_CHANGES.md","reiniciar_todo.ps1","REINICIAR.bat","RESTART_APP.bat",
    "RESTART_NGROK.bat","RESTORE_SLEEP.bat","RESUMEN_ARREGLOS.md",
    "server_main2.log","SETUP.bat","SOLUCION_DEFINITIVA.bat","START_DVDCOIN.bat",
    "start_ngrok.bat","STATUS.bat","STOP_DVDCOIN.bat","TASK_COMPLETION_REPORT.md",
    "TESTING_GUIDE.md","UNINSTALL.bat","USAR_LOCALHOST_RUN.bat","USAR_SERVEO.bat",
    "VERIFY.bat","VIDEO_SYSTEM_FIX.md","WEBRTC_P2P_SOLUTION.md",
    "TEST_VIDEO_NOW.md","watchdog.pid","ngrok.zip",
    "crear_config_ngrok.bat","desactivar_dvdch.bat","activar_dvdch.bat",
    "dvdcoin_bank_windows.bat","DIAGNOSTICO.bat","reiniciar_todo.bat","RESTART.bat",
    "main_2.py","server_main2.log","$null","_restart_main2.bat","_kill_restart.bat",
    "INICIAR.bat","kill.bat","backup_db.bat","INSTALL.bat",
]

def step(msg): print(f"\n[*] {msg}")
def ok(msg):   print(f"    OK  {msg}")
def warn(msg): print(f"    --  {msg}")

# ── 1. Delete junk ────────────────────────────────────────────────────────────
step("Borrando archivos obsoletos...")
deleted = 0
for f in JUNK:
    p = os.path.join(BASE, f)
    if os.path.exists(p):
        try:
            os.remove(p)
            ok(f"Borrado: {f}")
            deleted += 1
        except Exception as e:
            warn(f"No se pudo borrar {f}: {e}")
print(f"    Total borrados: {deleted}")

# ── 2. Delete junk folders ────────────────────────────────────────────────────
step("Borrando carpetas obsoletas...")
junk_dirs = ["dvdcoin_bank_windows", "__pycache__"]
for d in junk_dirs:
    p = os.path.join(BASE, d)
    if os.path.exists(p):
        try:
            shutil.rmtree(p)
            ok(f"Borrado: {d}/")
        except Exception as e:
            warn(f"No se pudo borrar {d}/: {e}")

# ── 3. Remove old scheduled tasks ─────────────────────────────────────────────
step("Eliminando tareas programadas antiguas...")
old_tasks = ["DVDcoin-ngrok", "DVDcoin", "DVDcoin-Server", "DVDcoin-Watchdog"]
for t in old_tasks:
    r = subprocess.run(
        ["schtasks", "/delete", "/tn", t, "/f"],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        ok(f"Tarea eliminada: {t}")
    else:
        warn(f"Tarea no existía: {t}")

# ── 4. Create the autostart scheduled task ────────────────────────────────────
step("Creando tarea de inicio automático...")

task_name = "DVDcoin-Autostart"
# Use start.py which handles server + ngrok
cmd = f'"{PYTHON}" "{os.path.join(BASE, "start.py")}"'

# Create XML for the task — runs at logon, highest privileges, hidden
xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>DVDcoin Bank — arranque automatico al iniciar Windows</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT10S</Delay>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>4</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{PYTHON}</Command>
      <Arguments>"{os.path.join(BASE, "start.py")}"</Arguments>
      <WorkingDirectory>{BASE}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

xml_path = os.path.join(BASE, "_task.xml")
with open(xml_path, "w", encoding="utf-16") as f:
    f.write(xml)

r = subprocess.run(
    ["schtasks", "/create", "/tn", task_name, "/xml", xml_path, "/f"],
    capture_output=True, text=True
)
os.remove(xml_path)

if r.returncode == 0:
    ok(f"Tarea creada: {task_name}")
    ok("El servidor arrancará automáticamente al iniciar Windows (10s después del login)")
else:
    warn(f"Error creando tarea: {r.stderr.strip()}")
    warn("Intenta ejecutar este script como Administrador")

# ── 5. Verify main.py is the target ───────────────────────────────────────────
step("Verificando que todo apunta a main.py...")
main_py = os.path.join(BASE, "main.py")
if os.path.exists(main_py):
    ok("main.py existe")
else:
    print("    ERROR: main.py no encontrado!")

# Check start.py
sp = os.path.join(BASE, "start.py")
if os.path.exists(sp):
    content = open(sp, encoding="utf-8", errors="ignore").read()
    if "main.py" in content and "main_2" not in content:
        ok("start.py apunta a main.py")
    else:
        warn("start.py puede tener referencias incorrectas")

# Check watchdog.py
wp = os.path.join(BASE, "watchdog.py")
if os.path.exists(wp):
    content = open(wp, encoding="utf-8", errors="ignore").read()
    if "main.py" in content and "main_2" not in content:
        ok("watchdog.py apunta a main.py")
    else:
        warn("watchdog.py puede tener referencias incorrectas")

# ── 6. Kill current server and restart cleanly ────────────────────────────────
step("Reiniciando servidor con la versión actualizada...")

# Kill port 8000
import socket as _sock
try:
    result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if ":8000" in line and "LISTENING" in line:
            parts = line.split()
            pid = parts[-1]
            if pid.isdigit() and int(pid) > 4:
                subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                ok(f"Proceso {pid} terminado")
except Exception as e:
    warn(f"Error matando proceso: {e}")

import time
time.sleep(2)

# Start server in background
log_path = os.path.join(BASE, "server.log")
with open(log_path, "w") as lf:
    proc = subprocess.Popen(
        [PYTHON, main_py],
        stdout=lf, stderr=lf,
        cwd=BASE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )

ok(f"Servidor arrancado (PID {proc.pid})")

# Wait for it
time.sleep(6)
try:
    import urllib.request
    r2 = urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=5)
    ok(f"Servidor respondiendo: {r2.read().decode()}")
except Exception as e:
    warn(f"Servidor no responde aún: {e}")
    warn("Revisa server.log para ver el error")

print(f"""
╔══════════════════════════════════════════════════════╗
║         DVDcoin Bank — Setup completado              ║
╠══════════════════════════════════════════════════════╣
║  Servidor:    http://localhost:8000                  ║
║  Autostart:   Tarea '{task_name}'              ║
║  Arranque:    python start.py                        ║
║  Servidor:    python main.py                         ║
╚══════════════════════════════════════════════════════╝
""")
