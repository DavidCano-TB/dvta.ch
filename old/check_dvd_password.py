import sqlite3

conn = sqlite3.connect('data/users.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT username, password_hash FROM users WHERE username='dvd'")
row = cursor.fetchone()

if row:
    print(f"Usuario: {row['username']}")
    print(f"Password hash: {row['password_hash'][:50]}..." if len(row['password_hash']) > 50 else f"Password hash: {row['password_hash']}")
    
    if row['password_hash'] in ('__UNSET__', '__AUTO__'):
        print("\n⚠️  Usuario sin contraseña configurada")
        print("   Debe usar la contraseña por defecto o configurar una")
    else:
        print("\n✅ Usuario tiene contraseña configurada")
else:
    print("❌ Usuario 'dvd' no encontrado")

conn.close()
