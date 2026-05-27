#!/usr/bin/env python3
"""
Script para probar el endpoint de setup de Hundir la Flota
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
TOKEN = input("Ingresa tu token de admin: ").strip()

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "1"
}

# Test 1: Verificar que el usuario es admin
print("\n[1] Verificando usuario...")
try:
    r = requests.get(f"{BASE_URL}/api/me", headers=headers)
    if r.status_code == 200:
        user_data = r.json()
        print(f"   ✓ Usuario: {user_data.get('username')}")
        print(f"   ✓ Admin: {user_data.get('is_admin')}")
    else:
        print(f"   ✗ Error: {r.status_code}")
        print(f"   {r.text}")
        exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 2: Obtener lista de usuarios
print("\n[2] Obteniendo lista de usuarios...")
try:
    r = requests.get(f"{BASE_URL}/api/hundirlaflota/users", headers=headers)
    if r.status_code == 200:
        users = r.json()
        print(f"   ✓ Usuarios disponibles: {len(users)}")
        print(f"   {users[:5]}")  # Mostrar primeros 5
    else:
        print(f"   ✗ Error: {r.status_code}")
        print(f"   {r.text}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Probar endpoint de setup
print("\n[3] Probando endpoint de setup...")
payload = {
    "players": ["dvd", "roydos"],
    "board_size": 10,
    "turn_time": 60
}

print(f"   Payload: {json.dumps(payload, indent=2)}")

try:
    r = requests.post(
        f"{BASE_URL}/api/hundirlaflota/setup",
        headers=headers,
        json=payload
    )
    print(f"   Status Code: {r.status_code}")
    print(f"   Response: {r.text}")
    
    if r.status_code == 200:
        print("   ✓ Setup exitoso!")
    else:
        print(f"   ✗ Error {r.status_code}")
        try:
            error_data = r.json()
            print(f"   Detalle: {error_data.get('detail', 'Sin detalle')}")
        except:
            pass
except Exception as e:
    print(f"   ✗ Excepción: {e}")

print("\n" + "="*60)
