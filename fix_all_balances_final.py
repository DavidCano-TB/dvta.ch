# Final balance fix script
# Problem: src/data/users.db has inflated balances (victorzahyr: 1182, nina_user: 1025)
# The active DB is data/users.db (used by main.py in root)
# Solution: Recalculate correct balances from data/transactions.db and apply to BOTH databases
import sqlite3

TX_DB = 'c:/dvdcoin/data/transactions.db'
USERS_DB_ACTIVE = 'c:/dvdcoin/data/users.db'
USERS_DB_SRC = 'c:/dvdcoin/src/data/users.db'

ADMINS = {'dvd', 'admin', 'aitor'}

# Step 1: Load all transactions
tx_conn = sqlite3.connect(TX_DB)
tx_conn.row_factory = sqlite3.Row
transactions = tx_conn.execute("SELECT * FROM transactions ORDER BY id").fetchall()
tx_conn.close()
print(f"Transactions loaded: {len(transactions)}")

# Step 2: Recalculate balances
calculated = {}
for tx in transactions:
    from_u = tx['from_user']
    to_u = tx['to_user']
    amount = tx['amount']
    
    # Deduct from sender (skip admins and system sources)
    if from_u not in ADMINS and not from_u.startswith('Porra:') and from_u != 'sistema':
        calculated[from_u] = calculated.get(from_u, 0.0) - amount
    
    # Credit to receiver (skip admins and system/porra targets)
    if to_u not in ADMINS and not to_u.startswith('Porra:') and to_u != 'sistema':
        calculated[to_u] = calculated.get(to_u, 0.0) + amount

# Ensure no negative balances
for u in calculated:
    if calculated[u] < 0:
        calculated[u] = 0.0

# Admin balances always 0
for u in ADMINS:
    calculated[u] = 0.0

# Step 3: Apply to BOTH databases
for db_path in [USERS_DB_ACTIVE, USERS_DB_SRC]:
    print(f"\nFixing: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Get existing users
    existing = conn.execute('SELECT username, balance FROM users').fetchall()
    
    for row in existing:
        username = row['username']
        old_balance = row['balance']
        new_balance = round(calculated.get(username, 0.0), 4)
        
        if abs(old_balance - new_balance) > 0.001:
            conn.execute("UPDATE users SET balance=? WHERE username=?", (new_balance, username))
            print(f"  {username}: {old_balance:.4f} -> {new_balance:.4f}")
    
    # Also ensure users that exist in transactions but not in users table get created
    for username in calculated:
        if username not in ADMINS and calculated[username] > 0:
            existing_user = conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone()
            if not existing_user:
                conn.execute("INSERT INTO users(username, password_hash, balance) VALUES(?, '__AUTO__', ?)",
                           (username, round(calculated[username], 4)))
                print(f"  CREATED {username}: {calculated[username]:.4f}")
    
    conn.commit()
    conn.close()

# Step 4: Also sync src/data/transactions.db with data/transactions.db
print("\nSyncing src/data/transactions.db...")
import shutil
shutil.copy2(TX_DB, 'c:/dvdcoin/src/data/transactions.db')
print("  Copied data/transactions.db -> src/data/transactions.db")

# Step 5: Final verification
print("\n\n=== FINAL BALANCES (data/users.db - ACTIVE) ===")
conn = sqlite3.connect(USERS_DB_ACTIVE)
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT username, balance FROM users ORDER BY balance DESC').fetchall()
for r in rows:
    if r['balance'] > 0:
        print(f"  {r['username']:25s} {r['balance']:>12.4f}")
conn.close()

print("\n=== FINAL BALANCES (src/data/users.db) ===")
conn = sqlite3.connect(USERS_DB_SRC)
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT username, balance FROM users ORDER BY balance DESC').fetchall()
for r in rows:
    if r['balance'] > 0:
        print(f"  {r['username']:25s} {r['balance']:>12.4f}")
conn.close()
