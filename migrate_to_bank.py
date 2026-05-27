#!/usr/bin/env python3
"""
Script para migrar toda la aplicación DVDcoin de la raíz (/) a /bank
Actualiza todas las rutas en Python, JavaScript, HTML y configuraciones
"""

import os
import re
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent

# Archivos a excluir
EXCLUDE_PATTERNS = [
    '.git', '__pycache__', 'node_modules', '.vscode', '.vs',
    'backup', 'backup_30min', 'BACKUP_ANTES_LIMPIEZA',
    '*.db', '*.pyc', '*.log', 'migrate_to_bank.py',
    'old', 'venv', 'env', '.venv', 'site-packages'
]

def should_exclude(path):
    """Verifica si un archivo/directorio debe ser excluido"""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False

def update_python_routes(content):
    """Actualiza rutas en archivos Python (FastAPI)"""
    changes = 0
    
    # Actualizar decoradores @app.get, @app.post, etc.
    # Patrón: @app.METHOD("/ruta") -> @app.METHOD("/bank/ruta")
    pattern = r'@app\.(get|post|put|delete|patch|websocket)\("(/[^"]*)"'
    
    def replace_route(match):
        nonlocal changes
        method = match.group(1)
        route = match.group(2)
        
        # No modificar si ya tiene /bank
        if route.startswith('/bank'):
            return match.group(0)
        
        # Casos especiales
        if route == '/':
            new_route = '/bank'
        else:
            new_route = f'/bank{route}'
        
        changes += 1
        return f'@app.{method}("{new_route}"'
    
    content = re.sub(pattern, replace_route, content)
    
    # Actualizar app.mount para archivos estáticos
    # app.mount("/static", ...) -> app.mount("/bank/static", ...)
    if 'app.mount("/static"' in content:
        content = content.replace('app.mount("/static"', 'app.mount("/bank/static"')
        changes += 1
    
    return content, changes

def update_javascript_routes(content):
    """Actualiza rutas en archivos JavaScript"""
    changes = 0
    
    # Patrones a buscar y reemplazar
    patterns = [
        # fetch('/api/...') -> fetch('/bank/api/...')
        (r'fetch\([\'"]/(api/[^\'"]+)[\'"]', r'fetch(\'/bank/\1\''),
        # fetch("/api/...") -> fetch("/bank/api/...")
        (r'fetch\([\'"]/(api/[^\'"]+)[\'"]', r'fetch(\'/bank/\1\''),
        # href: '/...' -> href: '/bank/...'
        (r'href:\s*[\'"]/((?!bank)[^\'"]+)[\'"]', r'href: \'/bank/\1\''),
        # href="/..." -> href="/bank/..."
        (r'href=[\'"]/((?!bank)[^\'"]+)[\'"]', r'href="/bank/\1"'),
        # window.location.href = '/' -> window.location.href = '/bank'
        (r'window\.location\.href\s*=\s*[\'"]/[\'"]', r'window.location.href = \'/bank\''),
        # checkEndpoint: '/api/...' -> checkEndpoint: '/bank/api/...'
        (r'checkEndpoint:\s*[\'"]/(api/[^\'"]+)[\'"]', r'checkEndpoint: \'/bank/\1\''),
    ]
    
    for pattern, replacement in patterns:
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            changes += count
    
    # Caso especial: fetch(`/static/i18n/${lang}.json`)
    if 'fetch(`/static/i18n/' in content:
        content = content.replace('fetch(`/static/i18n/', 'fetch(`/bank/static/i18n/')
        changes += 1
    
    return content, changes

def update_html_routes(content):
    """Actualiza rutas en archivos HTML"""
    changes = 0
    
    # Patrones a buscar y reemplazar
    patterns = [
        # <link href="/static/..." -> <link href="/bank/static/..."
        (r'<link\s+([^>]*\s+)?href=[\'"]/(static/[^\'"]+)[\'"]', r'<link \1href="/bank/\2"'),
        # <script src="/static/..." -> <script src="/bank/static/..."
        (r'<script\s+([^>]*\s+)?src=[\'"]/(static/[^\'"]+)[\'"]', r'<script \1src="/bank/\2"'),
        # fetch('/api/...') en scripts inline
        (r'fetch\([\'"]/(api/[^\'"]+)[\'"]', r'fetch(\'/bank/\1\''),
        # window.location.href = '/' en scripts inline
        (r'window\.location\.href\s*=\s*[\'"]/[\'"]', r'window.location.href = \'/bank\''),
        # href="/" -> href="/bank"
        (r'href=[\'"]/((?!bank|http)[^\'"]*)[\'"]', r'href="/bank/\1"'),
    ]
    
    for pattern, replacement in patterns:
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            changes += count
    
    return content, changes

def process_file(file_path):
    """Procesa un archivo individual"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = 0
        
        # Determinar tipo de archivo y aplicar transformaciones
        if file_path.suffix == '.py':
            content, changes = update_python_routes(content)
        elif file_path.suffix == '.js':
            content, changes = update_javascript_routes(content)
        elif file_path.suffix in ['.html', '.htm']:
            content, changes = update_html_routes(content)
        
        # Guardar si hubo cambios
        if changes > 0 and content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes
        
        return 0
    
    except Exception as e:
        print(f"  ⚠️  Error procesando {file_path}: {e}")
        return 0

def main():
    """Función principal"""
    print("=" * 70)
    print("🚀 Migración de DVDcoin Bank: / → /bank")
    print("=" * 70)
    print()
    
    # Contadores
    total_files = 0
    total_changes = 0
    files_modified = 0
    
    # Extensiones a procesar
    extensions = ['.py', '.js', '.html', '.htm']
    
    print("📁 Buscando archivos a procesar...")
    print()
    
    # Recorrer todos los archivos
    for ext in extensions:
        print(f"Procesando archivos {ext}...")
        
        for file_path in BASE_DIR.rglob(f'*{ext}'):
            if should_exclude(file_path):
                continue
            
            total_files += 1
            changes = process_file(file_path)
            
            if changes > 0:
                files_modified += 1
                total_changes += changes
                rel_path = file_path.relative_to(BASE_DIR)
                print(f"  ✅ {rel_path}: {changes} cambios")
    
    print()
    print("=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    print(f"Archivos analizados:  {total_files}")
    print(f"Archivos modificados: {files_modified}")
    print(f"Total de cambios:     {total_changes}")
    print()
    print("✨ Migración completada!")
    print()
    print("⚠️  IMPORTANTE:")
    print("1. Revisa los cambios con: git diff")
    print("2. Prueba la aplicación antes de hacer commit")
    print("3. Actualiza la configuración de Cloudflare si es necesario")
    print()

if __name__ == '__main__':
    main()
