import sqlite3
import shutil
from datetime import datetime

# Ruta del backup más reciente
backup_path = r"BACKUP_ANTES_LIMPIEZA_20260514_162538\dvdcoin backup\data\dvdcoin.db"
current_path = r"data\dvdcoin.db"

print("=== RESTAURANDO CONTRASEÑAS DESDE BACKUP ===")
print(f"Backup: {backup_path}")
print(f"Actual: {current_path}\n")

# Conectar a ambas bases de datos
conn_backup = sqlite3.connect(backup_path)
conn_backup.row_factory = sqlite3.Row

conn_current = sqlite3.connect(current_path)
conn_current.row_factory = sqlite3.Row

# Obtener todos los usuarios del backup
backup_users = conn_backup.execute("SELECT username, password_hash FROM users").fetchall()

print(f"Usuarios en backup: {len(backup_users)}")

# Restaurar contraseñas
restored = 0
created = 0
skipped = 0

for user in backup_users:
    username = user['username']
    password_hash = user['password_hash']
    
    # Verificar si el usuario existe en la base actual
    current_user = conn_current.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
    
    if current_user:
        # Actualizar contraseña
        conn_current.execute("UPDATE users SET password_hash=? WHERE username=?", (password_hash, username))
        print(f"✓ {username}: contraseña restaurada")
        restored += 1
    else:
        # Crear usuario con todos los datos del backup
        backup_full = conn_backup.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        
        # Insertar usuario completo
        conn_current.execute("""
            INSERT INTO users(username, password_hash, balance, is_blocked, lang_pref, created_at)
            VALUES(?,?,?,?,?,?)
        """, (
            backup_full['username'],
            backup_full['password_hash'],
            backup_full['balance'] if 'balance' in backup_full.keys() else 0.0,
            backup_full['is_blocked'] if 'is_blocked' in backup_full.keys() else 0,
            backup_full['lang_pref'] if 'lang_pref' in backup_full.keys() else 'en',
            backup_full['created_at'] if 'created_at' in backup_full.keys() else datetime.now().isoformat()
        ))
        print(f"✓ {username}: usuario creado desde backup")
        created += 1

conn_current.commit()

# Cerrar conexiones
conn_backup.close()
conn_current.close()

print(f"\n=== COMPLETADO ===")
print(f"✓ {restored} contraseñas restauradas")
print(f"✓ {created} usuarios creados desde backup")
print(f"Total procesado: {restored + created}")
