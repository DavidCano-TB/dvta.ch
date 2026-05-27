#!/usr/bin/env python3
"""
Script to add a user to OPO access list
Usage: python add_opo_user.py <username>
"""
import sys
import sqlite3
from datetime import datetime

def add_opo_user(username):
    """Add a user to the OPO players list"""
    try:
        # Connect to rights database
        conn = sqlite3.connect('data/rights.db')
        conn.row_factory = sqlite3.Row
        
        # Check if user already has access
        existing = conn.execute(
            "SELECT username FROM opo_players WHERE username=?", 
            (username,)
        ).fetchone()
        
        if existing:
            print(f"✓ User '{username}' already has OPO access")
            conn.close()
            return True
        
        # Add user to opo_players
        conn.execute(
            "INSERT INTO opo_players(username, added_by, added_at) VALUES(?, ?, ?)",
            (username, 'dvd', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        )
        conn.commit()
        
        print(f"✓ User '{username}' added to OPO access list")
        
        # Show all OPO users
        print("\nCurrent OPO users:")
        rows = conn.execute("SELECT username, added_by, added_at FROM opo_players ORDER BY username").fetchall()
        for row in rows:
            print(f"  - {row['username']} (added by {row['added_by']} at {row['added_at']})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_opo_user.py <username>")
        print("\nExample: python add_opo_user.py nina")
        sys.exit(1)
    
    username = sys.argv[1]
    success = add_opo_user(username)
    sys.exit(0 if success else 1)
