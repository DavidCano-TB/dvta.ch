import sqlite3
import os

db_path = 'data/users.db'

if not os.path.exists(db_path):
    print(f"❌ Base de datos no existe: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Ver todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tablas en data/users.db:")
for table in tables:
    print(f"  - {table['name']}")

# Ver usuarios
try:
    cursor.execute("SELECT username FROM users LIMIT 10")
    users = cursor.fetchall()
    print(f"\nUsuarios encontrados: {len(users)}")
    for user in users:
        print(f"  - {user['username']}")
except Exception as e:
    print(f"\n❌ Error al leer usuarios: {e}")

conn.close()
