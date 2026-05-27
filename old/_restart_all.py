#!/usr/bin/env python3
"""
Script de reinicio completo del sistema DVDcoin
- Mata todos los procesos Python y ngrok
- Limpia el puerto 8000
- Inicia el servidor Python
- Inicia ngrok
- Verifica que todo funcione
- Abre el navegador
"""
import subprocess
import sys
import time
import os
import urllib.request
import json
import webbrowser

BASE = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

print("=" * 60)
print(" REINICIO COMPLETO DEL SISTEMA DVDCOIN")
print("=" * 60)

# 1. Matar todos los procesos Python y ngrok
print("\n[1/7] Matando procesos existentes...")
subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], 
               capture_output=True)
subprocess.run(["taskkill", "/F", "/IM", "ngrok.exe", "/T"], 
               capture_output=True)
time.sleep(3)
print("✓ Procesos terminados")

# 2. Limpiar puerto 8000
print("\n[2/7] Limpiando puerto 8000...")
result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, 
                       encoding="utf-8", errors="ignore")
for line in result.stdout.splitlines():
    if ":8000" in line and "LISTENING" in line:
        parts = line.split()
        pid = parts[-1]
        if pid.isdigit() and int(pid) > 4:
            subprocess.run(["taskkill", "/F", "/PID", pid], 
                          capture_output=True)
            print(f"  Killed PID {pid}")
time.sleep(2)
print("✓ Puerto 8000 limpio")

# 3. Iniciar servidor Python
print("\n[3/7] Iniciando servidor Python...")
log = open(os.path.join(BASE, "server.log"), "w", encoding="utf-8")
proc = subprocess.Popen(
    [PYTHON, os.path.join(BASE, "main.py")],
    stdout=log, stderr=log, cwd=BASE,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
)
print(f"✓ Servidor iniciado (PID {proc.pid})")

# 4. Esperar y verificar servidor
print("\n[4/7] Verificando servidor...")
for i in range(15):
    time.sleep(1)
    try:
        r = urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=3)
        data = json.loads(r.read().decode())
        print(f"✓ Servidor OK: {data.get('status', 'ok')}")
        break
    except:
        print(f"  Esperando... {i+1}s")
else:
    print("✗ ERROR: Servidor no responde")
    sys.exit(1)

# 5. Iniciar ngrok
print("\n[5/7] Iniciando ngrok...")
ngrok_log = open(os.path.join(BASE, "ngrok.log"), "w", encoding="utf-8")
ngrok_proc = subprocess.Popen(
    ["ngrok", "http", "8000"],
    stdout=ngrok_log, stderr=ngrok_log, cwd=BASE,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
)
print(f"✓ Ngrok iniciado (PID {ngrok_proc.pid})")

# 6. Obtener URL de ngrok
print("\n[6/7] Obteniendo URL pública...")
ngrok_url = None
for i in range(10):
    time.sleep(1)
    try:
        r = urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=3)
        data = json.loads(r.read().decode())
        if data.get("tunnels") and len(data["tunnels"]) > 0:
            ngrok_url = data["tunnels"][0]["public_url"]
            print(f"✓ URL pública: {ngrok_url}")
            break
    except:
        print(f"  Esperando ngrok... {i+1}s")
else:
    print("✗ ADVERTENCIA: No se pudo obtener URL de ngrok")

# 7. Verificar URL pública
if ngrok_url:
    print("\n[7/7] Verificando URL pública...")
    try:
        req = urllib.request.Request(
            f"{ngrok_url}/api/health",
            headers={"ngrok-skip-browser-warning": "1"}
        )
        r = urllib.request.urlopen(req, timeout=10)
        print(f"✓ URL pública funciona: {r.getcode()}")
    except Exception as e:
        print(f"✗ ADVERTENCIA: URL pública no responde: {e}")
else:
    print("\n[7/7] Saltando verificación de URL pública")

# Resumen
print("\n" + "=" * 60)
print(" SISTEMA INICIADO CORRECTAMENTE")
print("=" * 60)
print(f"\n✓ Servidor local:  http://127.0.0.1:8000")
if ngrok_url:
    print(f"✓ URL pública:     {ngrok_url}")
    print(f"\nURLs de prueba:")
    print(f"  - Inicio:        {ngrok_url}/")
    print(f"  - Videollamadas: {ngrok_url}/video")
    print(f"  - Apuestas:      {ngrok_url}/apuestas")
    print(f"  - Porra 1:       {ngrok_url}/apuestas/porra/1")
else:
    print(f"✗ URL pública:     No disponible")

print("\n" + "=" * 60)
print(" LOGS:")
print("=" * 60)
print(f"  - Servidor: {os.path.join(BASE, 'server.log')}")
print(f"  - Ngrok:    {os.path.join(BASE, 'ngrok.log')}")

# Abrir navegador
if ngrok_url:
    print("\n[EXTRA] Abriendo navegador...")
    try:
        webbrowser.open(f"{ngrok_url}/")
        print("✓ Navegador abierto")
    except:
        print("✗ No se pudo abrir el navegador automáticamente")

print("\n" + "=" * 60)
print(" LISTO PARA USAR")
print("=" * 60)
print()
