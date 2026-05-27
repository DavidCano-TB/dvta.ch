import sqlite3
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

conn = sqlite3.connect('data/dvdcoin.db')
conn.row_factory = sqlite3.Row

# Obtener todos los usuarios
rows = conn.execute("SELECT username FROM users").fetchall()

print("=== RESETEANDO CONTRASEÑAS PARA TODOS LOS USUARIOS ===")
print(f"Total usuarios: {len(rows)}\n")

updated = 0
for row in rows:
    username = row['username']
    # La contraseña será igual al nombre de usuario
    password = username
    
    new_hash = hash_password(password)
    conn.execute("UPDATE users SET password_hash=? WHERE username=?", (new_hash, username))
    print(f"✓ {username}: contraseña = '{password}'")
    updated += 1

conn.commit()
conn.close()

print(f"\n=== COMPLETADO ===")
print(f"✓ {updated} contraseñas actualizadas")
print("\nTodos los usuarios ahora tienen como contraseña su propio nombre de usuario.")
