import subprocess, sys, time, os, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

# Kill port 8000
result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
for line in result.stdout.splitlines():
    if ":8000" in line and "LISTENING" in line:
        parts = line.split()
        pid = parts[-1]
        if pid.isdigit() and int(pid) > 4:
            subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
            print(f"Killed PID {pid}")

time.sleep(2)

# Start server
log = open(os.path.join(BASE, "server.log"), "w", encoding="utf-8")
proc = subprocess.Popen(
    [PYTHON, os.path.join(BASE, "main.py")],
    stdout=log, stderr=log, cwd=BASE,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
)
print(f"Server started PID {proc.pid}")

# Wait and verify
for i in range(15):
    time.sleep(1)
    try:
        r = urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=3)
        print(f"SERVER OK: {r.read().decode()}")
        # Verify new endpoint
        break
    except:
        print(f"  waiting... {i+1}s")

# Verify /api/ice-servers endpoint exists
try:
    import json
    # Need token - just check the route exists (will get 401/403 without auth, not 404)
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/api/ice-servers", timeout=3)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"ENDPOINT /api/ice-servers: NOT FOUND - check main.py")
        else:
            print(f"ENDPOINT /api/ice-servers: EXISTS (HTTP {e.code})")
    except Exception as e2:
        print(f"ENDPOINT check error: {e2}")
except Exception as e:
    print(f"Verify error: {e}")

print("Done.")
