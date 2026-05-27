#!/usr/bin/env python3
"""
Script para recuperar la porra 7 y establecerla como abierta
"""
import sqlite3
import os

db_path = os.path.join("data", "apuestas.db")

print("=" * 70)
print("RECUPERANDO PORRA 7 COMO ABIERTA")
print("=" * 70)

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Verificar estado actual de la porra 7
    print("\n🔍 Verificando estado actual de la porra 7...")
    cursor.execute("""
        SELECT id, creador, titulo, descripcion, estado, deleted, deleted_at, 
               fecha_limite, fecha_evento, created_at
        FROM porras 
        WHERE id = 7
    """)
    
    porra = cursor.fetchone()
    
    if not porra:
        print("\n❌ ERROR: No se encontró la porra con ID 7")
        conn.close()
        exit(1)
    
    print(f"\n📋 Estado actual de la porra 7:")
    print(f"   ID: {porra['id']}")
    print(f"   Título: {porra['titulo']}")
    print(f"   Descripción: {porra['descripcion']}")
    print(f"   Creador: {porra['creador']}")
    print(f"   Estado: {porra['estado']}")
    print(f"   Deleted: {porra['deleted'] if porra['deleted'] else 0}")
    if porra['deleted_at']:
        print(f"   Deleted at: {porra['deleted_at']}")
    print(f"   Fecha límite: {porra['fecha_limite']}")
    print(f"   Fecha evento: {porra['fecha_evento']}")
    print(f"   Creada: {porra['created_at']}")
    
    # Restaurar y establecer como abierta
    print(f"\n🔄 Restaurando porra 7 y estableciendo como ABIERTA...")
    
    cursor.execute("""
        UPDATE porras 
        SET deleted = 0, 
            deleted_at = NULL,
            estado = 'abierta'
        WHERE id = 7
    """)
    
    conn.commit()
    
    # Verificar cambios
    cursor.execute("""
        SELECT id, titulo, estado, deleted
        FROM porras 
        WHERE id = 7
    """)
    
    porra_updated = cursor.fetchone()
    
    print(f"\n✅ PORRA 7 RECUPERADA EXITOSAMENTE!")
    print(f"   ID: {porra_updated['id']}")
    print(f"   Título: {porra_updated['titulo']}")
    print(f"   Estado: {porra_updated['estado']}")
    print(f"   Deleted: {porra_updated['deleted']}")
    print(f"\n   ✓ La porra está ahora ABIERTA y visible para todos los usuarios")
    print(f"   ✓ Los usuarios pueden realizar apuestas")
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("PROCESO COMPLETADO")
print("=" * 70)
