#!/usr/bin/env python3
"""
Script para probar credenciales de login
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("TEST DE CREDENCIALES - DVDCoin Bank")
print("=" * 60)

# Credenciales a probar
test_credentials = [
    ("admin", "dvd_ghost_2026"),
    ("dvd", "dvd_aGGDdCWQ5Bh3"),  # Master password
    ("nebulosa", "dvd_aGGDdCWQ5Bh3"),  # Master password
    ("dvd", "dvd"),
    ("nina", "nina"),
    ("victor", "victor"),
    ("yu", "yu"),
    ("roy", "roy"),
]

for username, password in test_credentials:
    print(f"\nProbando: {username} / {password}")
    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            json={"username": username, "password": password},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ LOGIN EXITOSO")
            print(f"    Token: {data['token'][:30]}...")
            print(f"    Admin: {data.get('is_admin', False)}")
            print(f"    Superadmin: {data.get('is_superadmin', False)}")
        else:
            print(f"  ✗ FALLO: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")

print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)
print("\nCredenciales válidas encontradas arriba con ✓")
print("\nPara crear un nuevo usuario, usa /api/register")
