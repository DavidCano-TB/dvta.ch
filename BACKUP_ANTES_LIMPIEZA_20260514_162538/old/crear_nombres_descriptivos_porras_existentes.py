#!/usr/bin/env python3
"""
Script para crear archivos con nombres descriptivos para porras existentes.
Crea copias de porra_ID.html con el nombre porra "Titulo".html
NO modifica los archivos originales.
"""

import os
import sqlite3
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_BETS = os.path.join(BASE_DIR, "data", "apuestas.db")
PORRAS_DIR = os.path.join(BASE_DIR, "game_pages", "apuestas", "porras")

def sanitize_filename(titulo):
    """Remove invalid filename characters and limit length."""
    # Remove invalid characters for Windows/Linux filenames
    titulo_safe = re.sub(r'[<>:"/\\|?*]', '', titulo)
    titulo_safe = titulo_safe.strip()[:50]  # Limit to 50 chars
    return titulo_safe

def main():
    print("🚀 Creando nombres descriptivos para porras existentes\n")
    
    # Connect to database
    if not os.path.exists(DB_BETS):
        print(f"❌ Base de datos no encontrada: {DB_BETS}")
        return
    
    conn = sqlite3.connect(DB_BETS)
    conn.row_factory = sqlite3.Row
    
    # Get all porras
    porras = conn.execute("SELECT id, titulo FROM porras ORDER BY id").fetchall()
    conn.close()
    
    if not porras:
        print("⚠️  No se encontraron porras en la base de datos")
        return
    
    print(f"📊 Encontradas {len(porras)} porras en la base de datos\n")
    
    created = 0
    skipped = 0
    errors = 0
    
    for porra in porras:
        porra_id = porra['id']
        titulo = porra['titulo']
        
        # Paths
        source_path = os.path.join(PORRAS_DIR, f"porra_{porra_id}.html")
        titulo_safe = sanitize_filename(titulo)
        dest_path = os.path.join(PORRAS_DIR, f'porra ({titulo_safe}).html')
        
        # Check if source exists
        if not os.path.exists(source_path):
            print(f"⚠️  Porra {porra_id}: Archivo fuente no existe (porra_{porra_id}.html)")
            skipped += 1
            continue
        
        # Check if destination already exists
        if os.path.exists(dest_path):
            print(f"⏭️  Porra {porra_id}: Ya existe 'porra ({titulo_safe}).html'")
            skipped += 1
            continue
        
        # Copy file
        try:
            shutil.copy2(source_path, dest_path)
            print(f"✅ Porra {porra_id}: Creado 'porra ({titulo_safe}).html'")
            created += 1
        except Exception as e:
            print(f"❌ Porra {porra_id}: Error al copiar - {e}")
            errors += 1
    
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN:")
    print(f"   ✅ Archivos creados: {created}")
    print(f"   ⏭️  Archivos omitidos: {skipped}")
    print(f"   ❌ Errores: {errors}")
    print(f"{'='*60}\n")
    
    if created > 0:
        print("✅ Proceso completado exitosamente")
        print("\n📝 NOTA: Los archivos originales (porra_ID.html) NO fueron modificados.")
        print("   El sistema sigue funcionando por ID como siempre.")
        print("   Los archivos con nombres descriptivos son solo para referencia visual.")
    else:
        print("ℹ️  No se crearon archivos nuevos")

if __name__ == "__main__":
    main()
