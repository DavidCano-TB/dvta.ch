import sqlite3
import os

print("=== src/data/users.db ===")
conn = sqlite3.connect('c:/dvdcoin/src/data/users.db')
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT username, balance FROM users ORDER BY balance DESC LIMIT 5').fetchall()
for r in rows:
    print(f"  {r['username']}: {r['balance']}")
print(f"  Last modified: {os.path.getmtime('c:/dvdcoin/src/data/users.db')}")
conn.close()

print("\n=== data/users.db ===")
conn = sqlite3.connect('c:/dvdcoin/data/users.db')
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT username, balance FROM users ORDER BY balance DESC LIMIT 5').fetchall()
for r in rows:
    print(f"  {r['username']}: {r['balance']}")
print(f"  Last modified: {os.path.getmtime('c:/dvdcoin/data/users.db')}")
conn.close()

print("\n=== src/data/transactions.db ===")
conn = sqlite3.connect('c:/dvdcoin/src/data/transactions.db')
count = conn.execute('SELECT COUNT(*) FROM transactions').fetchone()[0]
print(f"  Count: {count}")
conn.close()

print("\n=== data/transactions.db ===")
conn = sqlite3.connect('c:/dvdcoin/data/transactions.db')
conn.row_factory = sqlite3.Row
count = conn.execute('SELECT COUNT(*) FROM transactions').fetchone()[0]
last = conn.execute('SELECT * FROM transactions ORDER BY id DESC LIMIT 1').fetchone()
print(f"  Count: {count}")
if last:
    print(f"  Last tx: {dict(last)}")
conn.close()

# Check which main.py is actually running
print("\n=== main.py locations ===")
for p in ['c:/dvdcoin/main.py', 'c:/dvdcoin/src/main.py']:
    if os.path.exists(p):
        print(f"  EXISTS: {p} (size: {os.path.getsize(p)})")

# Check ARRANCAR.bat to see which one is launched
print("\n=== ARRANCAR.bat ===")
with open('c:/dvdcoin/ARRANCAR.bat', 'r') as f:
    print(f.read())
