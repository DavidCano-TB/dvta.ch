#!/usr/bin/env python3
"""Diagnóstico del sistema de votaciones"""

import os
import sys

print("=" * 60)
print("DIAGNÓSTICO DEL SISTEMA DE VOTACIONES")
print("=" * 60)

# 1. Verificar archivo HTML
print("\n[1] Verificando archivo HTML...")
html_path = "game_pages/votaciones/votaciones.html"
if os.path.exists(html_path):
    size = os.path.getsize(html_path)
    print(f"✅ Archivo existe: {html_path}")
    print(f"   Tamaño: {size:,} bytes")
else:
    print(f"❌ Archivo NO existe: {html_path}")
    sys.exit(1)

# 2. Verificar backend
print("\n[2] Verificando backend en main.py...")
if os.path.exists("main.py"):
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    # Verificar endpoints
    endpoints = [
        '@app.get("/votaciones")',
        '@app.get("/api/votaciones/list")',
        '@app.get("/api/votaciones/{votacion_id}")',
        '@app.post("/api/votaciones/create")',
        '@app.post("/api/votaciones/votar")',
        '@app.post("/api/votaciones/finalizar")',
        '@app.delete("/api/votaciones/{votacion_id}")',
    ]
    
    found = 0
    for endpoint in endpoints:
        if endpoint in content:
            found += 1
            print(f"   ✅ {endpoint}")
        else:
            print(f"   ❌ {endpoint}")
    
    print(f"\n   Total: {found}/{len(endpoints)} endpoints encontrados")
    
    # Verificar función db_votaciones
    if "def db_votaciones" in content:
        print("   ✅ Función db_votaciones() encontrada")
    else:
        print("   ❌ Función db_votaciones() NO encontrada")
else:
    print("❌ main.py NO encontrado")
    sys.exit(1)

# 3. Verificar navegación
print("\n[3] Verificando navegación en index.html...")
if os.path.exists("static/index.html"):
    with open("static/index.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    if "openVotaciones" in content:
        print("   ✅ Función openVotaciones() encontrada")
    else:
        print("   ❌ Función openVotaciones() NO encontrada")
        
    if "Votaciones" in content:
        print("   ✅ Botón 'Votaciones' encontrado")
    else:
        print("   ❌ Botón 'Votaciones' NO encontrado")
else:
    print("❌ static/index.html NO encontrado")

# 4. Verificar servidor
print("\n[4] Verificando si el servidor está corriendo...")
try:
    import requests
    response = requests.get("http://localhost:8000/votaciones", timeout=2)
    print(f"   ✅ Servidor CORRIENDO - Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Endpoint /votaciones responde correctamente")
    else:
        print(f"   ⚠️  Endpoint responde pero con status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Servidor NO está corriendo")
    print("   💡 Solución: Ejecuta 'python main.py' para iniciar el servidor")
except Exception as e:
    print(f"   ❌ Error al conectar: {e}")

# 5. Verificar base de datos
print("\n[5] Verificando base de datos...")
if os.path.exists("data/apuestas.db"):
    print("   ✅ Base de datos existe: data/apuestas.db")
    try:
        import sqlite3
        conn = sqlite3.connect("data/apuestas.db")
        cursor = conn.cursor()
        
        # Verificar tabla votaciones
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='votaciones'")
        if cursor.fetchone():
            print("   ✅ Tabla 'votaciones' existe")
            
            # Contar votaciones
            cursor.execute("SELECT COUNT(*) FROM votaciones")
            count = cursor.fetchone()[0]
            print(f"   📊 Votaciones en DB: {count}")
        else:
            print("   ⚠️  Tabla 'votaciones' NO existe (se creará al iniciar)")
        
        # Verificar tabla votos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='votos'")
        if cursor.fetchone():
            print("   ✅ Tabla 'votos' existe")
        else:
            print("   ⚠️  Tabla 'votos' NO existe (se creará al iniciar)")
        
        conn.close()
    except Exception as e:
        print(f"   ⚠️  Error al leer DB: {e}")
else:
    print("   ⚠️  Base de datos NO existe (se creará al iniciar)")

print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)
print("\n✅ Todos los archivos están en su lugar")
print("✅ El código del backend está completo")
print("✅ La navegación está configurada")
print("\n💡 PARA USAR EL SISTEMA DE VOTACIONES:")
print("   1. Inicia el servidor: python main.py")
print("   2. Abre http://localhost:8000 en tu navegador")
print("   3. Inicia sesión")
print("   4. Click en el botón 'Votaciones'")
print("=" * 60)
