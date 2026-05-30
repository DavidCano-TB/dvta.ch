"""
Audit script: recalculate all user balances from transaction history
and compare with current stored balances.
"""
import sqlite3

# Connect to databases
users_conn = sqlite3.connect('c:/dvdcoin/src/data/users.db')
users_conn.row_factory = sqlite3.Row
tx_conn = sqlite3.connect('c:/dvdcoin/src/data/transactions.db')
tx_conn.row_factory = sqlite3.Row

# Get all users and their current balances
users = users_conn.execute('SELECT username, balance FROM users').fetchall()
current_balances = {r['username']: r['balance'] for r in users}

# Get all transactions
transactions = tx_conn.execute('SELECT id, from_user, to_user, amount, concept, created_at FROM transactions ORDER BY id').fetchall()

print(f"Total transactions: {len(transactions)}")
print(f"Total users: {len(current_balances)}")
print()

# Known admins (balance should always be 0)
ADMINS = {'dvd', 'admin', 'aitor'}

# Recalculate balances from transactions
calculated = {}
for tx in transactions:
    from_u = tx['from_user']
    to_u = tx['to_user']
    amount = tx['amount']
    
    # Skip admin deductions (admins have infinite money)
    if from_u not in ADMINS:
        calculated[from_u] = calculated.get(from_u, 0.0) - amount
    
    # Skip admin credits (admin balance stays 0)
    if to_u not in ADMINS:
        # Check if to_user looks like a bet description (not a real user)
        if not to_u.startswith('Porra:'):
            calculated[to_u] = calculated.get(to_u, 0.0) + amount

# Show comparison
print(f"{'USERNAME':25s} {'STORED':>12s} {'CALCULATED':>12s} {'DIFF':>12s}")
print("-" * 65)
for username in sorted(current_balances.keys(), key=lambda u: abs(current_balances.get(u, 0) - calculated.get(u, 0)), reverse=True):
    stored = current_balances[username]
    calc = calculated.get(username, 0.0)
    diff = stored - calc
    if abs(diff) > 0.001 or stored > 100:
        flag = " *** MISMATCH ***" if abs(diff) > 0.01 else ""
        print(f"{username:25s} {stored:>12.4f} {calc:>12.4f} {diff:>12.4f}{flag}")

print()
print("=" * 65)
print("USERS WITH BALANCE > 1000:")
print("=" * 65)
for username, balance in sorted(current_balances.items(), key=lambda x: x[1], reverse=True):
    if balance > 1000:
        print(f"  {username}: {balance:.4f}")
        # Show their transactions
        user_txs = [t for t in transactions if t['from_user'] == username or t['to_user'] == username]
        print(f"  Total transactions involving this user: {len(user_txs)}")
        # Show last 20 transactions
        print(f"  Last 20 transactions:")
        for t in user_txs[-20:]:
            direction = "SENT" if t['from_user'] == username else "RECEIVED"
            other = t['to_user'] if direction == "SENT" else t['from_user']
            print(f"    [{t['created_at']}] {direction} {t['amount']:.4f} {'to' if direction=='SENT' else 'from'} {other} - {t['concept']}")
        print()

users_conn.close()
tx_conn.close()
