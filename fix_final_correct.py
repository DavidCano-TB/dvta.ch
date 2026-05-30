# Final correct fix: recalculate balances excluding the erroneous
# pasapalabra payments of 500 and 1000 (which should have been 50 and 100)
# 
# The pattern shows pasapalabra prizes were normally 10-100 DVDcoins.
# On May 9 and May 18, prizes of 500 and 1000 were given - these are 10x errors.
# We'll reduce them to 1/10th of their value.
import sqlite3

TX_DB = 'c:/dvdcoin/data/transactions.db'
USERS_DB_ACTIVE = 'c:/dvdcoin/data/users.db'
USERS_DB_SRC = 'c:/dvdcoin/src/data/users.db'

ADMINS = {'dvd', 'admin', 'aitor'}

# Load transactions
tx_conn = sqlite3.connect(TX_DB)
tx_conn.row_factory = sqlite3.Row
transactions = tx_conn.execute("SELECT * FROM transactions ORDER BY id").fetchall()
tx_conn.close()

# Erroneous transactions (pasapalabra with amounts >= 500)
# These should be reduced to 1/10th
ERRONEOUS_TXS = {
    # (from_user, to_user, amount, created_at) -> corrected_amount
    ('dvd', 'nina_user', 1000.0, '2026-05-09 03:01:18'): 100.0,
    ('dvd', 'yumazurman', 500.0, '2026-05-09 03:01:35'): 50.0,
    ('dvd', 'victorzahyr', 1000.0, '2026-05-09 20:53:45'): 100.0,
    ('dvd', 'yumazurman', 500.0, '2026-05-18 01:00:34'): 50.0,
    ('dvd', 'victorzahyr', 200.0, '2026-05-18 01:00:47'): 200.0,  # 200 is ok
    ('dvd', 'mariterevr', 200.0, '2026-05-18 01:00:55'): 200.0,   # 200 is ok
    ('dvd', 'dianelau', 200.0, '2026-05-18 01:01:11'): 200.0,     # 200 is ok
    ('dvd', 'markus (polyglot)', 200.0, '2026-05-18 01:01:21'): 200.0,  # 200 is ok
}

print("Recalculating with corrected pasapalabra amounts...")
print("Corrections applied:")
for key, corrected in ERRONEOUS_TXS.items():
    if key[2] != corrected:
        print(f"  {key[1]}: {key[2]:.0f} -> {corrected:.0f} ({key[3]})")

# Recalculate
calculated = {}
for tx in transactions:
    from_u = tx['from_user']
    to_u = tx['to_user']
    amount = tx['amount']
    
    # Check if this is an erroneous transaction
    key = (from_u, to_u, amount, tx['created_at'])
    if key in ERRONEOUS_TXS:
        amount = ERRONEOUS_TXS[key]
    
    # Deduct from sender
    if from_u not in ADMINS and not from_u.startswith('Porra:') and from_u != 'sistema':
        calculated[from_u] = calculated.get(from_u, 0.0) - amount
    
    # Credit to receiver
    if to_u not in ADMINS and not to_u.startswith('Porra:') and to_u != 'sistema':
        calculated[to_u] = calculated.get(to_u, 0.0) + amount

# No negative balances
for u in calculated:
    if calculated[u] < 0:
        calculated[u] = 0.0

# Admin balances always 0
for u in ADMINS:
    calculated[u] = 0.0

# Apply to both databases
for db_path in [USERS_DB_ACTIVE, USERS_DB_SRC]:
    print(f"\nUpdating: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    existing = conn.execute('SELECT username, balance FROM users').fetchall()
    for row in existing:
        username = row['username']
        old_balance = row['balance']
        new_balance = round(calculated.get(username, 0.0), 4)
        if abs(old_balance - new_balance) > 0.001:
            conn.execute("UPDATE users SET balance=? WHERE username=?", (new_balance, username))
            print(f"  {username}: {old_balance:.4f} -> {new_balance:.4f}")
    
    # Create missing users
    for username in calculated:
        if username not in ADMINS and calculated[username] > 0:
            existing_user = conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone()
            if not existing_user:
                conn.execute("INSERT INTO users(username, password_hash, balance) VALUES(?, '__AUTO__', ?)",
                           (username, round(calculated[username], 4)))
                print(f"  CREATED {username}: {calculated[username]:.4f}")
    
    conn.commit()
    conn.close()

# Also fix the transaction amounts in the DB
print("\nCorrecting transaction amounts in data/transactions.db...")
tx_conn = sqlite3.connect(TX_DB)
for key, corrected in ERRONEOUS_TXS.items():
    if key[2] != corrected:
        tx_conn.execute(
            "UPDATE transactions SET amount=? WHERE from_user=? AND to_user=? AND amount=? AND created_at=?",
            (corrected, key[0], key[1], key[2], key[3])
        )
        print(f"  TX fixed: {key[1]} {key[2]:.0f} -> {corrected:.0f}")
tx_conn.commit()
tx_conn.close()

# Copy fixed transactions to src
import shutil
shutil.copy2(TX_DB, 'c:/dvdcoin/src/data/transactions.db')

# Final verification
print("\n\n=== FINAL CORRECTED BALANCES ===")
conn = sqlite3.connect(USERS_DB_ACTIVE)
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT username, balance FROM users ORDER BY balance DESC').fetchall()
print(f"{'USERNAME':25s} {'BALANCE':>12s}")
print("-" * 40)
for r in rows:
    if r['balance'] > 0:
        flag = " *** >1000 ***" if r['balance'] > 1000 else ""
        print(f"  {r['username']:25s} {r['balance']:>12.4f}{flag}")
conn.close()
