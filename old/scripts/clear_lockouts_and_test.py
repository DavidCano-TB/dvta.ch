#!/usr/bin/env python3
import sqlite3
import requests

print("=" * 70)
print("LIMPIANDO LOCKOUTS Y PROBANDO LOGIN")
print("=" * 70)

# Limpiar lockouts
conn = sqlite3.connect('data/users.db')
cursor = conn.cursor()

# Verificar si hay lockouts
cursor.execute("SELECT username, is_blocked FROM users WHERE username='dvd'")
row = cursor.fetchone()

if row:
    username, is_blocked = row
    print(f"\nUsuario: {username}")
    print(f"Bloqueado: {is_blocked}")
    
    if is_blocked:
        print("\n⚠ Usuario bloqueado. Desbloqueando...")
        cursor.execute("UPDATE users SET is_blocked=0 WHERE username='dvd'")
        conn.commit()
        print("✅ Usuario desbloqueado")

# Verificar tabla de failed_logins si existe
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='failed_logins'")
    if cursor.fetchone():
        cursor.execute("DELETE FROM failed_logins WHERE username='dvd'")
        conn.commit()
        print("✅ Lockouts limpiados")
except:
    pass

conn.close()

print("\n" + "=" * 70)
print("PROBANDO LOGIN LOCAL")
print("=" * 70)

try:
    r = requests.post(
        "http://localhost:8000/api/login",
        json={"username": "dvd", "password": "3666"},
        timeout=5
    )
    
    print(f"\nStatus: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print("✅ LOGIN LOCAL EXITOSO")
        print(f"Username: {data['username']}")
        print(f"Admin: {data.get('is_admin', False)}")
        print(f"Superadmin: {data.get('is_superadmin', False)}")
    else:
        print(f"❌ FALLO: {r.text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 70)
print("PROBANDO LOGIN PÚBLICO")
print("=" * 70)

try:
    r = requests.post(
        "https://premium-size-unreached.ngrok-free.dev/api/login",
        json={"username": "dvd", "password": "3666"},
        timeout=10
    )
    
    print(f"\nStatus: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print("✅ LOGIN PÚBLICO EXITOSO")
        print(f"Username: {data['username']}")
        print(f"Admin: {data.get('is_admin', False)}")
        print(f"Superadmin: {data.get('is_superadmin', False)}")
    else:
        print(f"❌ FALLO: {r.text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 70)
