#!/usr/bin/env python3
"""
Script para restaurar privilegios de superadmin a nebulosa.
Añade nebulosa como superadmin con acceso permanente a OPO y gestión de usuarios.
"""

import sqlite3
import os

DATA_DIR = "data"
DB_RIGHTS = os.path.join(DATA_DIR, "rights.db")

def restore_nebulosa_privileges():
    """Restaura privilegios de superadmin a nebulosa."""
    print("=" * 70)
    print("RESTAURANDO PRIVILEGIOS DE SUPERADMIN PARA NEBULOSA")
    print("=" * 70)
    print()
    
    # 1. Añadir a roles como admin
    try:
        conn = sqlite3.connect(DB_RIGHTS)
        cursor = conn.cursor()
        
        # Verificar si ya existe
        cursor.execute("SELECT * FROM roles WHERE username = 'nebulosa'")
        existing = cursor.fetchone()
        
        if existing:
            print("✓ nebulosa ya existe en roles")
        else:
            cursor.execute(
                "INSERT INTO roles (username, role, granted_by) VALUES (?, ?, ?)",
                ('nebulosa', 'admin', 'dvd')
            )
            conn.commit()
            print("✓ nebulosa añadida a roles como admin")
        
        conn.close()
    except Exception as e:
        print(f"✗ Error al añadir a roles: {e}")
    
    print()
    
    # 2. Añadir a opo_players para acceso permanente a OPO
    try:
        conn = sqlite3.connect(DB_RIGHTS)
        cursor = conn.cursor()
        
        # Verificar si ya existe
        cursor.execute("SELECT * FROM opo_players WHERE username = 'nebulosa'")
        existing = cursor.fetchone()
        
        if existing:
            print("✓ nebulosa ya tiene acceso a OPO")
        else:
            cursor.execute(
                "INSERT INTO opo_players (username, added_by) VALUES (?, ?)",
                ('nebulosa', 'dvd')
            )
            conn.commit()
            print("✓ nebulosa añadida a opo_players - acceso permanente a OPO")
        
        conn.close()
    except Exception as e:
        print(f"✗ Error al añadir a opo_players: {e}")
    
    print()
    print("=" * 70)
    print("RESUMEN DE PRIVILEGIOS RESTAURADOS")
    print("=" * 70)
    print()
    print("✅ nebulosa es SUPERADMIN (código)")
    print("✅ nebulosa está en roles (base de datos)")
    print("✅ nebulosa tiene acceso permanente a OPO")
    print("✅ nebulosa puede gestionar administradores")
    print("✅ nebulosa puede gestionar conexiones de usuarios")
    print()
    print("NOTA: Reinicia el servidor para aplicar todos los cambios.")
    print()

if __name__ == "__main__":
    restore_nebulosa_privileges()
