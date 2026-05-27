#!/usr/bin/env python3
"""
Script para corregir la tabla votaciones agregando fecha_creacion
"""
import sqlite3

DB_PATH = "data/apuestas.db"

def corregir_votaciones():
    print("=" * 80)
    print("CORRIGIENDO TABLA VOTACIONES")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print(f"\n✓ Conectado a: {DB_PATH}")
    
    # Verificar estructura actual
    print("\n[1] Verificando estructura actual...")
    c.execute("PRAGMA table_info(votaciones)")
    columnas = c.fetchall()
    
    columnas_existentes = [col[1] for col in columnas]
    print(f"   Columnas actuales: {', '.join(columnas_existentes)}")
    
    # Agregar fecha_creacion sin DEFAULT (SQLite no permite DEFAULT con funciones en ALTER TABLE)
    print("\n[2] Agregando columna 'fecha_creacion'...")
    if 'fecha_creacion' not in columnas_existentes:
        try:
            c.execute("""
                ALTER TABLE votaciones 
                ADD COLUMN fecha_creacion TIMESTAMP
            """)
            # Copiar valores de created_at a fecha_creacion
            if 'created_at' in columnas_existentes:
                c.execute("""
                    UPDATE votaciones 
                    SET fecha_creacion = created_at 
                    WHERE created_at IS NOT NULL
                """)
                print("   ✓ Columna 'fecha_creacion' agregada y datos copiados desde 'created_at'")
            else:
                # Si no hay created_at, usar la fecha actual para registros existentes
                c.execute("""
                    UPDATE votaciones 
                    SET fecha_creacion = CURRENT_TIMESTAMP 
                    WHERE fecha_creacion IS NULL
                """)
                print("   ✓ Columna 'fecha_creacion' agregada con fecha actual")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    else:
        print("   ✓ Columna 'fecha_creacion' ya existe")
    
    # Verificar fecha_cierre
    print("\n[3] Verificando columna 'fecha_cierre'...")
    if 'fecha_cierre' not in columnas_existentes:
        try:
            c.execute("""
                ALTER TABLE votaciones 
                ADD COLUMN fecha_cierre TIMESTAMP
            """)
            # Copiar valores de finalized_at a fecha_cierre
            if 'finalized_at' in columnas_existentes:
                c.execute("""
                    UPDATE votaciones 
                    SET fecha_cierre = finalized_at 
                    WHERE finalized_at IS NOT NULL
                """)
                print("   ✓ Columna 'fecha_cierre' agregada y datos copiados desde 'finalized_at'")
            else:
                print("   ✓ Columna 'fecha_cierre' agregada")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    else:
        print("   ✓ Columna 'fecha_cierre' ya existe")
    
    conn.commit()
    
    # Verificar estructura final
    print("\n[4] Verificando estructura final...")
    c.execute("PRAGMA table_info(votaciones)")
    columnas = c.fetchall()
    
    print("\n   Columnas finales:")
    for col in columnas:
        print(f"      - {col[1]} ({col[2]})")
    
    # Verificar datos
    print("\n[5] Verificando datos...")
    c.execute("SELECT COUNT(*) FROM votaciones")
    count = c.fetchone()[0]
    print(f"   Total de votaciones: {count}")
    
    if count > 0:
        c.execute("""
            SELECT id, titulo, fecha_creacion, fecha_cierre 
            FROM votaciones 
            LIMIT 3
        """)
        rows = c.fetchall()
        print("\n   Primeras votaciones:")
        for row in rows:
            print(f"      ID {row[0]}: {row[1]}")
            print(f"         Creación: {row[2]}")
            print(f"         Cierre: {row[3]}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✓ TABLA CORREGIDA CORRECTAMENTE")
    print("=" * 80)
    print("\nAhora el sistema de votaciones debería funcionar correctamente.\n")

if __name__ == "__main__":
    corregir_votaciones()
