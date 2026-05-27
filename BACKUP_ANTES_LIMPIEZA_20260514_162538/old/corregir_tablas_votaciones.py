#!/usr/bin/env python3
"""
Script para corregir las tablas de votaciones y asegurar que estén correctamente estructuradas
"""
import sqlite3
import os

DB_PATH = "data/apuestas.db"

def corregir_tablas():
    print("=" * 80)
    print("CORRECCIÓN DE TABLAS DE VOTACIONES")
    print("=" * 80)
    
    if not os.path.exists(DB_PATH):
        print(f"\n❌ Base de datos no encontrada: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    print(f"\n✓ Conectado a: {DB_PATH}")
    
    # Verificar si las tablas existen
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('votaciones', 'votaciones_opciones', 'votos')")
    tablas_existentes = [row[0] for row in c.fetchall()]
    
    print(f"\n[1] Tablas existentes: {', '.join(tablas_existentes) if tablas_existentes else 'Ninguna'}")
    
    # Si la tabla votos existe, verificar la estructura
    if 'votos' in tablas_existentes:
        print("\n[2] Verificando estructura de tabla 'votos'...")
        c.execute("PRAGMA table_info(votos)")
        columnas = {row[1]: row for row in c.fetchall()}
        
        print(f"   Columnas actuales: {', '.join(columnas.keys())}")
        
        # Si tiene 'usuario' en lugar de 'username', necesitamos recrear la tabla
        if 'usuario' in columnas and 'username' not in columnas:
            print("\n   ⚠️  Detectada columna 'usuario' en lugar de 'username'")
            print("   Migrando datos...")
            
            # Crear tabla temporal con la estructura correcta
            c.execute("""
                CREATE TABLE IF NOT EXISTS votos_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    votacion_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    opcion TEXT NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE
                )
            """)
            
            # Copiar datos de la tabla antigua a la nueva
            c.execute("""
                INSERT INTO votos_new (id, votacion_id, username, opcion, fecha)
                SELECT id, votacion_id, usuario, opcion, fecha FROM votos
            """)
            
            # Eliminar tabla antigua
            c.execute("DROP TABLE votos")
            
            # Renombrar tabla nueva
            c.execute("ALTER TABLE votos_new RENAME TO votos")
            
            print("   ✓ Tabla 'votos' migrada correctamente")
        elif 'username' in columnas:
            print("   ✓ Tabla 'votos' ya tiene la estructura correcta")
    else:
        print("\n[2] Creando tabla 'votos'...")
        c.execute("""
            CREATE TABLE IF NOT EXISTS votos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                votacion_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                opcion TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE
            )
        """)
        print("   ✓ Tabla 'votos' creada")
    
    # Crear tabla votaciones si no existe
    if 'votaciones' not in tablas_existentes:
        print("\n[3] Creando tabla 'votaciones'...")
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
        print("   ✓ Tabla 'votaciones' creada")
    else:
        print("\n[3] Tabla 'votaciones' ya existe")
    
    # Crear tabla votaciones_opciones si no existe
    if 'votaciones_opciones' not in tablas_existentes:
        print("\n[4] Creando tabla 'votaciones_opciones'...")
        c.execute("""
            CREATE TABLE IF NOT EXISTS votaciones_opciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                votacion_id INTEGER NOT NULL,
                opcion TEXT NOT NULL,
                FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE
            )
        """)
        print("   ✓ Tabla 'votaciones_opciones' creada")
    else:
        print("\n[4] Tabla 'votaciones_opciones' ya existe")
    
    # Crear índices
    print("\n[5] Creando/verificando índices...")
    try:
        c.execute("CREATE INDEX IF NOT EXISTS idx_votaciones_estado ON votaciones(estado)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_votaciones_creador ON votaciones(creador)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_votos_votacion ON votos(votacion_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_votos_username ON votos(username)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_opciones_votacion ON votaciones_opciones(votacion_id)")
        print("   ✓ Índices creados/verificados")
    except Exception as e:
        print(f"   ⚠️  Error creando índices: {e}")
    
    conn.commit()
    
    # Verificar estructura final
    print("\n[6] Verificando estructura final...")
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'vot%' ORDER BY name")
    tablas = c.fetchall()
    
    for tabla in tablas:
        tabla_nombre = tabla[0]
        print(f"\n   Tabla: {tabla_nombre}")
        c.execute(f"PRAGMA table_info({tabla_nombre})")
        columnas = c.fetchall()
        for col in columnas:
            print(f"      - {col[1]} ({col[2]})")
        
        # Contar registros
        c.execute(f"SELECT COUNT(*) FROM {tabla_nombre}")
        count = c.fetchone()[0]
        print(f"      Total: {count} registros")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✓ CORRECCIÓN COMPLETADA")
    print("=" * 80)
    print("\nLas tablas de votaciones están ahora correctamente estructuradas.")
    print("Puedes reiniciar el servidor y probar las funcionalidades.\n")

if __name__ == "__main__":
    corregir_tablas()
