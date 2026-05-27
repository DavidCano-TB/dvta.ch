#!/usr/bin/env python3
"""
Script para añadir navegación unificada a todos los archivos HTML del proyecto DVDcoin
"""

import os
import re
from pathlib import Path

# Directorios a procesar
STATIC_DIR = Path(__file__).parent.parent / 'static'

# Archivos a excluir
EXCLUDE_FILES = {
    '_nav.html',
    '_nav-include.html',
    'sw.js',
}

# Patrones para detectar si ya tiene la navegación
NAV_PATTERNS = [
    r'unifiedNavContainer',
    r'unified-nav\.js',
    r'unified-nav\.css'
]

def has_unified_nav(content):
    """Verifica si el archivo ya tiene la navegación unificada"""
    return any(re.search(pattern, content) for pattern in NAV_PATTERNS)

def add_css_link(content):
    """Añade el link al CSS de navegación en el <head>"""
    # Buscar el último <link> o <style> en el head
    head_pattern = r'(<head>.*?)(</head>)'
    
    css_link = '<link rel="stylesheet" href="/static/css/unified-nav.css">\n'
    
    def replacer(match):
        head_content = match.group(1)
        # Añadir antes del </head>
        if '<link' in head_content or '<style' in head_content:
            # Insertar después del último link o antes del primer style
            if '</style>' in head_content:
                # Insertar antes del primer <style>
                head_content = re.sub(r'(<style)', css_link + r'\1', head_content, count=1)
            else:
                # Insertar después del último </link> o al final
                head_content = head_content.rstrip() + '\n' + css_link
        else:
            head_content = head_content.rstrip() + '\n' + css_link
        
        return head_content + match.group(2)
    
    return re.sub(head_pattern, replacer, content, flags=re.DOTALL)

def add_nav_container(content):
    """Añade el contenedor de navegación después del <body>"""
    nav_container = '\n<!-- Navegación Unificada -->\n<div id="unifiedNavContainer"></div>\n\n'
    
    # Buscar <body> o <body class="...">
    body_pattern = r'(<body[^>]*>)'
    
    def replacer(match):
        return match.group(1) + nav_container
    
    return re.sub(body_pattern, replacer, content, count=1)

def add_body_class(content):
    """Añade la clase has-unified-nav al body si no la tiene"""
    # Si ya tiene clase
    if re.search(r'<body\s+class="[^"]*"', content):
        # Añadir la clase si no está
        def replacer(match):
            if 'has-unified-nav' not in match.group(0):
                return match.group(0).replace('class="', 'class="has-unified-nav ')
            return match.group(0)
        return re.sub(r'<body\s+class="[^"]*"', replacer, content)
    else:
        # Añadir atributo class
        return re.sub(r'<body>', '<body class="has-unified-nav">', content)

def add_nav_script(content):
    """Añade el script de navegación antes del </body>"""
    nav_script = '\n<!-- Sistema de Navegación Unificada -->\n<script src="/static/js/unified-nav.js"></script>\n\n'
    
    # Insertar antes del </body>
    return re.sub(r'(</body>)', nav_script + r'\1', content, count=1)

def process_html_file(filepath):
    """Procesa un archivo HTML individual"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si ya tiene la navegación
        if has_unified_nav(content):
            print(f"⏭️  {filepath.name} - Ya tiene navegación unificada")
            return False
        
        # Verificar que sea un HTML válido
        if '<html' not in content.lower() or '<body' not in content.lower():
            print(f"⚠️  {filepath.name} - No parece ser un HTML completo")
            return False
        
        # Aplicar transformaciones
        original_content = content
        
        # 1. Añadir CSS
        content = add_css_link(content)
        
        # 2. Añadir clase al body
        content = add_body_class(content)
        
        # 3. Añadir contenedor de navegación
        content = add_nav_container(content)
        
        # 4. Añadir script
        content = add_nav_script(content)
        
        # Verificar que se hicieron cambios
        if content == original_content:
            print(f"⚠️  {filepath.name} - No se pudieron aplicar cambios")
            return False
        
        # Guardar archivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {filepath.name} - Navegación añadida correctamente")
        return True
        
    except Exception as e:
        print(f"❌ {filepath.name} - Error: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("DVDcoin Bank - Añadir Navegación Unificada")
    print("=" * 60)
    print()
    
    # Buscar todos los archivos HTML
    html_files = []
    
    # Archivos en la raíz de static
    for file in STATIC_DIR.glob('*.html'):
        if file.name not in EXCLUDE_FILES:
            html_files.append(file)
    
    # Archivos en subdirectorios
    for subdir in ['admin', 'pages', 'millonario', 'pasapalabra', 'quiensoy', 
                   'cifrasletras', 'hundirlaflota', 'opo', 'apuestas', 'votaciones']:
        subdir_path = STATIC_DIR / subdir
        if subdir_path.exists():
            for file in subdir_path.glob('*.html'):
                if file.name not in EXCLUDE_FILES:
                    html_files.append(file)
    
    print(f"📁 Encontrados {len(html_files)} archivos HTML\n")
    
    # Procesar archivos
    processed = 0
    skipped = 0
    errors = 0
    
    for filepath in sorted(html_files):
        result = process_html_file(filepath)
        if result:
            processed += 1
        elif result is False:
            skipped += 1
        else:
            errors += 1
    
    # Resumen
    print()
    print("=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"✅ Procesados: {processed}")
    print(f"⏭️  Omitidos: {skipped}")
    print(f"❌ Errores: {errors}")
    print(f"📊 Total: {len(html_files)}")
    print()

if __name__ == '__main__':
    main()
