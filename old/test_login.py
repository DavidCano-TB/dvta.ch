import sqlite3
import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False

# Test con usuario dvd
username = "dvd"
password = "dvd"  # Contraseña por defecto

conn = sqlite3.connect('data/dvdcoin.db')
conn.row_factory = sqlite3.Row
row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
conn.close()

if row:
    print(f"✓ Usuario '{username}' encontrado en la base de datos")
    print(f"  Password hash: {row['password_hash'][:50]}...")
    print(f"  Balance: {row['balance']}")
    print(f"  Blocked: {row['is_blocked']}")
    
    # Probar verificación de contraseña
    print(f"\nProbando contraseña '{password}'...")
    if verify_password(password, row['password_hash']):
        print("✓ Contraseña correcta!")
    else:
        print("❌ Contraseña incorrecta")
        
        # Probar otras contraseñas comunes
        common_passwords = ["dvd", "1234", "admin", "password", "dvd2024", "dvd2026"]
        print("\nProbando contraseñas comunes...")
        for pwd in common_passwords:
            if verify_password(pwd, row['password_hash']):
                print(f"✓ Contraseña encontrada: '{pwd}'")
                break
        else:
            print("❌ Ninguna contraseña común funciona")
            print("\nGenerando nuevo hash para 'dvd'...")
            new_hash = bcrypt.hashpw("dvd".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            print(f"Nuevo hash: {new_hash}")
            
            # Actualizar en la base de datos
            conn = sqlite3.connect('data/dvdcoin.db')
            conn.execute("UPDATE users SET password_hash=? WHERE username=?", (new_hash, username))
            conn.commit()
            conn.close()
            print("✓ Contraseña actualizada en la base de datos")
else:
    print(f"❌ Usuario '{username}' NO encontrado en la base de datos")
