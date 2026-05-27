#!/usr/bin/env python3
"""
Direct SQL script to restore the Italy rain porra
Run this manually: python restore_italy_porra_direct.py
"""
import sqlite3
import os

db_path = os.path.join("data", "apuestas.db")

print("=" * 70)
print("RESTORING ITALY RAIN PORRA - DIRECT SQL METHOD")
print("=" * 70)

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Search for porras about rain, Italy, or Milan
    print("\n🔍 Searching for deleted porras about rain/Italy/Milan...")
    cursor.execute("""
        SELECT id, creador, titulo, descripcion, estado, deleted, deleted_at, created_at
        FROM porras 
        WHERE (titulo LIKE '%lluev%' OR titulo LIKE '%italia%' OR titulo LIKE '%milan%' OR titulo LIKE '%Milán%')
        AND deleted = 1
        ORDER BY id DESC
    """)
    
    deleted_porras = cursor.fetchall()
    
    if not deleted_porras:
        print("\n❌ No deleted porras found about rain/Italy/Milan")
        print("\n🔍 Searching for ALL deleted porras...")
        cursor.execute("""
            SELECT id, creador, titulo, descripcion, estado, deleted, deleted_at, created_at
            FROM porras 
            WHERE deleted = 1
            ORDER BY deleted_at DESC
            LIMIT 10
        """)
        deleted_porras = cursor.fetchall()
        
        if not deleted_porras:
            print("❌ No deleted porras found at all")
        else:
            print(f"\n✅ Found {len(deleted_porras)} recently deleted porra(s):\n")
            for p in deleted_porras:
                print(f"ID: {p['id']}")
                print(f"Title: {p['titulo']}")
                print(f"Description: {p['descripcion']}")
                print(f"Creator: {p['creador']}")
                print(f"Status: {p['estado']}")
                print(f"Deleted: {p['deleted_at']}")
                print("-" * 70)
    else:
        print(f"\n✅ Found {len(deleted_porras)} deleted porra(s) about rain/Italy/Milan:\n")
        for p in deleted_porras:
            print(f"ID: {p['id']}")
            print(f"Title: {p['titulo']}")
            print(f"Description: {p['descripcion']}")
            print(f"Creator: {p['creador']}")
            print(f"Status: {p['estado']}")
            print(f"Deleted: {p['deleted_at']}")
            print("-" * 70)
            
            # Restore this porra
            print(f"\n🔄 RESTORING PORRA ID {p['id']}...")
            cursor.execute("""
                UPDATE porras 
                SET deleted = 0, deleted_at = NULL
                WHERE id = ?
            """, (p['id'],))
            conn.commit()
            print(f"✅ Porra ID {p['id']} restored successfully!")
            print(f"   Title: {p['titulo']}")
            print(f"   It is now visible again in the betting system.\n")
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("PROCESS COMPLETED")
print("=" * 70)
print("\nYou can now:")
print("1. Check the betting interface - the restored porra should be visible")
print("2. Or use the DVD 'Deleted' tab to manage other deleted porras")
print("=" * 70)
