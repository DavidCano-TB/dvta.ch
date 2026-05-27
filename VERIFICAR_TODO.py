#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
  🔍 VERIFICACIÓN COMPLETA DEL SISTEMA DVDBANK
═══════════════════════════════════════════════════════════════════════════
"""
import os
import sqlite3
import sys

def check_file(path, name):
    """Verificar que un archivo existe"""
    if os.path.exists(path):
        print(f"  ✅ {name}: EXISTE")
        return True
    else:
        print(f"  ❌ {name}: NO EXISTE")
        return False

def check_database(db_path, expected_tables, db_name):
    """Verificar que una base de datos tiene las tablas esperadas"""
    if not os.path.exists(db_path):
        print(f"  ❌ {db_name}: NO EXISTE")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        tables = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        conn.close()
        
        missing = [t for t in expected_tables if t not in tables]
        if missing:
            print(f"  ⚠️  {db_name}: Faltan tablas {missing}")
            return False
        else:
            print(f"  ✅ {db_name}: OK ({len(tables)} tablas)")
            return True
    except Exception as e:
        print(f"  ❌ {db_name}: ERROR - {e}")
        return False

def main():
    print("\n" + "═" * 79)
    print("  🔍 VERIFICACIÓN COMPLETA DEL SISTEMA")
    print("═" * 79 + "\n")
    
    all_ok = True
    
    # 1. Archivos principales
    print("[1/5] Verificando archivos principales...")
    all_ok &= check_file("main.py", "main.py")
    all_ok &= check_file("cloudflared.exe", "cloudflared.exe")
    all_ok &= check_file("cloudflare-tunnel-dvta.yml", "cloudflare-tunnel-dvta.yml")
    all_ok &= check_file("ai_helper.py", "ai_helper.py")
    print()
    
    # 2. Directorios
    print("[2/5] Verificando directorios...")
    for dir_name in ["data", "static", "config", "backup", "logs"]:
        if os.path.exists(dir_name):
            print(f"  ✅ {dir_name}/: EXISTE")
        else:
            print(f"  ❌ {dir_name}/: NO EXISTE")
            all_ok = False
    print()
    
    # 3. Bases de datos
    print("[3/5] Verificando bases de datos...")
    
    databases = {
        "data/users.db": ["users", "lang_prefs"],
        "data/rights.db": ["roles", "opo_players"],
        "data/transactions.db": ["transactions"],
        "data/stats.db": ["sessions"],
        "data/opo.db": ["opo_results", "opo_sessions"],
        "data/apuestas.db": ["porras", "apuestas_usuarios", "estadisticas_porras", "votaciones", "votaciones_opciones", "votaciones_votos"],
        "data/messages.db": ["messages", "msg_reads", "msg_reactions", "msg_settings", "video_rooms", "video_room_members", "video_room_invites"]
    }
    
    for db_path, tables in databases.items():
        all_ok &= check_database(db_path, tables, os.path.basename(db_path))
    print()
    
    # 4. Archivos de configuración
    print("[4/5] Verificando archivos de configuración...")
    config_files = [
        ("config/jwt_secret.txt", "JWT Secret"),
        ("config/master.txt", "Master Password")
    ]
    
    for path, name in config_files:
        if os.path.exists(path):
            print(f"  ✅ {name}: CONFIGURADO")
        else:
            print(f"  ⚠️  {name}: Se generará al iniciar")
    print()
    
    # 5. Scripts de inicio
    print("[5/5] Verificando scripts de inicio...")
    scripts = [
        "ARRANCAR.bat",
        "INICIAR_TUNNEL_DVTA.bat",
        "INICIAR_SISTEMA_DVTA.bat",
        "DETENER_SISTEMA.bat",
        "VER_ESTADO.bat"
    ]
    
    for script in scripts:
        all_ok &= check_file(script, script)
    print()
    
    # Resumen final
    print("═" * 79)
    if all_ok:
        print("  ✅ VERIFICACIÓN COMPLETA: TODO OK")
        print("\n  El sistema está listo para usar:")
        print("    • Iniciar servidor: ARRANCAR.bat")
        print("    • Iniciar túnel: INICIAR_TUNNEL_DVTA.bat")
        print("    • Iniciar todo: INICIAR_SISTEMA_DVTA.bat")
    else:
        print("  ⚠️  VERIFICACIÓN COMPLETA: ALGUNOS PROBLEMAS ENCONTRADOS")
        print("\n  Revisa los errores arriba y corrige antes de iniciar.")
    print("═" * 79 + "\n")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
