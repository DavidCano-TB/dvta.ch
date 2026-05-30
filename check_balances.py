import sqlite3

conn = sqlite3.connect('c:/dvdcoin/src/data/users.db')
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT username, balance FROM users ORDER BY balance DESC').fetchall()
print(f"{'USERNAME':20s} {'BALANCE':>12s}")
print("-" * 34)
for r in rows:
    print(f"{r['username']:20s} {r['balance']:>12.4f}")
conn.close()
