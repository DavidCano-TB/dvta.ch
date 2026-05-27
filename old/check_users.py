import sqlite3

conn = sqlite3.connect('data/dvdcoin.db')
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT username, password_hash, balance, is_blocked FROM users').fetchall()

print("=== USUARIOS EN LA BASE DE DATOS ===")
for r in rows:
    print(f"{r['username']}: hash={r['password_hash'][:30]}..., balance={r['balance']}, blocked={r['is_blocked']}")

conn.close()
