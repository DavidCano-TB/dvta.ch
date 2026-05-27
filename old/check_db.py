import sqlite3

conn = sqlite3.connect('apuestas.db')
cursor = conn.cursor()

# Ver todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tablas en la base de datos:")
for table in tables:
    print(f"  - {table[0]}")

# Ver usuarios si existe la tabla
try:
    cursor.execute("SELECT username, password FROM usuarios LIMIT 5")
    users = cursor.fetchall()
    print("\nUsuarios:")
    for user in users:
        print(f"  - {user[0]}")
except:
    print("\nNo se pudo leer la tabla usuarios")

conn.close()
