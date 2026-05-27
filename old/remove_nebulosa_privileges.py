#!/usr/bin/env python3
"""
Script para eliminar privilegios especiales de nebulosa en la base de datos.
Convierte a nebulosa en un usuario normal sin privilegios de superadmin.
"""

import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

DB_USERS = os.path.join(DATA_DIR, "users.db")
DB_RIGHTS = os.path.join(DATA_DIR, "rights.db")
DB_TX = os.path.join(DATA_DIR, "transactions.db")
DB_STATS = os.path.join(DATA_DIR, "stats.db")
DB_OPO = os.path.join(DATA_DIR, "opo.db")


def remove_nebulosa_privileges():
    """Elimina privilegios especiales de nebulosa, manteniéndola como usuario normal."""
    
    print("=" * 70)
    print("ELIMINANDO PRIVILEGIOS ESPECIALES DE NEBULOSA")
    print("=" * 70)
    print()
    
    # 1. Eliminar de roles de admin en rights.db
    try:
        conn = sqlite3.connect(DB_RIGHTS)
        cursor = conn.cursor()
        
        # Verificar si existe en roles
        cursor.execute("SELECT * FROM roles WHERE username = 'nebulosa'")
        role = cursor.fetchone()
        
        if role:
            print("✓ Encontrada en tabla 'roles' - Eliminando...")
            cursor.execute("DELETE FROM roles WHERE username = 'nebulosa'")
            conn.commit()
            print("  → Eliminada de roles de admin")
        else:
            print("✓ No encontrada en tabla 'roles' (ya no es admin)")
        
        conn.close()
    except Exception as e:
        print(f"✗ Error al procesar rights.db: {e}")
    
    print()
    
    # 2. Verificar en opo_players (mantener si fue añadida manualmente)
    try:
        conn = sqlite3.connect(DB_RIGHTS)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM opo_players WHERE username = 'nebulosa'")
        opo = cursor.fetchone()
        
        if opo:
            print("✓ Encontrada en 'opo_players'")
            print("  → Manteniendo acceso a OPO (puede ser removido manualmente si se desea)")
        else:
            print("✓ No encontrada en 'opo_players'")
        
        conn.close()
    except Exception as e:
        print(f"✗ Error al verificar opo_players: {e}")
    
    print()
    
    # 3. Verificar usuario en users.db (mantener como usuario normal)
    try:
        conn = sqlite3.connect(DB_USERS)
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, balance, is_blocked FROM users WHERE username = 'nebulosa'")
        user = cursor.fetchone()
        
        if user:
            print("✓ Usuario 'nebulosa' existe en users.db")
            print(f"  → Balance: {user[1]}")
            print(f"  → Bloqueado: {'Sí' if user[2] else 'No'}")
            print("  → Manteniendo como usuario normal")
        else:
            print("✓ Usuario 'nebulosa' no existe en la base de datos")
        
        conn.close()
    except Exception as e:
        print(f"✗ Error al verificar users.db: {e}")
    
    print()
    print("=" * 70)
    print("PROCESO COMPLETADO")
    print("=" * 70)
    print()
    print("CAMBIOS REALIZADOS:")
    print("  1. Eliminada de roles de admin (si existía)")
    print("  2. Mantenida como usuario normal en users.db")
    print("  3. Código actualizado para remover privilegios de superadmin")
    print()
    print("NOTA: Reinicia el servidor para aplicar los cambios en el código.")
    print()


def show_current_status():
    """Muestra el estado actual de nebulosa en las bases de datos."""
    
    print("=" * 70)
    print("ESTADO ACTUAL DE NEBULOSA EN LA BASE DE DATOS")
    print("=" * 70)
    print()
    
    # Users
    try:
        conn = sqlite3.connect(DB_USERS)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = 'nebulosa'")
        user = cursor.fetchone()
        if user:
            print("✓ users.db: EXISTE")
            print(f"  Columnas: {[desc[0] for desc in cursor.description]}")
            print(f"  Datos: {user}")
        else:
            print("✗ users.db: NO EXISTE")
        conn.close()
    except Exception as e:
        print(f"✗ Error en users.db: {e}")
    
    print()
    
    # Rights - roles
    try:
        conn = sqlite3.connect(DB_RIGHTS)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM roles WHERE username = 'nebulosa'")
        role = cursor.fetchone()
        if role:
            print("✓ rights.db (roles): EXISTE")
            print(f"  Datos: {role}")
        else:
            print("✗ rights.db (roles): NO EXISTE")
        conn.close()
    except Exception as e:
        print(f"✗ Error en rights.db (roles): {e}")
    
    print()
    
    # Rights - opo_players
    try:
        conn = sqlite3.connect(DB_RIGHTS)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM opo_players WHERE username = 'nebulosa'")
        opo = cursor.fetchone()
        if opo:
            print("✓ rights.db (opo_players): EXISTE")
            print(f"  Datos: {opo}")
        else:
            print("✗ rights.db (opo_players): NO EXISTE")
        conn.close()
    except Exception as e:
        print(f"✗ Error en rights.db (opo_players): {e}")
    
    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        show_current_status()
    else:
        print()
        print("Este script eliminará los privilegios de superadmin de 'nebulosa'")
        print("manteniéndola como usuario normal.")
        print()
        response = input("¿Deseas continuar? (s/n): ")
        
        if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            print()
            remove_nebulosa_privileges()
        else:
            print()
            print("Operación cancelada.")
            print()
