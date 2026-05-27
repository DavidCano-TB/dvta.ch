import sqlite3

c = sqlite3.connect('data/apuestas.db')
c.row_factory = sqlite3.Row

rows = c.execute('SELECT username, COUNT(*) as total FROM apuestas_usuarios GROUP BY username').fetchall()
print('Bets by user:')
for r in rows:
    print(f'{r["username"]}: {r["total"]} bets')

c.close()
