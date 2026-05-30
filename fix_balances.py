# Fix balances in the ACTIVE database (data/users.db) by recalculating
# from the transaction history in data/transactions.db.
# The server runs main.py from c:/dvdcoin/ so:
# - Active users DB: c:/dvdcoin/data/users.db
# - Active transactions DB: c:/dvdcoin/data/transactions.db
import sqlite3

USERS_DB = 'c:/dvdcoin/data/users.db'
TX_DB = 'c:/dvdcoin/data/transactions.db'

ADMINS = {'dvd', 'admin', 'aitor'}

# Step 1: Get current balances
users_conn = sqlite3.connect(USERS_DB)
users_conn.row_factory = sqlite3.Row
users = users_conn.execute('SELECT username, balance FROM users').fetchall()
current_balances = {r['username']: r['balance'] for r in users}
print(f"Users in DB: {len(current_balances)}")

# Step 2: Get all transactions
tx_conn = sqlite3.connect(TX_DB)
tx_conn.row_factory = sqlite3.Row
transactions = tx_conn.execute("SELECT * FROM transactions ORDER BY id").fetchall()
tx_conn.close()
print(f"Transactions: {len(transactions)}")

# Step 3: Recalculate balances from scratch
calculated = {}
for tx in transactions:
    from_u = tx['from_user']
    to_u = tx['to_user']
    amount = tx['amount']
    
    # Deduct from sender (unless admin or system/porra payout source)
    if from_u not in ADMINS and not from_u.startswith('Porra:') and from_u != 'sistema':
        calculated[from_u] = calculated.get(from_u, 0.0) - amount
    
    # Credit to receiver (unless admin or porra bet target or sistema)
    if to_u not in ADMINS and not to_u.startswith('Porra:') and to_u != 'sistema':
        calculated[to_u] = calculated.get(to_u, 0.0) + amount

# Step 4: Compare and fix
print(f"\n{'USERNAME':25s} {'STORED':>12s} {'CORRECT':>12s} {'DIFF':>12s}")
print("=" * 65)

corrections = {}
for username in sorted(current_balances.keys(), key=lambda u: current_balances.get(u, 0), reverse=True):
    stored = current_balances[username]
    correct = round(calculated.get(username, 0.0), 4)
    if username in ADMINS:
        correct = 0.0
    # No negative balances
    if correct < 0:
        correct = 0.0
    diff = round(stored - correct, 4)
    action = ""
    if abs(diff) > 0.001:
        action = "FIX"
        corrections[username] = correct
    print(f"{username:25s} {stored:>12.4f} {correct:>12.4f} {diff:>12.4f} {action}")

print(f"\nCorrections needed: {len(corrections)}")

if corrections:
    print("\n--- APPLYING CORRECTIONS ---")
    for username, new_balance in corrections.items():
        old = current_balances[username]
        users_conn.execute("UPDATE users SET balance=? WHERE username=?", (new_balance, username))
        print(f"  {username}: {old:.4f} -> {new_balance:.4f}")
    users_conn.commit()
    print("\nAll balances corrected!")

    # Final verification
    print("\n--- FINAL BALANCES ---")
    rows = users_conn.execute('SELECT username, balance FROM users ORDER BY balance DESC').fetchall()
    for r in rows:
        if r['balance'] > 0:
            print(f"  {r['username']:25s} {r['balance']:>12.4f}")
else:
    print("\nAll balances are already correct!")

users_conn.close()
