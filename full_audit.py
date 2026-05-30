"""
Full audit: recalculate all user balances from ALL transaction history
across both transaction databases (legacy + current).
"""
import sqlite3

# The real transaction history is in c:/dvdcoin/data/transactions.db (128 txs)
# The backup legacy dvdcoin.db has 29 older transactions
# Let's combine them all

all_transactions = []

# 1. Legacy transactions from backup dvdcoin.db
try:
    conn = sqlite3.connect('c:/dvdcoin/backup/2026-05-14/dvdcoin.db')
    conn.row_factory = sqlite3.Row
    txs = conn.execute("SELECT id, from_user, to_user, amount, concept, created_at FROM transactions ORDER BY id").fetchall()
    for t in txs:
        all_transactions.append(dict(t))
    conn.close()
    print(f"Legacy dvdcoin.db transactions: {len(txs)}")
except Exception as e:
    print(f"Error reading legacy: {e}")

# 2. Backup transactions.db (110 txs from May 14 backup)
try:
    conn = sqlite3.connect('c:/dvdcoin/backup/2026-05-14/transactions.db')
    conn.row_factory = sqlite3.Row
    txs = conn.execute("SELECT id, from_user, to_user, amount, concept, created_at FROM transactions ORDER BY id").fetchall()
    for t in txs:
        all_transactions.append(dict(t))
    conn.close()
    print(f"Backup transactions.db: {len(txs)}")
except Exception as e:
    print(f"Error reading backup tx: {e}")

# 3. Current transactions.db
try:
    conn = sqlite3.connect('c:/dvdcoin/data/transactions.db')
    conn.row_factory = sqlite3.Row
    txs = conn.execute("SELECT id, from_user, to_user, amount, concept, created_at FROM transactions ORDER BY id").fetchall()
    for t in txs:
        all_transactions.append(dict(t))
    conn.close()
    print(f"Current data/transactions.db: {len(txs)}")
except Exception as e:
    print(f"Error reading current tx: {e}")

# Deduplicate by (from_user, to_user, amount, created_at)
seen = set()
unique_txs = []
for t in all_transactions:
    key = (t['from_user'], t['to_user'], t['amount'], t['created_at'])
    if key not in seen:
        seen.add(key)
        unique_txs.append(t)

print(f"\nTotal unique transactions: {len(unique_txs)}")

# Sort by date
unique_txs.sort(key=lambda x: x['created_at'] or '')

# Known admins
ADMINS = {'dvd', 'admin', 'aitor'}

# Recalculate balances
calculated = {}
for tx in unique_txs:
    from_u = tx['from_user']
    to_u = tx['to_user']
    amount = tx['amount']
    
    # Deduct from sender (unless admin or porra payout)
    if from_u not in ADMINS and not from_u.startswith('Porra:'):
        calculated[from_u] = calculated.get(from_u, 0.0) - amount
    
    # Credit to receiver (unless admin or porra bet)
    if to_u not in ADMINS and not to_u.startswith('Porra:'):
        calculated[to_u] = calculated.get(to_u, 0.0) + amount

# Get current stored balances
conn = sqlite3.connect('c:/dvdcoin/src/data/users.db')
conn.row_factory = sqlite3.Row
users = conn.execute('SELECT username, balance FROM users').fetchall()
current_balances = {r['username']: r['balance'] for r in users}
conn.close()

print(f"\n{'USERNAME':25s} {'STORED':>12s} {'CALCULATED':>12s} {'DIFF':>12s}")
print("=" * 65)
all_users = set(list(current_balances.keys()) + list(calculated.keys()))
for username in sorted(all_users, key=lambda u: current_balances.get(u, 0), reverse=True):
    stored = current_balances.get(username, 0.0)
    calc = round(calculated.get(username, 0.0), 4)
    diff = round(stored - calc, 4)
    if username in ADMINS:
        calc = 0.0
        diff = 0.0
    print(f"{username:25s} {stored:>12.4f} {calc:>12.4f} {diff:>12.4f}")

# Show all transactions for users with balance > 500
print("\n\n" + "=" * 80)
print("DETAILED TRANSACTIONS FOR HIGH-BALANCE USERS (>500)")
print("=" * 80)
for target_user in ['victorzahyr', 'nina_user', 'yumazurman']:
    print(f"\n--- {target_user} ---")
    user_txs = [t for t in unique_txs if t['from_user'] == target_user or t['to_user'] == target_user]
    running = 0.0
    for t in user_txs:
        if t['from_user'] == target_user and target_user not in ADMINS:
            running -= t['amount']
            direction = f"SENT {t['amount']:.4f} to {t['to_user']}"
        elif t['to_user'] == target_user:
            running += t['amount']
            direction = f"RECEIVED {t['amount']:.4f} from {t['from_user']}"
        else:
            direction = f"??? {t}"
        print(f"  [{t['created_at']}] {direction:60s} Running: {running:.4f}  | {t['concept']}")
    print(f"  FINAL CALCULATED: {running:.4f}")
    print(f"  STORED IN DB:     {current_balances.get(target_user, 0.0):.4f}")
