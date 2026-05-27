import sqlite3

conn = sqlite3.connect('data/apuestas.db')
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print(f'Tables: {tables}')

# Get porra 7 info
cursor.execute('PRAGMA table_info(porras)')
columns = [c[1] for c in cursor.fetchall()]
print(f'\nPorras columns: {columns}')

cursor.execute('SELECT * FROM porras WHERE id=7')
row = cursor.fetchone()
print(f'\nPorra 7 data: {row}')

# Update to abierta
cursor.execute("UPDATE porras SET estado='abierta' WHERE id=7")
conn.commit()

cursor.execute('SELECT * FROM porras WHERE id=7')
row = cursor.fetchone()
print(f'\nPorra 7 updated: {row}')

conn.close()
print('\nDone!')
