import sqlite3
import os
from datetime import datetime

# The ARRANCAR.bat runs: python main.py (from c:\dvdcoin\)
# main.py has: BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# So BASE_DIR = c:\dvdcoin\ and DATA_DIR = c:\dvdcoin\data\

# But src/main.py has the same structure, so if run from src/, it uses src/data/

# Let's check modification times to see which was last written
files = [
    'c:/dvdcoin/data/users.db',
    'c:/dvdcoin/src/data/users.db',
    'c:/dvdcoin/data/transactions.db',
    'c:/dvdcoin/src/data/transactions.db',
]

print("File modification times:")
for f in files:
    if os.path.exists(f):
        mtime = os.path.getmtime(f)
        dt = datetime.fromtimestamp(mtime)
        size = os.path.getsize(f)
        print(f"  {f:45s} {dt.strftime('%Y-%m-%d %H:%M:%S')} ({size} bytes)")

# The key question: which users.db has the most recent user activity?
print("\n\ndata/users.db - last created user:")
conn = sqlite3.connect('c:/dvdcoin/data/users.db')
conn.row_factory = sqlite3.Row
row = conn.execute("SELECT username, created_at FROM users ORDER BY created_at DESC LIMIT 3").fetchall()
for r in row:
    print(f"  {r['username']}: {r['created_at']}")
conn.close()

print("\nsrc/data/users.db - last created user:")
conn = sqlite3.connect('c:/dvdcoin/src/data/users.db')
conn.row_factory = sqlite3.Row
row = conn.execute("SELECT username, created_at FROM users ORDER BY created_at DESC LIMIT 3").fetchall()
for r in row:
    print(f"  {r['username']}: {r['created_at']}")
conn.close()

# Check if there's a symlink or if they're the same file
print(f"\nSame file? {os.path.samefile('c:/dvdcoin/data/users.db', 'c:/dvdcoin/src/data/users.db') if os.path.exists('c:/dvdcoin/data/users.db') and os.path.exists('c:/dvdcoin/src/data/users.db') else 'N/A'}")
