"""
Recalculate correct balances from the ACTIVE transaction database (data/transactions.db).
The src/data/transactions.db is empty (the app uses data/transactions.db at runtime).

Strategy:
- Use data/transactions.db which has 128 transactions (the real active one)
- Recalculate each user's balance as: sum(received) - sum(sent)
- Admin transfers (from dvd/admin/aitor) count as income for receiver
- Porra bets (to_user starts with "Porra:") count as expense for sender
- Porra winnings (from_user starts with "Porra:" or "sistema") count as income for receiver
"""
import sqlite3

# Active transaction database
tx_conn = sqlite3.connect('c:/dvdcoin/data/transactions.db')
tx_conn.row_factory = sqlite3.Row
transactions = tx_conn.execute("SELECT * FROM transactions ORDER BY id").fetchall()
tx_conn.close()

print(f"Active transactions: {len(transactions)}")

ADMINS = {'dvd', 'admin', 'aitor'}

# Recalculate
calculated = {}
for tx in transactions:
    from_u = tx['from_user']
    to_u = tx['to_user']
    amount = tx['amount']
    
    # Deduct from sender (unless admin or system/porra payout)
    if from_u not in ADMINS and not from_u.startswith('Porra:') and from_u != 'sistema':
        calculated[from_u] = calculated.get(from_u, 0.0) - amount
    
    # Credit to receiver (unless admin or porra bet target)
    if to_u not in ADMINS and not to_u.startswith('Porra:') and to_u != 'sistema':
        calculated[to_u] = calculated.get(to_u, 0.0) + amount

# Get current stored balances
users_conn = sqlite3.connect('c:/dvdcoin/src/data/users.db')
users_conn.row_factory = sqlite3.Row
users = users_conn.execute('SELECT username, balance FROM users').fetchall()
current_balances = {r['username']: r['balance'] for r in users}

print(f"\n{'USERNAME':25s} {'STORED':>12s} {'CORRECT':>12s} {'ACTION':>12s}")
print("=" * 65)

corrections = {}
for username in sorted(current_balances.keys(), key=lambda u: current_balances.get(u, 0), reverse=True):
    stored = current_balances[username]
    correct = round(calculated.get(username, 0.0), 4)
    if username in ADMINS:
        correct = 0.0
    # Ensure no negative balances
    if correct < 0:
        correct = 0.0
    action = ""
    if abs(stored - correct) > 0.001:
        action = "FIX"
        corrections[username] = correct
    print(f"{username:25s} {stored:>12.4f} {correct:>12.4f} {action:>12s}")

print(f"\n\nTotal corrections needed: {len(corrections)}")
print("\nCorrections to apply:")
for u, bal in sorted(corrections.items(), key=lambda x: x[1], reverse=True):
    print(f"  {u}: {current_balances[u]:.4f} -> {bal:.4f}")

# Apply corrections
if corrections:
    print("\n\nAPPLYING CORRECTIONS...")
    for username, new_balance in corrections.items():
        users_conn.execute("UPDATE users SET balance=? WHERE username=?", (new_balance, username))
        print(f"  Updated {username}: {new_balance:.4f}")
    users_conn.commit()
    print("\nDONE! All balances corrected.")

    # Verify
    print("\n\nVERIFICATION - New balances:")
    rows = users_conn.execute('SELECT username, balance FROM users ORDER BY balance DESC').fetchall()
    for r in rows:
        print(f"  {r['username']:25s} {r['balance']:>12.4f}")

users_conn.close()
