#!/usr/bin/env python3
"""
Script to implement soft-delete system for porras
"""
import sqlite3
import os

# Connect to database
db_path = os.path.join("data", "apuestas.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Implementing soft-delete system for porras...")

# Check if deleted column exists
cursor.execute("PRAGMA table_info(porras)")
columns = [row[1] for row in cursor.fetchall()]

if 'deleted' not in columns:
    print("Adding 'deleted' column to porras table...")
    cursor.execute("ALTER TABLE porras ADD COLUMN deleted INTEGER DEFAULT 0")
    conn.commit()
    print("✓ Column added successfully")
else:
    print("✓ Column 'deleted' already exists")

# Check if deleted_at column exists
if 'deleted_at' not in columns:
    print("Adding 'deleted_at' column to porras table...")
    cursor.execute("ALTER TABLE porras ADD COLUMN deleted_at TEXT")
    conn.commit()
    print("✓ Column added successfully")
else:
    print("✓ Column 'deleted_at' already exists")

# Show current porras
print("\nCurrent porras:")
cursor.execute("SELECT id, titulo, estado, deleted FROM porras ORDER BY id DESC LIMIT 10")
for row in cursor.fetchall():
    deleted_status = " [DELETED]" if row[3] == 1 else ""
    print(f"  ID {row[0]}: {row[1]} - {row[2]}{deleted_status}")

conn.close()
print("\n✓ Soft-delete system implemented successfully!")
