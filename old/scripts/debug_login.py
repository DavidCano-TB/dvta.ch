#!/usr/bin/env python3
"""
Debug completo del login
"""
import sqlite3
import bcrypt
import sys

print("=" * 70)
print("DEBUG COMPLETO DEL LOGIN")
print("=" * 70)

# 1. Verificar base de datos
conn = sqlite3.connect('data/users.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT * FROM users WHERE username='dvd'")
row = cursor.fetchone()

if not row:
    print("\n❌ ERROR: Usuario 'dvd' no existe en la base de datos")
    sys.exit(1)

print("\n[1] DATOS DEL USUARIO EN LA BASE DE DATOS:")
print(f"    Username: {row['username']}")
print(f"    Password hash: {row['password_hash'][:60]}...")
print(f"    Is blocked: {row['is_blocked']}")
print(f"    Balance: {row['balance']}")

# 2. Probar contraseña
pwd_hash = row['password_hash']
test_password = "3666"

print(f"\n[2] PROBANDO CONTRASEÑA '{test_password}':")

try:
    result = bcrypt.checkpw(test_password.encode('utf-8'), pwd_hash.encode('utf-8'))
    if result:
        print(f"    ✅ La contraseña '{test_password}' es CORRECTA")
    else:
        print(f"    ❌ La contraseña '{test_password}' es INCORRECTA")
        
        # Probar otras contraseñas
        print("\n    Probando otras contraseñas:")
        for pwd in ["dvd", "password", "admin", "1234"]:
            if bcrypt.checkpw(pwd.encode('utf-8'), pwd_hash.encode('utf-8')):
                print(f"    ✅ Contraseña encontrada: '{pwd}'")
                break
except Exception as e:
    print(f"    ❌ ERROR al verificar: {e}")

# 3. Simular el código del servidor
print("\n[3] SIMULANDO CÓDIGO DEL SERVIDOR:")

username_input = "dvd"
password_input = "3666"

# El servidor hace .strip().lower()
u = username_input.strip().lower()
print(f"    Username procesado: '{u}'")

# Buscar en DB
cursor.execute("SELECT * FROM users WHERE username=?", (u,))
row2 = cursor.fetchone()

if not row2:
    print(f"    ❌ Usuario '{u}' no encontrado en DB")
else:
    print(f"    ✅ Usuario encontrado")
    print(f"    Is blocked: {row2['is_blocked']}")
    
    if row2['is_blocked']:
        print("    ❌ Usuario bloqueado")
    else:
        # Verificar contraseña
        pwd_hash2 = row2['password_hash']
        try:
            if bcrypt.checkpw(password_input.encode('utf-8'), pwd_hash2.encode('utf-8')):
                print(f"    ✅ Contraseña correcta - LOGIN DEBERÍA FUNCIONAR")
            else:
                print(f"    ❌ Contraseña incorrecta")
                print(f"    Hash en DB: {pwd_hash2[:60]}...")
        except Exception as e:
            print(f"    ❌ Error al verificar: {e}")

conn.close()

# 4. Probar con requests
print("\n[4] PROBANDO CON REQUESTS:")

import requests
import json

# Probar local
print("\n    [A] LOCAL (http://localhost:8000):")
try:
    r = requests.post(
        "http://localhost:8000/api/login",
        json={"username": "dvd", "password": "3666"},
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print(f"        Status: {r.status_code}")
    if r.status_code == 200:
        print(f"        ✅ LOGIN EXITOSO")
        print(f"        Response: {r.json()}")
    else:
        print(f"        ❌ FALLO")
        print(f"        Response: {r.text}")
except Exception as e:
    print(f"        ❌ ERROR: {e}")

# Probar público
print("\n    [B] PÚBLICO (https://premium-size-unreached.ngrok-free.dev):")
try:
    r = requests.post(
        "https://premium-size-unreached.ngrok-free.dev/api/login",
        json={"username": "dvd", "password": "3666"},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    print(f"        Status: {r.status_code}")
    if r.status_code == 200:
        print(f"        ✅ LOGIN EXITOSO")
        print(f"        Response: {r.json()}")
    else:
        print(f"        ❌ FALLO")
        print(f"        Response: {r.text}")
except Exception as e:
    print(f"        ❌ ERROR: {e}")

print("\n" + "=" * 70)
print("CONCLUSIÓN:")
print("=" * 70)
print("\nSi la contraseña es correcta en [2] y [3] pero falla en [4],")
print("el problema está en el código del servidor o en la conexión a la DB.")
print("\n" + "=" * 70)
