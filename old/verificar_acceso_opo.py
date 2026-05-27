#!/usr/bin/env python3
"""
Script para verificar y gestionar acceso a OPO
"""
import sqlite3
import sys

def verificar_opo():
    """Verifica quién tiene acceso a OPO"""
    print("\n" + "="*60)
    print("  VERIFICACIÓN DE ACCESO A OPO")
    print("="*60 + "\n")
    
    # Conectar a la base de datos
    conn = sqlite3.connect("data/rights.db")
    conn.row_factory = sqlite3.Row
    
    # Obtener usuarios con acceso
    rows = conn.execute("""
        SELECT username, added_by, added_at 
        FROM opo_players 
        ORDER BY username
    """).fetchall()
    
    print("👥 Usuarios con acceso a OPO:")
    print("-" * 60)
    
    # Superadmins siempre tienen acceso
    print("  ✓ dvd (superadmin - acceso permanente)")
    print("  ✓ nebulosa (superadmin - acceso permanente)")
    
    if rows:
        for row in rows:
            print(f"  ✓ {row['username']} (añadido por {row['added_by']} el {row['added_at']})")
    else:
        print("\n  (No hay usuarios adicionales con acceso)")
    
    conn.close()
    
    print("\n" + "="*60)
    print("  Para agregar usuarios, usa el panel de admin en /")
    print("  o ejecuta: python agregar_usuario_opo.py <username>")
    print("="*60 + "\n")

def agregar_usuario(username):
    """Agrega un usuario a OPO"""
    username = username.strip().lower()
    
    if username in ["dvd", "nebulosa"]:
        print(f"\n❌ {username} ya tiene acceso permanente como superadmin\n")
        return
    
    # Verificar que el usuario existe
    conn_users = sqlite3.connect("data/users.db")
    conn_users.row_factory = sqlite3.Row
    user_row = conn_users.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
    conn_users.close()
    
    if not user_row:
        print(f"\n❌ El usuario '{username}' no existe en el sistema\n")
        return
    
    # Agregar a OPO
    conn = sqlite3.connect("data/rights.db")
    try:
        conn.execute("""
            INSERT OR IGNORE INTO opo_players(username, added_by, added_at)
            VALUES(?, 'dvd', datetime('now'))
        """, (username,))
        conn.commit()
        
        # Verificar si se insertó
        if conn.total_changes > 0:
            print(f"\n✅ Usuario '{username}' agregado a OPO exitosamente\n")
        else:
            print(f"\n⚠️  Usuario '{username}' ya tenía acceso a OPO\n")
    except Exception as e:
        print(f"\n❌ Error al agregar usuario: {e}\n")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Agregar usuario
        agregar_usuario(sys.argv[1])
    else:
        # Solo verificar
        verificar_opo()
