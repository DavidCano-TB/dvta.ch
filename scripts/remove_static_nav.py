#!/usr/bin/env python3
"""
Script para eliminar navegaciones estáticas hardcodeadas que quedaron
"""

import os
import re
from pathlib import Path

STATIC_DIR = Path(__file__).parent.parent / 'static'

def remove_static_nav_blocks(content):
    """Elimina bloques de navegación estática hardcodeada"""
    changes = []
    
    # Patrón para detectar navegación estática después de unifiedNavContainer
    pattern = r'(<div id="unifiedNavContainer"></div>\s*\n\s*<!-- NAVEGACIÓN UNIFICADA -->.*?</nav>)'
    
    matches = re.findall(pattern, content, re.DOTALL)
    if matches:
        # Reemplazar todo el bloque por solo el contenedor
        content = re.sub(pattern, r'<div id="unifiedNavContainer"></div>\n\n', content, flags=re.DOTALL)
        changes.append(f"  - Eliminada navegación estática hardcodeada ({len(matches)} bloques)")
    
    # También eliminar navegaciones que están antes del unifiedNavContainer
    pattern2 = r'(<!-- NAVEGACIÓN UNIFICADA -->.*?</nav>\s*\n\s*<div id="unifiedNavContainer"></div>)'
    matches2 = re.findall(pattern2, content, re.DOTALL)
    if matches2:
        content = re.sub(pattern2, r'<div id="unifiedNavContainer"></div>\n\n', content, flags=re.DOTALL)
        changes.append(f"  - Eliminada navegación estática antes del contenedor ({len(matches2)} bloques)")
    
    # Eliminar navegaciones standalone sin unifiedNavContainer cerca
    pattern3 = r'<!-- NAVEGACIÓN UNIFICADA -->\s*\n\s*<nav class="unified-nav">.*?</nav>\s*\n'
    matches3 = re.findall(pattern3, content, re.DOTALL)
    if matches3:
        content = re.sub(pattern3, '', content, flags=re.DOTALL)
        changes.append(f"  - Eliminada navegación standalone ({len(matches3)} bloques)")
    
    return content, changes

def process_file(filepath):
    """Procesa un archivo HTML"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'unifiedNavContainer' not in content:
            return None, "No tiene navegación unificada"
        
        original_content = content
        
        # Eliminar navegaciones estáticas
        content, changes = remove_static_nav_blocks(content)
        
        if content == original_content:
            return None, "Sin navegaciones estáticas"
        
        # Guardar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, changes
        
    except Exception as e:
        return False, f"Error: {e}"

def main():
    print("=" * 70)
    print("DVDcoin Bank - Eliminar Navegaciones Estáticas Hardcodeadas")
    print("=" * 70)
    print()
    
    # Buscar archivos HTML
    html_files = []
    
    for file in STATIC_DIR.rglob('*.html'):
        if file.name not in ['_nav.html', '_nav-include.html']:
            html_files.append(file)
    
    print(f"📁 Encontrados {len(html_files)} archivos HTML\n")
    
    processed = 0
    skipped = 0
    
    for filepath in sorted(html_files):
        result, info = process_file(filepath)
        
        if result is True:
            print(f"✅ {filepath.relative_to(STATIC_DIR)}")
            if isinstance(info, list):
                for change in info:
                    print(change)
            processed += 1
        elif result is None:
            # No mostrar los que no tienen cambios para reducir output
            skipped += 1
    
    print()
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"✅ Limpiados: {processed}")
    print(f"⏭️  Sin cambios: {skipped}")
    print(f"📊 Total: {len(html_files)}")
    print()

if __name__ == '__main__':
    main()
