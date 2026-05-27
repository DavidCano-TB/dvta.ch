#!/usr/bin/env python3
"""
🔓 DESBLOQUEAR USUARIOS
Limpia los bloqueos y intentos fallidos de todos los usuarios
"""
import sqlite3
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def desbloquear_usuarios():
    """Desbloquea todos los usuarios y limpia intentos fallidos"""
    
    # Buscar la base de datos de usuarios
    db_paths = [
        Path("data/users.db"),
        Path("../data/users.db"),
        Path("../../data/users.db")
    ]
    
    db_path = None
    for path in db_paths:
        if path.exists():
            db_path = path
            break
    
    if not db_path:
        print("❌ No se encontró la base de datos de usuarios (data/users.db)")
        print("   Asegúrate de ejecutar este script desde la carpeta correcta")
        return False
    
    print(f"📂 Base de datos: {db_path.absolute()}")
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Obtener usuarios bloqueados o con intentos fallidos
        rows = conn.execute(
            "SELECT username, failed_attempts, locked_until FROM users "
            "WHERE failed_attempts > 0 OR locked_until IS NOT NULL"
        ).fetchall()
        
        if not rows:
            print("✅ No hay usuarios bloqueados")
            conn.close()
            return True
        
        print(f"🔍 Encontrados {len(rows)} usuarios con bloqueos o intentos fallidos:")
        print()
        
        for row in rows:
            username = row["username"]
            attempts = row["failed_attempts"]
            locked = row["locked_until"]
            
            status = []
            if attempts > 0:
                status.append(f"{attempts} intentos fallidos")
            if locked:
                status.append(f"bloqueado hasta {locked}")
            
            print(f"  • {username}: {', '.join(status)}")
        
        print()
        print("🔓 Desbloqueando usuarios...")
        
        # Limpiar todos los bloqueos
        conn.execute(
            "UPDATE users SET failed_attempts = 0, locked_until = NULL "
            "WHERE failed_attempts > 0 OR locked_until IS NOT NULL"
        )
        conn.commit()
        
        # Verificar
        remaining = conn.execute(
            "SELECT COUNT(*) as count FROM users "
            "WHERE failed_attempts > 0 OR locked_until IS NOT NULL"
        ).fetchone()["count"]
        
        conn.close()
        
        if remaining == 0:
            print("✅ Todos los usuarios desbloqueados exitosamente")
            print()
            return True
        else:
            print(f"⚠️  Aún quedan {remaining} usuarios con problemas")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print_header("🔓 DESBLOQUEAR USUARIOS")
    
    print("Este script limpia los bloqueos de cuenta y reinicia los intentos fallidos.")
    print("Útil cuando los tests han causado bloqueos por intentos de login.")
    print()
    
    success = desbloquear_usuarios()
    
    if success:
        print_header("✅ COMPLETADO")
        print("Los usuarios están desbloqueados y listos para usar.")
        print()
        print("Ahora puedes ejecutar los tests:")
        print("  EJECUTAR_TODOS_LOS_TESTS.bat")
        print()
    else:
        print_header("⚠️  HUBO PROBLEMAS")
        print("Revisa los errores anteriores.")
        print()
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    input("\nPresiona Enter para continuar...")
    sys.exit(0 if success else 1)
