#!/usr/bin/env python3
"""
Script de prueba completo para el sistema de votaciones
"""
import sqlite3

DB_PATH = "data/apuestas.db"

def test_votaciones():
    print("=" * 80)
    print("TEST COMPLETO DEL SISTEMA DE VOTACIONES")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print(f"\n✓ Conectado a: {DB_PATH}")
    
    # 1. Verificar estructura de votaciones
    print("\n[1] Verificando tabla 'votaciones'...")
    c.execute("PRAGMA table_info(votaciones)")
    columnas = c.fetchall()
    columnas_nombres = [col[1] for col in columnas]
    
    columnas_requeridas = ['id', 'creador', 'titulo', 'descripcion', 'estado', 
                           'multiple', 'anonima', 'fecha_creacion', 'fecha_cierre']
    
    for col in columnas_requeridas:
        if col in columnas_nombres:
            print(f"   ✓ {col}")
        else:
            print(f"   ❌ {col} - FALTA")
    
    # 2. Verificar tabla votaciones_opciones
    print("\n[2] Verificando tabla 'votaciones_opciones'...")
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='votaciones_opciones'")
    if c.fetchone():
        print("   ✓ Tabla existe")
        c.execute("PRAGMA table_info(votaciones_opciones)")
        columnas = c.fetchall()
        for col in columnas:
            print(f"      - {col[1]} ({col[2]})")
    else:
        print("   ❌ Tabla NO existe")
    
    # 3. Verificar tabla votos
    print("\n[3] Verificando tabla 'votos'...")
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='votos'")
    if c.fetchone():
        print("   ✓ Tabla existe")
        c.execute("PRAGMA table_info(votos)")
        columnas = c.fetchall()
        columnas_nombres = [col[1] for col in columnas]
        
        if 'username' in columnas_nombres:
            print("   ✓ Columna 'username' existe")
        else:
            print("   ❌ Columna 'username' NO existe")
        
        for col in columnas:
            print(f"      - {col[1]} ({col[2]})")
    else:
        print("   ❌ Tabla NO existe")
    
    # 4. Contar registros
    print("\n[4] Contando registros...")
    c.execute("SELECT COUNT(*) FROM votaciones")
    count_votaciones = c.fetchone()[0]
    print(f"   Votaciones: {count_votaciones}")
    
    c.execute("SELECT COUNT(*) FROM votaciones_opciones")
    count_opciones = c.fetchone()[0]
    print(f"   Opciones: {count_opciones}")
    
    c.execute("SELECT COUNT(*) FROM votos")
    count_votos = c.fetchone()[0]
    print(f"   Votos: {count_votos}")
    
    # 5. Mostrar votaciones existentes
    if count_votaciones > 0:
        print("\n[5] Votaciones existentes:")
        c.execute("""
            SELECT id, titulo, estado, fecha_creacion, fecha_cierre 
            FROM votaciones 
            ORDER BY id
        """)
        rows = c.fetchall()
        for row in rows:
            print(f"\n   ID: {row[0]}")
            print(f"   Título: {row[1]}")
            print(f"   Estado: {row[2]}")
            print(f"   Creación: {row[3]}")
            print(f"   Cierre: {row[4]}")
            
            # Mostrar opciones
            c.execute("""
                SELECT opcion FROM votaciones_opciones 
                WHERE votacion_id=? 
                ORDER BY id
            """, (row[0],))
            opciones = c.fetchall()
            print(f"   Opciones: {', '.join([o[0] for o in opciones])}")
            
            # Contar votos
            c.execute("SELECT COUNT(*) FROM votos WHERE votacion_id=?", (row[0],))
            votos = c.fetchone()[0]
            print(f"   Votos: {votos}")
    
    # 6. Test de consulta SQL (la que usa el backend)
    print("\n[6] Probando consulta SQL del backend...")
    try:
        rows = c.execute("""
            SELECT id, creador, titulo, descripcion, estado, multiple, anonima,
                   fecha_creacion, fecha_cierre
            FROM votaciones
            ORDER BY fecha_creacion DESC
        """).fetchall()
        print(f"   ✓ Consulta exitosa - {len(rows)} votaciones encontradas")
    except Exception as e:
        print(f"   ❌ Error en consulta: {e}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✓ TEST COMPLETADO")
    print("=" * 80)
    print("\nSi todas las verificaciones pasaron, el sistema está listo para usar.\n")

if __name__ == "__main__":
    test_votaciones()
