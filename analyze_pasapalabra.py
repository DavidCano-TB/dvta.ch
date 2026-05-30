# Analyze pasapalabra payments to understand the pattern
import sqlite3

TX_DB = 'c:/dvdcoin/data/transactions.db'
conn = sqlite3.connect(TX_DB)
conn.row_factory = sqlite3.Row

# All pasapalabra-related transactions
print("=== ALL PASAPALABRA PAYMENTS ===")
txs = conn.execute(
    "SELECT * FROM transactions WHERE concept LIKE '%pasa%' OR concept LIKE '%pasapalabra%' ORDER BY created_at"
).fetchall()
for t in txs:
    print(f"  [{t['created_at']}] {t['from_user']} -> {t['to_user']}: {t['amount']:.2f} ({t['concept']})")

print("\n\n=== ALL PAYMENTS FROM ADMIN (dvd) GROUPED BY AMOUNT ===")
txs = conn.execute(
    "SELECT amount, COUNT(*) as cnt, GROUP_CONCAT(to_user) as users FROM transactions WHERE from_user='dvd' GROUP BY amount ORDER BY amount DESC"
).fetchall()
for t in txs:
    print(f"  Amount: {t['amount']:>8.2f} x{t['cnt']} -> {t['users']}")

conn.close()
