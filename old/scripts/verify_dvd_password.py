#!/usr/bin/env python3
import sqlite3
import bcrypt
import os
import glob

def check_password(db_path, username, password):
    """Verifica si una contraseña es correcta para un usuario"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return False, "Usuario no encontrado"
        
        pwd_hash = row[0]
        if pwd_hash in ("__UNSET__", "__AUTO__"):
            return False, "Contraseña no configurada"
        
        try:
            if bcrypt.checkpw(password.encode('utf-8'), pwd_hash.encode('utf-8')):
                return True, "Contraseña correcta"
            else:
                return False, "Contraseña incorrecta"
        except Exception as e:
            return False, f"Error al verificar: {e}"
    except Exception as e:
        return False, f"Error al abrir DB: {e}"

# Verificar base de datos actual
print("=" * 70)
print("VERIFICANDO CONTRASEÑA DE 'dvd' = '3666'")
print("=" * 70)

current_db = "data/users.db"
is_correct, msg = check_password(current_db, "dvd", "3666")

print(f"\n[ACTUAL] {current_db}")
print(f"  Estado: {msg}")
print(f"  ✓ CORRECTO" if is_correct else f"  ✗ INCORRECTO")

if is_correct:
    print("\n✅ La contraseña actual ya es '3666'. No se necesita restaurar.")
    exit(0)

# Buscar en backups
print("\n" + "=" * 70)
print("BUSCANDO EN BACKUPS...")
print("=" * 70)

backup_locations = [
    "backup/*/users.db",
    "backup_30min/*/users.db",
    "BACKUP_*/*/users.db",
    "BACKUP_*/dvdcoin backup/data/users.db",
]

found_backups = []
for pattern in backup_locations:
    found_backups.extend(glob.glob(pattern))

if not found_backups:
    print("\n✗ No se encontraron backups de users.db")
    exit(1)

print(f"\nEncontrados {len(found_backups)} backups")

# Verificar cada backup
valid_backup = None
for backup_path in found_backups:
    is_correct, msg = check_password(backup_path, "dvd", "3666")
    status = "✓" if is_correct else "✗"
    print(f"\n{status} {backup_path}")
    print(f"  {msg}")
    
    if is_correct and not valid_backup:
        valid_backup = backup_path

if valid_backup:
    print("\n" + "=" * 70)
    print("✅ BACKUP VÁLIDO ENCONTRADO")
    print("=" * 70)
    print(f"\nBackup: {valid_backup}")
    print(f"\nPara restaurar, ejecuta:")
    print(f"  copy \"{valid_backup}\" data\\users.db")
else:
    print("\n" + "=" * 70)
    print("✗ NO SE ENCONTRÓ NINGÚN BACKUP CON LA CONTRASEÑA '3666'")
    print("=" * 70)
    print("\nOpciones:")
    print("  1. Usar las credenciales actuales (admin/dvd_ghost_2026)")
    print("  2. Cambiar la contraseña manualmente")
    exit(1)
