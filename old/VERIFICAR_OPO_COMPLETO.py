#!/usr/bin/env python3
"""Verificación completa del sistema OPO"""
import sqlite3
import os
import json

print("=" * 70)
print("  VERIFICACIÓN COMPLETA DEL SISTEMA OPO")
print("=" * 70)
print()

# 1. Verificar base de datos OPO
print("[1] VERIFICANDO BASE DE DATOS OPO (data/opo.db)")
print("-" * 70)
try:
    conn = sqlite3.connect('data/opo.db')
    conn.row_factory = sqlite3.Row
    
    # Listar tablas
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in cursor.fetchall()]
    print(f"Tablas encontradas: {len(tables)}")
    for table in tables:
        print(f"  - {table}")
        # Contar registros
        cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
        count = cursor.fetchone()['count']
        print(f"    Registros: {count}")
    
    conn.close()
except Exception as e:
    print(f"❌ ERROR: {e}")
print()

# 2. Verificar archivo de preguntas JSON
print("[2] VERIFICANDO ARCHIVO DE PREGUNTAS")
print("-" * 70)
json_files = [
    'data/opo_questions.json',
    'opo_questions.json',
    'static/opo/questions.json',
    'data/questions.json'
]

questions_found = False
for json_file in json_files:
    if os.path.exists(json_file):
        print(f"✓ Encontrado: {json_file}")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    print(f"  Total preguntas: {len(data)}")
                    if len(data) > 0:
                        print(f"  Primera pregunta: {data[0].get('p', 'N/A')[:50]}...")
                        print(f"  Campos: {list(data[0].keys())}")
                    questions_found = True
                elif isinstance(data, dict):
                    print(f"  Estructura: diccionario con {len(data)} claves")
                    print(f"  Claves: {list(data.keys())}")
        except Exception as e:
            print(f"  ❌ Error al leer: {e}")
    else:
        print(f"✗ No existe: {json_file}")

if not questions_found:
    print("\n❌ NO SE ENCONTRÓ ARCHIVO DE PREGUNTAS")
print()

# 3. Verificar OpoManager en main.py
print("[3] VERIFICANDO OpoManager EN main.py")
print("-" * 70)
try:
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Buscar clase OpoManager
        if 'class OpoManager:' in content:
            print("✓ Clase OpoManager encontrada")
            
            # Buscar método de carga de preguntas
            if 'def _load_questions' in content or 'self._questions' in content:
                print("✓ Sistema de carga de preguntas presente")
            else:
                print("❌ NO se encontró método de carga de preguntas")
            
            # Buscar método enable
            if 'def enable' in content:
                print("✓ Método enable() presente")
            else:
                print("❌ NO se encontró método enable()")
            
            # Buscar renderizado de bloques
            if 'total_blocks' in content:
                print("✓ Sistema de bloques presente")
            else:
                print("❌ NO se encontró sistema de bloques")
        else:
            print("❌ Clase OpoManager NO encontrada")
except Exception as e:
    print(f"❌ ERROR: {e}")
print()

# 4. Verificar frontend
print("[4] VERIFICANDO FRONTEND (static/opo/game.html)")
print("-" * 70)
try:
    with open('static/opo/game.html', 'r', encoding='utf-8') as f:
        content = f.read()
        
        checks = [
            ('function renderBlockSelect', 'Función renderBlockSelect()'),
            ('function renderWaiting', 'Función renderWaiting()'),
            ('blockBtn', 'Clase CSS blockBtn'),
            ('id="blockGrid"', 'Elemento blockGrid'),
            ('id="waitBlockGrid"', 'Elemento waitBlockGrid'),
            ('function applyState', 'Función applyState()'),
            ('function connectWS', 'Función connectWS()'),
        ]
        
        for search, desc in checks:
            if search in content:
                print(f"✓ {desc}")
            else:
                print(f"❌ {desc} NO encontrado")
except Exception as e:
    print(f"❌ ERROR: {e}")
print()

# 5. Verificar usuarios OPO
print("[5] VERIFICANDO USUARIOS CON ACCESO OPO")
print("-" * 70)
try:
    conn = sqlite3.connect('data/rights.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT username FROM opo_players ORDER BY username")
    users = [row['username'] for row in cursor.fetchall()]
    print(f"Total usuarios OPO: {len(users)}")
    for user in users:
        print(f"  ✓ {user}")
    conn.close()
except Exception as e:
    print(f"❌ ERROR: {e}")
print()

# 6. Verificar endpoint WebSocket
print("[6] VERIFICANDO ENDPOINT WEBSOCKET")
print("-" * 70)
try:
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
        if '@app.websocket("/ws/opo")' in content:
            print("✓ Endpoint /ws/opo encontrado")
            
            # Verificar verificación de OPO_USERS
            if 'if username not in OPO_USERS:' in content:
                print("✓ Verificación de OPO_USERS presente")
            else:
                print("❌ Verificación de OPO_USERS NO encontrada")
        else:
            print("❌ Endpoint /ws/opo NO encontrado")
except Exception as e:
    print(f"❌ ERROR: {e}")
print()

print("=" * 70)
print("  FIN DE LA VERIFICACIÓN")
print("=" * 70)
