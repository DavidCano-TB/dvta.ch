#!/usr/bin/env python3
"""
Script para crear las tablas necesarias para el sistema de votaciones
"""
import sqlite3
import os

DB_PATH = "data/apuestas.db"

def crear_tablas():
    print("=" * 80)
    print("CREACIÓN DE TABLAS DE VOTACIONES")
    print("=" * 80)
    
    if not os.path.exists(DB_PATH):
        print(f"\n❌ Base de datos no encontrada: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print(f"\n✓ Conectado a: {DB_PATH}")
    
    # 1. Tabla de votaciones
    print("\n[1] Creando tabla 'votaciones'...")
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS votaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                creador TEXT NOT NULL,
                titulo TEXT NOT NULL,
                descripcion TEXT DEFAULT '',
                estado TEXT DEFAULT 'abierta',
                multiple INTEGER DEFAULT 0,
                anonima INTEGER DEFAULT 0,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_cierre TIMESTAMP,
                resultado TEXT
            )
        """)
        print("   ✓ Tabla 'votaciones' creada/verificada")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Tabla de opciones de votaciones
    print("\n[2] Creando tabla 'votaciones_opciones'...")
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS votaciones_opciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                votacion_id INTEGER NOT NULL,
                opcion TEXT NOT NULL,
                FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE
            )
        """)
        print("   ✓ Tabla 'votaciones_opciones' creada/verificada")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Tabla de votos
    print("\n[3] Creando tabla 'votos'...")
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS votos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                votacion_id INTEGER NOT NULL,
                usuario TEXT NOT NULL,
                opcion TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE
            )
        """)
        print("   ✓ Tabla 'votos' creada/verificada")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Crear índices para mejorar rendimiento
    print("\n[4] Creando índices...")
    try:
        c.execute("CREATE INDEX IF NOT EXISTS idx_votaciones_estado ON votaciones(estado)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_votaciones_creador ON votaciones(creador)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_votos_votacion ON votos(votacion_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_votos_usuario ON votos(usuario)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_opciones_votacion ON votaciones_opciones(votacion_id)")
        print("   ✓ Índices creados")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    conn.commit()
    
    # 5. Verificar tablas creadas
    print("\n[5] Verificando tablas...")
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'vot%' ORDER BY name")
    tablas = c.fetchall()
    
    print("\n   Tablas encontradas:")
    for tabla in tablas:
        print(f"   ✓ {tabla[0]}")
        
        # Mostrar estructura de cada tabla
        c.execute(f"PRAGMA table_info({tabla[0]})")
        columnas = c.fetchall()
        for col in columnas:
            print(f"      - {col[1]} ({col[2]})")
    
    # 6. Contar registros
    print("\n[6] Contando registros...")
    for tabla in tablas:
        c.execute(f"SELECT COUNT(*) FROM {tabla[0]}")
        count = c.fetchone()[0]
        print(f"   {tabla[0]}: {count} registros")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✓ TABLAS CREADAS CORRECTAMENTE")
    print("=" * 80)
    print("\nAhora puedes:")
    print("1. Crear votaciones desde el panel de administración")
    print("2. Los usuarios pueden votar")
    print("3. DVD puede borrar votaciones")
    print("\n")

if __name__ == "__main__":
    crear_tablas()
