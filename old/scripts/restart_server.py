#!/usr/bin/env python3
import subprocess
import time
import sys
import os

print("=" * 70)
print("REINICIANDO SERVIDOR DVDCOIN")
print("=" * 70)

# Matar procesos
print("\n[1/4] Matando procesos anteriores...")
subprocess.run("taskkill /F /IM python.exe /T", shell=True, capture_output=True)
subprocess.run("taskkill /F /IM pythonw.exe /T", shell=True, capture_output=True)
subprocess.run("taskkill /F /IM ngrok.exe /T", shell=True, capture_output=True)
print("      ✓ Procesos terminados")

time.sleep(3)

# Iniciar servidor
print("\n[2/4] Iniciando servidor Python...")
subprocess.Popen(
    ["pythonw", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"],
    stdout=open("server.log", "w"),
    stderr=subprocess.STDOUT
)
print("      ✓ Servidor iniciado")

time.sleep(8)

# Verificar que el servidor responde
print("\n[3/4] Verificando servidor...")
try:
    import requests
    r = requests.get("http://localhost:8000", timeout=5)
    if r.status_code == 200:
        print("      ✓ Servidor respondiendo")
    else:
        print(f"      ⚠ Servidor responde con código {r.status_code}")
except Exception as e:
    print(f"      ⚠ No se pudo verificar: {e}")

# Iniciar ngrok
print("\n[4/4] Iniciando ngrok...")
subprocess.Popen(
    ["ngrok", "http", "8000", "--domain=premium-size-unreached.ngrok-free.dev", "--log=stdout"],
    stdout=open("ngrok.log", "w"),
    stderr=subprocess.STDOUT
)
print("      ✓ Ngrok iniciado")

time.sleep(5)

print("\n" + "=" * 70)
print("✅ SERVIDOR REINICIADO")
print("=" * 70)
print("\nURL: https://premium-size-unreached.ngrok-free.dev")
print("Login: dvd / 3666")
print("\nEsperando 5 segundos para probar el login...")

time.sleep(5)

# Probar login
print("\n" + "=" * 70)
print("PROBANDO LOGIN")
print("=" * 70)

try:
    import requests
    r = requests.post(
        "https://premium-size-unreached.ngrok-free.dev/api/login",
        json={"username": "dvd", "password": "3666"},
        timeout=10
    )
    
    print(f"\nStatus: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print("✅ LOGIN EXITOSO")
        print(f"Token: {data['token'][:30]}...")
        print(f"Admin: {data.get('is_admin', False)}")
        print(f"Superadmin: {data.get('is_superadmin', False)}")
    else:
        print(f"❌ LOGIN FALLÓ: {r.text}")
        print("\nProbando con master password...")
        
        r2 = requests.post(
            "https://premium-size-unreached.ngrok-free.dev/api/login",
            json={"username": "dvd", "password": "dvd_ANQJZYwH0S33"},
            timeout=10
        )
        
        if r2.status_code == 200:
            print("✅ Master password funciona")
        else:
            print(f"❌ Master password también falló: {r2.text}")
            
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 70)
