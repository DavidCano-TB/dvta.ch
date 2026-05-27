#!/usr/bin/env python3
"""
Script para ELIMINAR navegaciones antiguas y reemplazarlas con navegación unificada
"""

import os
import re
from pathlib import Path

STATIC_DIR = Path(__file__).parent.parent / 'static'

# Patrones de navegaciones antiguas a eliminar
OLD_NAV_PATTERNS = [
    # Headers con botones de navegación
    (r'<div class="hdr">.*?<a[^>]*class="hdrBack"[^>]*>.*?</a>.*?</div>', 'hdr con hdrBack'),
    (r'<div id="hdr">.*?<a[^>]*class="backBtn"[^>]*>.*?</a>.*?</div>', 'hdr con backBtn'),
    
    # SimpleNav (stats.html)
    (r'<div id="simpleNav">.*?</div>', 'simpleNav'),
    
    # Top bars con botones back
    (r'<div id="topBar">.*?<a[^>]*class="tbBack"[^>]*>.*?</a>.*?</div>', 'topBar con tbBack'),
    
    # Headers genéricos con back button
    (r'<div class="header">.*?<button[^>]*onclick="goBack\(\)"[^>]*>.*?</button>.*?</div>', 'header con goBack'),
]

# CSS de navegaciones antiguas a eliminar
OLD_CSS_PATTERNS = [
    (r'\.hdrBack\{[^}]+\}', 'hdrBack CSS'),
    (r'\.backBtn\{[^}]+\}', 'backBtn CSS'),
    (r'\.tbBack\{[^}]+\}', 'tbBack CSS'),
    (r'#simpleNav\{[^}]+\}', 'simpleNav CSS'),
    (r'\.sNavBtn\{[^}]+\}', 'sNavBtn CSS'),
]

def remove_old_navigation_html(content):
    """Elimina elementos HTML de navegación antigua"""
    changes = []
    
    for pattern, name in OLD_NAV_PATTERNS:
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            changes.append(f"  - Eliminado: {name}")
    
    return content, changes

def remove_old_navigation_css(content):
    """Elimina CSS de navegación antigua"""
    changes = []
    
    for pattern, name in OLD_CSS_PATTERNS:
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            changes.append(f"  - Eliminado CSS: {name}")
    
    return content, changes

def has_unified_nav(content):
    """Verifica si ya tiene navegación unificada"""
    return 'unifiedNavContainer' in content

def add_unified_nav_if_missing(content):
    """Añade navegación unificada si no la tiene"""
    changes = []
    
    # 1. Añadir CSS si no está
    if 'unified-nav.css' not in content:
        # Buscar </head> y añadir antes
        if '</head>' in content:
            css_link = '<link rel="stylesheet" href="/static/css/unified-nav.css">\n'
            content = content.replace('</head>', css_link + '</head>')
            changes.append("  + Añadido CSS unified-nav")
    
    # 2. Añadir clase al body si no está
    if 'has-unified-nav' not in content:
        content = re.sub(r'<body([^>]*)>', r'<body\1 class="has-unified-nav">', content)
        changes.append("  + Añadida clase has-unified-nav al body")
    
    # 3. Añadir contenedor si no está
    if 'unifiedNavContainer' not in content:
        # Buscar <body> y añadir después
        body_pattern = r'(<body[^>]*>)'
        nav_container = r'\1\n<!-- Navegación Unificada -->\n<div id="unifiedNavContainer"></div>\n\n'
        content = re.sub(body_pattern, nav_container, content, count=1)
        changes.append("  + Añadido contenedor unifiedNavContainer")
    
    # 4. Añadir script si no está
    if 'unified-nav.js' not in content:
        # Buscar </body> y añadir antes
        if '</body>' in content:
            nav_script = '\n<!-- Sistema de Navegación Unificada -->\n<script src="/static/js/unified-nav.js"></script>\n\n'
            content = content.replace('</body>', nav_script + '</body>')
            changes.append("  + Añadido script unified-nav.js")
    
    return content, changes

def clean_empty_lines(content):
    """Limpia líneas vacías excesivas"""
    # Reemplazar 3+ líneas vacías por 2
    content = re.sub(r'\n\n\n+', '\n\n', content)
    return content

def process_file(filepath):
    """Procesa un archivo HTML"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '<html' not in content.lower():
            return None, "No es HTML completo"
        
        original_content = content
        all_changes = []
        
        # 1. Eliminar navegación HTML antigua
        content, html_changes = remove_old_navigation_html(content)
        all_changes.extend(html_changes)
        
        # 2. Eliminar CSS de navegación antigua
        content, css_changes = remove_old_navigation_css(content)
        all_changes.extend(css_changes)
        
        # 3. Añadir navegación unificada si falta
        content, nav_changes = add_unified_nav_if_missing(content)
        all_changes.extend(nav_changes)
        
        # 4. Limpiar líneas vacías
        content = clean_empty_lines(content)
        
        if content == original_content:
            return None, "Sin cambios necesarios"
        
        # Guardar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, all_changes
        
    except Exception as e:
        return False, f"Error: {e}"

def main():
    print("=" * 70)
    print("DVDcoin Bank - Reemplazar Navegación Antigua por Unificada")
    print("=" * 70)
    print()
    
    # Buscar archivos HTML
    html_files = []
    
    # Raíz de static
    for file in STATIC_DIR.glob('*.html'):
        if file.name not in ['_nav.html', '_nav-include.html']:
            html_files.append(file)
    
    # Subdirectorios
    for subdir in ['admin', 'pages', 'millonario', 'pasapalabra', 'quiensoy', 
                   'cifrasletras', 'hundirlaflota', 'opo', 'apuestas', 'votaciones',
                   'messages', 'cuentos']:
        subdir_path = STATIC_DIR / subdir
        if subdir_path.exists():
            for file in subdir_path.glob('*.html'):
                html_files.append(file)
    
    print(f"📁 Encontrados {len(html_files)} archivos HTML\n")
    
    processed = 0
    skipped = 0
    errors = 0
    
    for filepath in sorted(html_files):
        result, info = process_file(filepath)
        
        if result is True:
            print(f"✅ {filepath.name}")
            if isinstance(info, list):
                for change in info:
                    print(change)
            processed += 1
        elif result is None:
            print(f"⏭️  {filepath.name} - {info}")
            skipped += 1
        else:
            print(f"❌ {filepath.name} - {info}")
            errors += 1
        print()
    
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"✅ Procesados: {processed}")
    print(f"⏭️  Omitidos: {skipped}")
    print(f"❌ Errores: {errors}")
    print(f"📊 Total: {len(html_files)}")
    print()

if __name__ == '__main__':
    main()
