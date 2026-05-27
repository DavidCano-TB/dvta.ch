#!/usr/bin/env python3
import sqlite3
import bcrypt

print("=" * 70)
print("FORZANDO ACTUALIZACIÓN DE CONTRASEÑA")
print("=" * 70)

# Conectar a la base de datos
conn = sqlite3.connect('data/users.db')
cursor = conn.cursor()

# Verificar hash actual
cursor.execute("SELECT password_hash FROM users WHERE username='dvd'")
current_hash = cursor.fetchone()[0]
print(f"\nHash actual: {current_hash[:60]}...")

# Probar si 3666 funciona
if bcrypt.checkpw(b"3666", current_hash.encode('utf-8')):
    print("✓ La contraseña 3666 YA funciona con el hash actual")
else:
    print("✗ La contraseña 3666 NO funciona con el hash actual")
    print("\nGenerando nuevo hash...")
    
    # Generar nuevo hash
    new_hash = bcrypt.hashpw(b"3666", bcrypt.gensalt()).decode('utf-8')
    print(f"Nuevo hash: {new_hash[:60]}...")
    
    # Actualizar
    cursor.execute("UPDATE users SET password_hash=? WHERE username='dvd'", (new_hash,))
    conn.commit()
    print("✅ Hash actualizado")

# Verificar todos los usuarios admin
print("\n" + "=" * 70)
print("VERIFICANDO TODOS LOS ADMINS")
print("=" * 70)

admins = ['dvd', 'nebulosa', 'nina', 'victor', 'yu', 'roy', 'admin']
for admin in admins:
    cursor.execute("SELECT password_hash FROM users WHERE username=?", (admin,))
    row = cursor.fetchone()
    if row:
        pwd_hash = row[0]
        # Probar contraseña = username
        try:
            if bcrypt.checkpw(admin.encode('utf-8'), pwd_hash.encode('utf-8')):
                print(f"✓ {admin:15} - pwd: {admin}")
            elif admin == 'dvd' and bcrypt.checkpw(b"3666", pwd_hash.encode('utf-8')):
                print(f"✓ {admin:15} - pwd: 3666")
            elif pwd_hash in ("__UNSET__", "__AUTO__"):
                print(f"⚠ {admin:15} - Sin contraseña configurada")
            else:
                print(f"✗ {admin:15} - Contraseña desconocida")
        except:
            print(f"✗ {admin:15} - Error al verificar")

conn.close()

print("\n" + "=" * 70)
print("PROBANDO LOGIN DESPUÉS DE LA ACTUALIZACIÓN")
print("=" * 70)

import time
time.sleep(2)

import requests
try:
    r = requests.post(
        "http://localhost:8000/api/login",
        json={"username": "dvd", "password": "3666"},
        timeout=5
    )
    
    if r.status_code == 200:
        print("✅ LOGIN LOCAL EXITOSO")
    else:
        print(f"❌ LOGIN LOCAL FALLÓ: {r.status_code}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 70)
