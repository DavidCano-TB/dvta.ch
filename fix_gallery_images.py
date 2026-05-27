#!/usr/bin/env python3
"""Script para actualizar las rutas de imágenes de galería"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

files_to_fix = [
    'static/index.html',
    'static/pages/index.html',
    'static/millonario/index.html',
    'static/pasapalabra/index.html',
    'src/static/index.html',
    'src/static/pages/index.html',
    'src/static/millonario/index.html',
    'src/static/pasapalabra/index.html',
]

for file_rel in files_to_fix:
    file_path = BASE_DIR / file_rel
    if not file_path.exists():
        print(f"⚠️  No existe: {file_rel}")
        continue
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        content = content.replace('src="/static/gallery/', 'src="/bank/static/gallery/')
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Actualizado: {file_rel}")
        else:
            print(f"ℹ️  Sin cambios: {file_rel}")
    
    except Exception as e:
        print(f"❌ Error en {file_rel}: {e}")

print("\n✨ Completado!")
