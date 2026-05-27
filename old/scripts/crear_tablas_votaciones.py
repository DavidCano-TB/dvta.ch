#!/usr/bin/env python3
"""
Script para crear las tablas de votaciones en apuestas.db
Ejecutar este script para agregar las tablas faltantes sin reiniciar el servidor.
"""

import sqlite3
import os

# Ruta a la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_BETS = os.path.join(DATA_DIR, "apuestas.db")

def crear_tablas_votaciones():
    """Crear las tablas de votaciones en apuestas.db"""
    print(f"Conectando a {DB_BETS}...")
    
    if not os.path.exists(DB_BETS):
        print(f"ERROR: No se encuentra la base de datos en {DB_BETS}")
        return False
    
    try:
        conn = sqlite3.connect(DB_BETS)
        cursor = conn.cursor()
        
        print("Creando tablas de votaciones...")
        
        # Crear tabla votaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS votaciones (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                creador         TEXT NOT NULL,
                titulo          TEXT NOT NULL,
                descripcion     TEXT NOT NULL DEFAULT '',
                estado          TEXT NOT NULL DEFAULT 'abierta',
                multiple        INTEGER NOT NULL DEFAULT 0,
                anonima         INTEGER NOT NULL DEFAULT 0,
                fecha_creacion  TEXT NOT NULL DEFAULT (datetime('now')),
                fecha_cierre    TEXT
            )
        """)
        print("✓ Tabla 'votaciones' creada")
        
        # Crear tabla votaciones_opciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS votaciones_opciones (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                votacion_id     INTEGER NOT NULL,
                opcion          TEXT NOT NULL,
                FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE
            )
        """)
        print("✓ Tabla 'votaciones_opciones' creada")
        
        # Crear tabla votaciones_votos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS votaciones_votos (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                votacion_id     INTEGER NOT NULL,
                username        TEXT NOT NULL,
                opcion          TEXT NOT NULL,
                fecha           TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE
            )
        """)
        print("✓ Tabla 'votaciones_votos' creada")
        
        # Crear índices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_votaciones_estado ON votaciones(estado)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_votaciones_creador ON votaciones(creador)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_votaciones_votos_votacion ON votaciones_votos(votacion_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_votaciones_votos_user ON votaciones_votos(username)")
        print("✓ Índices creados")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Tablas de votaciones creadas exitosamente!")
        print("Ahora puedes usar /votaciones sin errores.")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR al crear las tablas: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CREACIÓN DE TABLAS DE VOTACIONES")
    print("=" * 60)
    print()
    
    if crear_tablas_votaciones():
        print("\n✅ Proceso completado con éxito")
    else:
        print("\n❌ Proceso fallido")
    
    print()
    input("Presiona Enter para salir...")
