import sqlite3
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Usuarios y contraseñas por defecto
users_passwords = {
    "dvd": "dvd",
    "nebulosa": "nebulosa",
    "nina": "nina",
    "victor": "victor",
    "yu": "yu",
    "roy": "roy",
    "admin": "admin"
}

conn = sqlite3.connect('data/dvdcoin.db')

print("=== ACTUALIZANDO CONTRASEÑAS ===")
for username, password in users_passwords.items():
    # Verificar si el usuario existe
    row = conn.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
    
    if row:
        # Actualizar contraseña
        new_hash = hash_password(password)
        conn.execute("UPDATE users SET password_hash=? WHERE username=?", (new_hash, username))
        print(f"✓ {username}: contraseña actualizada a '{password}'")
    else:
        # Crear usuario si no existe
        new_hash = hash_password(password)
        conn.execute("INSERT INTO users(username, password_hash, balance, is_blocked) VALUES(?,?,0.0,0)", 
                    (username, new_hash))
        print(f"✓ {username}: usuario creado con contraseña '{password}'")

conn.commit()
conn.close()

print("\n=== CONTRASEÑAS ACTUALIZADAS ===")
print("Usuarios y contraseñas:")
for username, password in users_passwords.items():
    print(f"  {username}: {password}")
