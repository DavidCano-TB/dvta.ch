#!/usr/bin/env python3
"""
Script para verificar y corregir la tabla votos
"""
import sqlite3

DB_PATH = "apuestas.db"

def verificar_votos():
    print("=" * 80)
    print("VERIFICANDO TABLA VOTOS")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print(f"\n✓ Conectado a: {DB_PATH}")
    
    # Verificar estructura actual
    print("\n[1] Verificando estructura actual de 'votos'...")
    c.execute("PRAGMA table_info(votos)")
    columnas = c.fetchall()
    
    if not columnas:
        print("   ❌ La tabla 'votos' NO EXISTE")
        conn.close()
        return
    
    columnas_existentes = [col[1] for col in columnas]
    print(f"   Columnas actuales: {', '.join(columnas_existentes)}")
    
    # Verificar si necesitamos agregar 'username'
    if 'usuario' in columnas_existentes and 'username' not in columnas_existentes:
        print("\n[2] Agregando columna 'username'...")
        try:
            c.execute("""
                ALTER TABLE votos 
                ADD COLUMN username TEXT
            """)
            # Copiar valores de usuario a username
            c.execute("""
                UPDATE votos 
                SET username = usuario 
                WHERE usuario IS NOT NULL
            """)
            conn.commit()
            print("   ✓ Columna 'username' agregada y datos copiados desde 'usuario'")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    elif 'username' in columnas_existentes:
        print("\n[2] ✓ Columna 'username' ya existe")
    else:
        print("\n[2] ⚠️  No se encontró ni 'usuario' ni 'username'")
    
    # Verificar estructura final
    print("\n[3] Verificando estructura final...")
    c.execute("PRAGMA table_info(votos)")
    columnas = c.fetchall()
    
    print("\n   Columnas finales:")
    for col in columnas:
        print(f"      - {col[1]} ({col[2]})")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✓ VERIFICACIÓN COMPLETADA")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    verificar_votos()
