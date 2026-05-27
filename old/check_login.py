import sqlite3
import bcrypt

# Verificar usuarios y contraseñas
conn = sqlite3.connect('data/users.db')
cursor = conn.cursor()

print("=" * 60)
print("USUARIOS EN LA BASE DE DATOS")
print("=" * 60)

cursor.execute("SELECT username, password_hash FROM users ORDER BY username")
users = cursor.fetchall()

for username, pwd_hash in users:
    print(f"\nUsuario: {username}")
    print(f"Hash: {pwd_hash[:50]}...")
    
    # Probar contraseñas comunes
    common_passwords = [username, "1234", "admin", "password", "dvd"]
    for pwd in common_passwords:
        try:
            if bcrypt.checkpw(pwd.encode('utf-8'), pwd_hash.encode('utf-8')):
                print(f"  ✓ Contraseña encontrada: '{pwd}'")
                break
        except:
            pass

conn.close()

print("\n" + "=" * 60)
print("MASTER PASSWORD (emergencia)")
print("=" * 60)
try:
    with open('conf/master.txt', 'r') as f:
        master = f.read().strip()
        print(f"Master password: {master}")
        print("Usuarios: dvd, nebulosa")
except:
    print("No se encontró master password")
