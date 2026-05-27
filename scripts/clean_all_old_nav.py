#!/usr/bin/env python3
"""
Script FINAL para limpiar COMPLETAMENTE todas las navegaciones antiguas
"""

import re
from pathlib import Path

STATIC_DIR = Path(__file__).parent.parent / 'static'

def clean_file(content):
    """Limpia TODO rastro de navegaciones antiguas"""
    changes = []
    
    # 1. Eliminar CSS de navegaciones antiguas (más agresivo)
    css_patterns = [
        (r'\.hdrBack[^}]*\{[^}]*\}', 'hdrBack'),
        (r'\.backBtn[^}]*\{[^}]*\}', 'backBtn'),
        (r'\.tbBack[^}]*\{[^}]*\}', 'tbBack'),
        (r'#simpleNav[^}]*\{[^}]*\}', 'simpleNav'),
        (r'\.sNavBtn[^}]*\{[^}]*\}', 'sNavBtn'),
        (r'\.hdrBack:hover[^}]*\{[^}]*\}', 'hdrBack:hover'),
        (r'\.backBtn:hover[^}]*\{[^}]*\}', 'backBtn:hover'),
        (r'\.tbBack:hover[^}]*\{[^}]*\}', 'tbBack:hover'),
        (r'\.sNavBtn:hover[^}]*\{[^}]*\}', 'sNavBtn:hover'),
    ]
    
    for pattern, name in css_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, '', content)
            changes.append(f"  - CSS: {name}")
    
    # 2. Eliminar elementos HTML de navegación antigua
    html_patterns = [
        (r'<a[^>]*class="hdrBack"[^>]*>.*?</a>', 'link hdrBack'),
        (r'<a[^>]*class="backBtn"[^>]*>.*?</a>', 'link backBtn'),
        (r'<a[^>]*class="tbBack"[^>]*>.*?</a>', 'link tbBack'),
        (r'<div id="simpleNav">.*?</div>', 'div simpleNav'),
        (r'<a[^>]*class="sNavBtn"[^>]*>.*?</a>', 'link sNavBtn'),
    ]
    
    for pattern, name in html_patterns:
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            changes.append(f"  - HTML: {name}")
    
    # 3. Eliminar comentarios de navegación antigua
    content = re.sub(r'<!-- Nav bar -->\s*\n', '', content)
    
    # 4. Limpiar líneas vacías excesivas
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # 5. Limpiar espacios al final de líneas
    content = re.sub(r' +\n', '\n', content)
    
    return content, changes

def process_file(filepath):
    """Procesa un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        content, changes = clean_file(content)
        
        if content == original:
            return None, "Sin cambios"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, changes
        
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("DVDcoin Bank - Limpieza FINAL de Navegaciones Antiguas")
    print("=" * 70)
    print()
    
    html_files = list(STATIC_DIR.rglob('*.html'))
    html_files = [f for f in html_files if f.name not in ['_nav.html', '_nav-include.html']]
    
    print(f"📁 {len(html_files)} archivos HTML\n")
    
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
            skipped += 1
    
    print()
    print("=" * 70)
    print(f"✅ Limpiados: {processed}")
    print(f"⏭️  Sin cambios: {skipped}")
    print(f"📊 Total: {len(html_files)}")
    print("=" * 70)

if __name__ == '__main__':
    main()
