# Revert data/users.db to original values and show what the correct approach should be
import sqlite3

USERS_DB = 'c:/dvdcoin/data/users.db'
TX_DB = 'c:/dvdcoin/data/transactions.db'

# Original balances from data/users.db (before my fix)
ORIGINAL_BALANCES = {
    'dianelau': 250.0,
    'samson': 135.0,
    'yumazurman': 73.0,
    'victorzahyr': 72.0,
    'markus (polyglot)': 63.0,
    'an': 57.0,
    'dvdrec': 49.0,
    'aitor.mo': 42.0,
    'roydos': 35.0,
    'malagacity': 30.0,
    'mariterevr': 14.0,
    'mannycarpro': 5.0,
    'aquetzalliua': 4.0,
    'clara i': 3.0,
}

# Revert data/users.db
print("REVERTING data/users.db to original values...")
conn = sqlite3.connect(USERS_DB)
for username, balance in ORIGINAL_BALANCES.items():
    conn.execute("UPDATE users SET balance=? WHERE username=?", (balance, username))
# Also revert nina_user to 0
conn.execute("UPDATE users SET balance=0.0 WHERE username='nina_user'")
conn.commit()
conn.close()
print("Done reverting data/users.db")

# Now show the transactions that caused the inflation
print("\n\nLARGE TRANSACTIONS (>= 100 DVDcoins) from admin:")
tx_conn = sqlite3.connect(TX_DB)
tx_conn.row_factory = sqlite3.Row
large_txs = tx_conn.execute(
    "SELECT * FROM transactions WHERE amount >= 100 ORDER BY amount DESC"
).fetchall()
for t in large_txs:
    print(f"  [{t['created_at']}] {t['from_user']} -> {t['to_user']}: {t['amount']:.2f} ({t['concept']})")

# Show all unique "from dvd" transactions (admin gifts)
print("\n\nALL ADMIN GIFTS (from dvd):")
admin_gifts = tx_conn.execute(
    "SELECT to_user, SUM(amount) as total, COUNT(*) as count FROM transactions WHERE from_user='dvd' GROUP BY to_user ORDER BY total DESC"
).fetchall()
for t in admin_gifts:
    print(f"  {t['to_user']:25s} Total: {t['total']:>10.2f} ({t['count']} txs)")

# Show porra winnings
print("\n\nPORRA WINNINGS (from Porra:* or sistema):")
porra_wins = tx_conn.execute(
    "SELECT to_user, SUM(amount) as total FROM transactions WHERE from_user LIKE 'Porra:%' OR from_user='sistema' GROUP BY to_user ORDER BY total DESC"
).fetchall()
for t in porra_wins:
    print(f"  {t['to_user']:25s} Total: {t['total']:>10.2f}")

# Show user-to-user transfers
print("\n\nUSER-TO-USER TRANSFERS (not from admin, not porra):")
user_txs = tx_conn.execute(
    "SELECT * FROM transactions WHERE from_user NOT IN ('dvd','admin','aitor') AND from_user NOT LIKE 'Porra:%' AND from_user != 'sistema' ORDER BY id"
).fetchall()
for t in user_txs:
    print(f"  [{t['created_at']}] {t['from_user']} -> {t['to_user']}: {t['amount']:.2f} ({t['concept']})")

tx_conn.close()
