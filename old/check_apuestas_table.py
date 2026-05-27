import sqlite3

conn = sqlite3.connect('data/apuestas.db')
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(apuestas_usuarios)')
columns = cursor.fetchall()
print('apuestas_usuarios columns:')
for col in columns:
    print(f'  {col}')

cursor.execute('SELECT * FROM apuestas_usuarios WHERE porra_id=7')
rows = cursor.fetchall()
print(f'\nRows for porra 7: {len(rows)}')
for row in rows:
    print(f'  {row}')

conn.close()
