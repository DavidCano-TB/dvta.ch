#!/usr/bin/env python3
"""
Script para verificar que nebulosa tiene todos los privilegios de superadmin.
"""

import sqlite3
import os

DATA_DIR = "data"
DB_RIGHTS = os.path.join(DATA_DIR, "rights.db")

def verificar_nebulosa():
    """Verifica el estado de nebulosa en el sistema."""
    print("=" * 70)
    print("VERIFICACIÓN DE PRIVILEGIOS DE NEBULOSA")
    print("=" * 70)
    print()
    
    # 1. Verificar en código (main.py)
    print("📋 VERIFICACIÓN EN CÓDIGO (main.py)")
    print("-" * 70)
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        if '"nebulosa"' in content and 'SUPERADMINS' in content:
            # Buscar la línea específica
            for line in content.split('\n'):
                if 'SUPERADMINS' in line and '=' in line and 'nebulosa' in line:
                    print(f"✅ Encontrada en SUPERADMINS: {line.strip()}")
                    break
        else:
            print("❌ No encontrada en SUPERADMINS")
            
        if '"nebulosa"' in content and 'ADMINS' in content:
            for line in content.split('\n'):
                if 'ADMINS' in line and '=' in line and 'nebulosa' in line and 'SUPERADMINS' not in line:
                    print(f"✅ Encontrada en ADMINS: {line.strip()}")
                    break
        else:
            print("❌ No encontrada en ADMINS")
    except Exception as e:
        print(f"❌ Error al leer main.py: {e}")
    
    print()
    
    # 2. Verificar en base de datos - roles
    print("🗄️  VERIFICACIÓN EN BASE DE DATOS (rights.db)")
    print("-" * 70)
    try:
        conn = sqlite3.connect(DB_RIGHTS)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar en roles
        cursor.execute("SELECT * FROM roles WHERE username = 'nebulosa'")
        role = cursor.fetchone()
        
        if role:
            print(f"✅ Encontrada en tabla 'roles':")
            print(f"   - Username: {role['username']}")
            print(f"   - Role: {role['role']}")
            print(f"   - Granted by: {role['granted_by']}")
            print(f"   - Granted at: {role['granted_at']}")
        else:
            print("❌ NO encontrada en tabla 'roles'")
        
        print()
        
        # Verificar en opo_players
        cursor.execute("SELECT * FROM opo_players WHERE username = 'nebulosa'")
        opo = cursor.fetchone()
        
        if opo:
            print(f"✅ Encontrada en tabla 'opo_players':")
            print(f"   - Username: {opo['username']}")
            print(f"   - Added by: {opo['added_by']}")
            print(f"   - Added at: {opo['added_at']}")
        else:
            print("❌ NO encontrada en tabla 'opo_players'")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error al verificar base de datos: {e}")
    
    print()
    
    # 3. Verificar en archivos frontend
    print("🌐 VERIFICACIÓN EN FRONTEND")
    print("-" * 70)
    
    archivos_frontend = [
        "static/opo/game.html",
        "static/pasapalabra/index.html",
        "static/pages/index.html",
        "static/index.html",
        "static/webrtc-video.html",
        "static/pages/webrtc-video.html"
    ]
    
    for archivo in archivos_frontend:
        try:
            if os.path.exists(archivo):
                with open(archivo, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if 'nebulosa' in content:
                    # Contar menciones
                    menciones = content.count('nebulosa')
                    print(f"✅ {archivo}: {menciones} mención(es)")
                else:
                    print(f"⚠️  {archivo}: No se encontró 'nebulosa'")
            else:
                print(f"❌ {archivo}: Archivo no encontrado")
        except Exception as e:
            print(f"❌ {archivo}: Error al leer - {e}")
    
    print()
    print("=" * 70)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 70)
    print()
    print("Si todos los checks anteriores muestran ✅, entonces:")
    print()
    print("✅ Nebulosa está configurada como SUPERADMIN en el código")
    print("✅ Nebulosa tiene rol de admin en la base de datos")
    print("✅ Nebulosa tiene acceso permanente a OPO")
    print("✅ Nebulosa está reconocida en el frontend")
    print()
    print("🔄 IMPORTANTE: Reinicia el servidor para aplicar todos los cambios")
    print()

if __name__ == "__main__":
    verificar_nebulosa()
