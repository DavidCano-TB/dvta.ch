#!/usr/bin/env python3
"""
Script para limpiar todas las votaciones existentes
"""
import sqlite3

DB_PATH = "data/apuestas.db"

def limpiar_votaciones():
    print("=" * 80)
    print("LIMPIANDO VOTACIONES")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print(f"\n✓ Conectado a: {DB_PATH}")
    
    # Contar registros antes
    print("\n[1] Contando registros antes de limpiar...")
    c.execute("SELECT COUNT(*) FROM votaciones")
    count_votaciones = c.fetchone()[0]
    print(f"   Votaciones: {count_votaciones}")
    
    c.execute("SELECT COUNT(*) FROM votaciones_opciones")
    count_opciones = c.fetchone()[0]
    print(f"   Opciones: {count_opciones}")
    
    c.execute("SELECT COUNT(*) FROM votos")
    count_votos = c.fetchone()[0]
    print(f"   Votos: {count_votos}")
    
    # Eliminar todo
    print("\n[2] Eliminando todos los registros...")
    c.execute("DELETE FROM votos")
    print("   ✓ Votos eliminados")
    
    c.execute("DELETE FROM votaciones_opciones")
    print("   ✓ Opciones eliminadas")
    
    c.execute("DELETE FROM votaciones")
    print("   ✓ Votaciones eliminadas")
    
    conn.commit()
    
    # Verificar
    print("\n[3] Verificando limpieza...")
    c.execute("SELECT COUNT(*) FROM votaciones")
    count_votaciones = c.fetchone()[0]
    print(f"   Votaciones: {count_votaciones}")
    
    c.execute("SELECT COUNT(*) FROM votaciones_opciones")
    count_opciones = c.fetchone()[0]
    print(f"   Opciones: {count_opciones}")
    
    c.execute("SELECT COUNT(*) FROM votos")
    count_votos = c.fetchone()[0]
    print(f"   Votos: {count_votos}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✓ LIMPIEZA COMPLETADA")
    print("=" * 80)
    print("\nTodas las votaciones han sido eliminadas.\n")

if __name__ == "__main__":
    limpiar_votaciones()
