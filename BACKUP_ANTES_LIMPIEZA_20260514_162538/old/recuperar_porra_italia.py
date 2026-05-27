#!/usr/bin/env python3
"""
Script para buscar y recuperar la porra sobre lluvia en Italia
"""
import sqlite3
import os

# Conectar a la base de datos
db_path = os.path.join("data", "apuestas.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 60)
print("BUSCANDO PORRA SOBRE LLUVIA EN ITALIA/MILÁN")
print("=" * 60)

# Buscar porras relacionadas con lluvia, Italia o Milán
cursor.execute("""
    SELECT id, creador, titulo, descripcion, estado, deleted, deleted_at, created_at
    FROM porras 
    WHERE titulo LIKE '%lluev%' OR titulo LIKE '%italia%' OR titulo LIKE '%milan%' OR titulo LIKE '%Milán%'
    ORDER BY id DESC
""")

porras = cursor.fetchall()

if not porras:
    print("\n❌ No se encontró ninguna porra sobre lluvia en Italia/Milán")
else:
    print(f"\n✅ Se encontraron {len(porras)} porra(s):\n")
    for p in porras:
        deleted_status = "🗑️ ELIMINADA" if p['deleted'] == 1 else "✓ Activa"
        print(f"ID: {p['id']}")
        print(f"Título: {p['titulo']}")
        print(f"Descripción: {p['descripcion']}")
        print(f"Estado: {p['estado']}")
        print(f"Deleted: {deleted_status}")
        if p['deleted'] == 1:
            print(f"Eliminada el: {p['deleted_at']}")
        print(f"Creada el: {p['created_at']}")
        print("-" * 60)
        
        # Si está eliminada, restaurarla
        if p['deleted'] == 1:
            print(f"\n🔄 RESTAURANDO PORRA ID {p['id']}...")
            cursor.execute("""
                UPDATE porras 
                SET deleted = 0, deleted_at = NULL
                WHERE id = ?
            """, (p['id'],))
            conn.commit()
            print(f"✅ Porra ID {p['id']} restaurada correctamente!")
            print(f"   Título: {p['titulo']}")

conn.close()
print("\n" + "=" * 60)
print("PROCESO COMPLETADO")
print("=" * 60)
