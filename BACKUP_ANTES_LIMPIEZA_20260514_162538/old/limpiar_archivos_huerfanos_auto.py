#!/usr/bin/env python3
"""
Script para borrar automáticamente archivos HTML de porras que ya no existen en la base de datos.
"""

import os
import sqlite3
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_BETS = os.path.join(BASE_DIR, "data", "apuestas.db")
PORRAS_DIR = os.path.join(BASE_DIR, "game_pages", "apuestas", "porras")

def main():
    print("🔍 Buscando archivos HTML huérfanos...\n")
    
    if not os.path.exists(DB_BETS):
        print(f"❌ Base de datos no encontrada: {DB_BETS}")
        return
    
    # Get all porra IDs from database
    conn = sqlite3.connect(DB_BETS)
    porras_db = conn.execute("SELECT id FROM porras").fetchall()
    conn.close()
    
    porras_ids_db = set(row[0] for row in porras_db)
    print(f"📊 Porras en la base de datos: {sorted(porras_ids_db)}")
    
    # Get all HTML files
    if not os.path.exists(PORRAS_DIR):
        print(f"❌ Directorio no encontrado: {PORRAS_DIR}")
        return
    
    archivos = os.listdir(PORRAS_DIR)
    
    # Find porra_ID.html files
    archivos_id = {}
    for filename in archivos:
        match = re.match(r'porra_(\d+)\.html$', filename)
        if match:
            porra_id = int(match.group(1))
            archivos_id[porra_id] = filename
    
    print(f"📁 Archivos porra_ID.html encontrados: {sorted(archivos_id.keys())}\n")
    
    # Find orphaned files
    huerfanos = []
    for porra_id, filename in archivos_id.items():
        if porra_id not in porras_ids_db:
            huerfanos.append((porra_id, filename))
    
    if not huerfanos:
        print("✅ No se encontraron archivos huérfanos")
        return
    
    print(f"🗑️  ARCHIVOS HUÉRFANOS ENCONTRADOS: {len(huerfanos)}\n")
    print("="*80)
    
    for porra_id, filename in sorted(huerfanos):
        # Try to find descriptive name file
        descriptive_file = None
        for fname in archivos:
            if fname.startswith("porra (") and fname.endswith(").html"):
                fpath = os.path.join(PORRAS_DIR, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if f"const PORRA_ID={porra_id};" in content:
                            descriptive_file = fname
                            break
                except:
                    pass
        
        print(f"   - Porra {porra_id}:")
        print(f"     • {filename}")
        if descriptive_file:
            print(f"     • {descriptive_file}")
    
    print("="*80)
    print("\n🗑️  Borrando archivos automáticamente...\n")
    
    borrados = 0
    errores = 0
    
    for porra_id, filename in sorted(huerfanos):
        try:
            # Delete porra_ID.html
            filepath = os.path.join(PORRAS_DIR, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"✅ Borrado: {filename}")
                borrados += 1
            
            # Delete descriptive file if exists
            for fname in archivos:
                if fname.startswith("porra (") and fname.endswith(").html"):
                    fpath = os.path.join(PORRAS_DIR, fname)
                    try:
                        with open(fpath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if f"const PORRA_ID={porra_id};" in content:
                                os.remove(fpath)
                                print(f"✅ Borrado: {fname}")
                                borrados += 1
                                break
                    except:
                        pass
        
        except Exception as e:
            print(f"❌ Error al borrar porra {porra_id}: {e}")
            errores += 1
    
    print("\n" + "="*80)
    print(f"\n📊 RESUMEN:")
    print(f"   ✅ Archivos borrados: {borrados}")
    print(f"   ❌ Errores: {errores}")
    print("="*80)
    
    if borrados > 0:
        print("\n✅ Limpieza completada exitosamente")

if __name__ == "__main__":
    main()
