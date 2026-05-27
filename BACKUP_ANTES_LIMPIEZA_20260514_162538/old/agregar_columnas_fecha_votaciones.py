#!/usr/bin/env python3
"""
Script para agregar las columnas fecha_creacion y fecha_cierre a la tabla votaciones
"""
import sqlite3

DB_PATH = "data/apuestas.db"

def agregar_columnas():
    print("=" * 80)
    print("AGREGANDO COLUMNAS A LA TABLA VOTACIONES")
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
    
    # Agregar fecha_creacion si no existe
    print("\n[2] Agregando columna 'fecha_creacion'...")
    if 'fecha_creacion' not in columnas_existentes:
        try:
            # Si existe created_at, copiar sus valores
            if 'created_at' in columnas_existentes:
                c.execute("""
                    ALTER TABLE votaciones 
                    ADD COLUMN fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """)
                # Copiar valores de created_at a fecha_creacion
                c.execute("""
                    UPDATE votaciones 
                    SET fecha_creacion = created_at 
                    WHERE created_at IS NOT NULL
                """)
                print("   ✓ Columna 'fecha_creacion' agregada y datos copiados desde 'created_at'")
            else:
                c.execute("""
                    ALTER TABLE votaciones 
                    ADD COLUMN fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """)
                print("   ✓ Columna 'fecha_creacion' agregada")
        except Exception as e:
            print(f"   ⚠️  Error o columna ya existe: {e}")
    else:
        print("   ✓ Columna 'fecha_creacion' ya existe")
    
    # Agregar fecha_cierre si no existe
    print("\n[3] Agregando columna 'fecha_cierre'...")
    if 'fecha_cierre' not in columnas_existentes:
        try:
            # Si existe closed_at, copiar sus valores
            if 'closed_at' in columnas_existentes:
                c.execute("""
                    ALTER TABLE votaciones 
                    ADD COLUMN fecha_cierre TIMESTAMP
                """)
                # Copiar valores de closed_at a fecha_cierre
                c.execute("""
                    UPDATE votaciones 
                    SET fecha_cierre = closed_at 
                    WHERE closed_at IS NOT NULL
                """)
                print("   ✓ Columna 'fecha_cierre' agregada y datos copiados desde 'closed_at'")
            else:
                c.execute("""
                    ALTER TABLE votaciones 
                    ADD COLUMN fecha_cierre TIMESTAMP
                """)
                print("   ✓ Columna 'fecha_cierre' agregada")
        except Exception as e:
            print(f"   ⚠️  Error o columna ya existe: {e}")
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
    print("✓ COLUMNAS AGREGADAS CORRECTAMENTE")
    print("=" * 80)
    print("\nAhora el sistema de votaciones debería funcionar correctamente.\n")

if __name__ == "__main__":
    agregar_columnas()
