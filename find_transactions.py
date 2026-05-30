"""Find all transaction databases and check their contents."""
import sqlite3
import os
import glob

# Check all possible transaction DB locations
paths_to_check = [
    'c:/dvdcoin/src/data/transactions.db',
    'c:/dvdcoin/transactions.db',
    'c:/dvdcoin/data/transactions.db',
    'c:/dvdcoin/dvdcoin.db',
]

# Also check backup
for p in glob.glob('c:/dvdcoin/backup/**/*.db', recursive=True):
    paths_to_check.append(p)

for path in paths_to_check:
    if os.path.exists(path):
        try:
            conn = sqlite3.connect(path)
            # List tables
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [t[0] for t in tables]
            print(f"\n{'='*60}")
            print(f"DB: {path}")
            print(f"Tables: {table_names}")
            
            if 'transactions' in table_names:
                count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
                print(f"  transactions count: {count}")
                if count > 0:
                    conn.row_factory = sqlite3.Row
                    sample = conn.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 5").fetchall()
                    for s in sample:
                        print(f"    {dict(s)}")
            
            if 'users' in table_names:
                conn.row_factory = sqlite3.Row
                users = conn.execute("SELECT username, balance FROM users ORDER BY balance DESC LIMIT 10").fetchall()
                print(f"  Top users by balance:")
                for u in users:
                    print(f"    {u['username']}: {u['balance']}")
            conn.close()
        except Exception as e:
            print(f"  Error: {e}")
