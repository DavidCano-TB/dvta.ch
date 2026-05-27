#!/usr/bin/env python3
import requests
import json

# Probar login directo
url = "https://premium-size-unreached.ngrok-free.dev/api/login"

credentials = [
    ("dvd", "3666"),
    ("dvd", "dvd"),
    ("admin", "dvd_ghost_2026"),
]

print("=" * 70)
print("PROBANDO LOGIN EN EL SERVIDOR PÚBLICO")
print("=" * 70)

for username, password in credentials:
    print(f"\n🔑 Probando: {username} / {password}")
    
    try:
        response = requests.post(
            url,
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ LOGIN EXITOSO")
            print(f"   Token: {data['token'][:30]}...")
            print(f"   Admin: {data.get('is_admin', False)}")
            print(f"   Superadmin: {data.get('is_superadmin', False)}")
        else:
            print(f"   ❌ FALLO: {response.text}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

print("\n" + "=" * 70)
