#!/usr/bin/env python3
"""Script para crear las tablas de votaciones en la base de datos"""

import sqlite3

def crear_tablas_votaciones():
    conn = sqlite3.connect('apuestas.db')
    cursor = conn.cursor()
    
    print("🔧 Creando tablas de votaciones...")
    
    # Tabla principal de votaciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creador TEXT NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT DEFAULT '',
            estado TEXT DEFAULT 'abierta',
            multiple INTEGER DEFAULT 0,
            anonima INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            closed_at TIMESTAMP NULL
        )
    ''')
    print("✅ Tabla 'votaciones' creada")
    
    # Tabla de opciones de votación
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votaciones_opciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            votacion_id INTEGER NOT NULL,
            opcion TEXT NOT NULL,
            votos INTEGER DEFAULT 0,
            FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE
        )
    ''')
    print("✅ Tabla 'votaciones_opciones' creada")
    
    # Tabla de votos de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votaciones_votos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            votacion_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            opcion TEXT NOT NULL,
            voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE,
            UNIQUE(votacion_id, username, opcion)
        )
    ''')
    print("✅ Tabla 'votaciones_votos' creada")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Todas las tablas de votaciones creadas correctamente")

if __name__ == '__main__':
    crear_tablas_votaciones()
