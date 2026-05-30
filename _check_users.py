import sqlite3, os

# Check all possible user database locations
paths = [
    r"c:\dvdcoin\users.db",
    r"c:\dvdcoin\data\users.db",
    r"c:\dvdcoin\dvdcoin.db",
    r"c:\dvdcoin\data\dvdcoin.db",
]

for db_path in paths:
    if not os.path.exists(db_path):
        continue
    print(f"\n{'='*60}")
    print(f"DB: {db_path} ({os.path.getsize(db_path)} bytes)")
    print(f"{'='*60}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"Tables: {tables}")
    
    if 'users' in tables:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
        print(f"Columns: {cols}")
        users = conn.execute("SELECT * FROM users LIMIT 10").fetchall()
        print(f"Users ({len(users)}):")
        for u in users:
            d = dict(u)
            # Mask password hash but show first 10 chars
            if 'password' in d and d['password']:
                d['password'] = d['password'][:15] + '...'
            if 'password_hash' in d and d['password_hash']:
                d['password_hash'] = d['password_hash'][:15] + '...'
            print(f"  {d}")
    conn.close()
