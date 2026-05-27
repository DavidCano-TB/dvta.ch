#!/usr/bin/env python3
"""
Script para verificar que las tablas de votaciones existen
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_BETS = os.path.join(DATA_DIR, "apuestas.db")

def verificar_tablas():
    """Verificar que las tablas de votaciones existen"""
    print(f"Verificando tablas en {DB_BETS}...")
    print()
    
    try:
        conn = sqlite3.connect(DB_BETS)
        cursor = conn.cursor()
        
        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tablas = cursor.fetchall()
        
        print("Tablas encontradas en apuestas.db:")
        print("-" * 40)
        for tabla in tablas:
            print(f"  ✓ {tabla[0]}")
        
        print()
        print("Verificando tablas de votaciones:")
        print("-" * 40)
        
        tablas_requeridas = ['votaciones', 'votaciones_opciones', 'votaciones_votos']
        todas_existen = True
        
        for tabla_req in tablas_requeridas:
            existe = any(t[0] == tabla_req for t in tablas)
            if existe:
                print(f"  ✓ {tabla_req} - OK")
                
                # Mostrar estructura de la tabla
                cursor.execute(f"PRAGMA table_info({tabla_req})")
                columnas = cursor.fetchall()
                print(f"    Columnas: {', '.join([c[1] for c in columnas])}")
            else:
                print(f"  ✗ {tabla_req} - FALTA")
                todas_existen = False
        
        conn.close()
        
        print()
        if todas_existen:
            print("✅ Todas las tablas de votaciones están presentes")
        else:
            print("❌ Faltan algunas tablas de votaciones")
        
        return todas_existen
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICACIÓN DE TABLAS DE VOTACIONES")
    print("=" * 60)
    print()
    
    verificar_tablas()
    
    print()
    input("Presiona Enter para salir...")
