#!/usr/bin/env python3
"""
Script para actualizar todas las referencias del dominio ngrok antiguo al nuevo
"""

import re
from pathlib import Path

# Directorios a procesar
ROOT_DIR = Path(__file__).parent.parent

# Dominio antiguo y nuevo
OLD_DOMAIN = "premium-size-unreached.ngrok-free.dev"
NEW_DOMAIN = "premium-size-unreached.ngrok-free.dev"

# Archivos a excluir
EXCLUDE_PATTERNS = [
    '.git',
    '__pycache__',
    'venv',
    'node_modules',
    '.kiro',
    'BACKUP_',
]

def should_process(filepath):
    """Determina si un archivo debe procesarse"""
    # Excluir directorios
    for pattern in EXCLUDE_PATTERNS:
        if pattern in str(filepath):
            return False
    
    # Solo procesar archivos de texto
    text_extensions = {
        '.md', '.txt', '.py', '.js', '.html', '.css', 
        '.json', '.log', '.bat', '.sh', '.yml', '.yaml',
        '.conf', '.config', '.env'
    }
    
    return filepath.suffix.lower() in text_extensions or filepath.suffix == ''

def update_file(filepath):
    """Actualiza las referencias en un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si contiene el dominio antiguo
        if OLD_DOMAIN not in content:
            return None, "Sin referencias"
        
        # Contar ocurrencias
        count = content.count(OLD_DOMAIN)
        
        # Reemplazar
        new_content = content.replace(OLD_DOMAIN, NEW_DOMAIN)
        
        # Guardar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f"{count} referencias actualizadas"
        
    except Exception as e:
        return False, f"Error: {e}"

def main():
    print("=" * 70)
    print("DVDcoin Bank - Actualizar Dominio ngrok")
    print("=" * 70)
    print()
    print(f"Dominio antiguo: {OLD_DOMAIN}")
    print(f"Dominio nuevo:   {NEW_DOMAIN}")
    print()
    print("=" * 70)
    print()
    
    # Buscar archivos
    all_files = []
    for filepath in ROOT_DIR.rglob('*'):
        if filepath.is_file() and should_process(filepath):
            all_files.append(filepath)
    
    print(f"📁 Encontrados {len(all_files)} archivos para revisar\n")
    
    processed = 0
    skipped = 0
    errors = 0
    total_refs = 0
    
    for filepath in sorted(all_files):
        result, info = update_file(filepath)
        
        if result is True:
            rel_path = filepath.relative_to(ROOT_DIR)
            print(f"✅ {rel_path}")
            print(f"   {info}")
            processed += 1
            # Extraer número de referencias
            if "referencias" in info:
                refs = int(info.split()[0])
                total_refs += refs
        elif result is False:
            rel_path = filepath.relative_to(ROOT_DIR)
            print(f"❌ {rel_path} - {info}")
            errors += 1
        else:
            skipped += 1
    
    print()
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"✅ Archivos actualizados: {processed}")
    print(f"📝 Referencias cambiadas: {total_refs}")
    print(f"⏭️  Sin cambios: {skipped}")
    print(f"❌ Errores: {errors}")
    print(f"📊 Total revisados: {len(all_files)}")
    print()
    print("=" * 70)
    print("VERIFICACIÓN")
    print("=" * 70)
    print(f"Dominio correcto: {NEW_DOMAIN}")
    print(f"URL correcta: https://{NEW_DOMAIN}")
    print("=" * 70)

if __name__ == '__main__':
    main()
