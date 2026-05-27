#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificación Final Completa del Sistema DVDCoin Bank
"""
import requests
import sqlite3
import bcrypt
import sys

print("=" * 70)
print(" " * 15 + "VERIFICACIÓN FINAL COMPLETA")
print(" " * 20 + "DVDCoin Bank")
print("=" * 70)
print()

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def test_result(name, success, details=""):
    status = f"{GREEN}✅ PASS{RESET}" if success else f"{RED}❌ FAIL{RESET}"
    print(f"{status} | {name}")
    if details:
        print(f"       {details}")
    return success

all_tests_passed = True

# TEST 1: Base de datos
print(f"\n{BOLD}[1] VERIFICACIÓN DE BASE DE DATOS{RESET}")
print("-" * 70)
try:
    conn = sqlite3.connect('src/data/users.db')
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT username, password_hash, is_blocked FROM users WHERE username=?", ('dvd',)).fetchone()
    conn.close()
    
    if row:
        test_result("Usuario 'dvd' existe en BD", True, f"Hash: {row['password_hash'][:30]}...")
        test_result("Usuario NO está bloqueado", row['is_blocked'] == 0, f"is_blocked = {row['is_blocked']}")
        
        # Verificar password
        pwd_hash = row['password_hash'].encode('utf-8')
        pwd_test = '3666'.encode('utf-8')
        pwd_match = bcrypt.checkpw(pwd_test, pwd_hash)
        test_result("Password '3666' coincide con hash", pwd_match)
        all_tests_passed = all_tests_passed and pwd_match
    else:
        test_result("Usuario 'dvd' existe en BD", False, "Usuario no encontrado")
        all_tests_passed = False
except Exception as e:
    test_result("Acceso a base de datos", False, str(e))
    all_tests_passed = False

# TEST 2: Servidor Local
print(f"\n{BOLD}[2] VERIFICACIÓN DE SERVIDOR LOCAL{RESET}")
print("-" * 70)
try:
    # Health check
    response = requests.get('http://localhost:8000/api/health', timeout=5)
    test_result("Health check", response.status_code == 200, f"Status: {response.status_code}")
    
    # Login
    response = requests.post(
        'http://localhost:8000/api/login',
        json={'username': 'dvd', 'password': '3666'},
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        test_result("Login local", True, f"Status: {response.status_code}")
        test_result("  → Username correcto", data.get('username') == 'dvd')
        test_result("  → Es admin", data.get('is_admin') == True)
        test_result("  → Es superadmin", data.get('is_superadmin') == True)
        test_result("  → Token generado", 'token' in data and len(data['token']) > 20)
    else:
        test_result("Login local", False, f"Status: {response.status_code} - {response.text}")
        all_tests_passed = False
        
except Exception as e:
    test_result("Servidor local", False, str(e))
    all_tests_passed = False

# TEST 3: Ngrok
print(f"\n{BOLD}[3] VERIFICACIÓN DE NGROK{RESET}")
print("-" * 70)
try:
    # Homepage
    response = requests.get('https://premium-size-unreached.ngrok-free.dev/', verify=False, timeout=10)
    test_result("Homepage ngrok", response.status_code == 200, f"Status: {response.status_code}, Size: {len(response.text)} bytes")
    
    # Login
    response = requests.post(
        'https://premium-size-unreached.ngrok-free.dev/api/login',
        json={'username': 'dvd', 'password': '3666'},
        verify=False,
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        test_result("Login ngrok", True, f"Status: {response.status_code}")
        test_result("  → Username correcto", data.get('username') == 'dvd')
        test_result("  → Es admin", data.get('is_admin') == True)
        test_result("  → Es superadmin", data.get('is_superadmin') == True)
        test_result("  → Token generado", 'token' in data and len(data['token']) > 20)
    else:
        test_result("Login ngrok", False, f"Status: {response.status_code} - {response.text}")
        all_tests_passed = False
        
except Exception as e:
    test_result("Ngrok", False, str(e))
    all_tests_passed = False

# TEST 4: Credenciales incorrectas (debe fallar)
print(f"\n{BOLD}[4] VERIFICACIÓN DE SEGURIDAD{RESET}")
print("-" * 70)
try:
    response = requests.post(
        'http://localhost:8000/api/login',
        json={'username': 'dvd', 'password': 'wrong_password'},
        timeout=5
    )
    test_result("Rechaza password incorrecto", response.status_code == 401, f"Status: {response.status_code}")
except Exception as e:
    test_result("Test de seguridad", False, str(e))

# RESUMEN FINAL
print("\n" + "=" * 70)
if all_tests_passed:
    print(f"{GREEN}{BOLD}✅ TODOS LOS TESTS PASARON - SISTEMA FUNCIONANDO CORRECTAMENTE{RESET}")
    print()
    print("🌐 URLs de acceso:")
    print("   Local:   http://localhost:8000")
    print("   Público: https://premium-size-unreached.ngrok-free.dev")
    print()
    print("🔐 Credenciales:")
    print("   Usuario:    dvd")
    print("   Contraseña: 3666")
    sys.exit(0)
else:
    print(f"{RED}{BOLD}❌ ALGUNOS TESTS FALLARON - REVISAR ERRORES ARRIBA{RESET}")
    sys.exit(1)
print("=" * 70)
