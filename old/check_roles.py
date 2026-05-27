import sqlite3

# Verificar tabla roles
try:
    conn = sqlite3.connect('data/dvdcoin.db')
    conn.row_factory = sqlite3.Row
    
    # Verificar si existe la tabla roles
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'").fetchall()
    
    if tables:
        print("=== TABLA ROLES EXISTE ===")
        rows = conn.execute('SELECT username, role, granted_by FROM roles').fetchall()
        print(f"Total roles: {len(rows)}")
        for r in rows:
            print(f"  {r['username']}: role={r['role']}, granted_by={r['granted_by']}")
    else:
        print("❌ TABLA ROLES NO EXISTE")
        print("Creando tabla roles...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                username TEXT NOT NULL,
                role TEXT NOT NULL,
                granted_by TEXT,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (username, role)
            )
        """)
        conn.commit()
        print("✓ Tabla roles creada")
        
        # Insertar roles base
        base_admins = [
            ("dvd", "admin", "system"),
            ("nebulosa", "admin", "system"),
            ("nina", "admin", "system"),
            ("victor", "admin", "system"),
            ("yu", "admin", "system"),
            ("roy", "admin", "system"),
            ("admin", "admin", "system")
        ]
        
        for username, role, granted_by in base_admins:
            conn.execute("INSERT OR IGNORE INTO roles(username, role, granted_by) VALUES(?,?,?)", 
                        (username, role, granted_by))
        conn.commit()
        print(f"✓ Insertados {len(base_admins)} admins base")
    
    conn.close()
except Exception as e:
    print(f"❌ ERROR: {e}")
