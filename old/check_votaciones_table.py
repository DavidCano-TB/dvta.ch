import sqlite3

conn = sqlite3.connect('apuestas.db')
cursor = conn.cursor()

print("=== Estructura de la tabla votaciones ===")
cursor.execute('PRAGMA table_info(votaciones)')
columns = cursor.fetchall()

if not columns:
    print("❌ La tabla votaciones NO EXISTE")
else:
    print("\nColumnas actuales:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

conn.close()
