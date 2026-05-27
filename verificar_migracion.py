#!/usr/bin/env python3
"""
Script para verificar que la migración a /bank fue completa
Busca patrones que puedan indicar rutas no actualizadas
"""

import os
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent

# Patrones sospechosos que podrían indicar rutas no actualizadas
SUSPICIOUS_PATTERNS = [
    # Rutas API sin /bank
    (r'fetch\([\'"]/(api/[^\'"]+)[\'"]', 'Llamada API sin /bank'),
    (r'href=[\'"]/(api/[^\'"]+)[\'"]', 'Link API sin /bank'),
    
    # Rutas estáticas sin /bank (excepto URLs externas)
    (r'src=[\'"]/(static/[^\'"]+)[\'"]', 'Script/img sin /bank'),
    (r'href=[\'"]/(static/[^\'"]+)[\'"]', 'Link CSS sin /bank'),
    
    # Decoradores FastAPI sin /bank
    (r'@app\.(get|post|put|delete|patch)\("(/[^"]*)"', 'Ruta FastAPI sin /bank'),
    
    # app.mount sin /bank
    (r'app\.mount\("(/[^"]+)"', 'Mount sin /bank'),
]

# Archivos a excluir
EXCLUDE_PATTERNS = [
    '.git', '__pycache__', 'node_modules', '.vscode', '.vs',
    'backup', 'backup_30min', 'BACKUP_ANTES_LIMPIEZA',
    '*.db', '*.pyc', '*.log', 'migrate_to_bank.py', 'verificar_migracion.py',
    'old', 'venv', 'env', '.venv', 'site-packages'
]

def should_exclude(path):
    """Verifica si un archivo/directorio debe ser excluido"""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False

def check_file(file_path):
    """Verifica un archivo en busca de patrones sospechosos"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        for pattern, description in SUSPICIOUS_PATTERNS:
            matches = re.finditer(pattern, content)
            for match in matches:
                route = match.group(1) if match.lastindex >= 1 else match.group(0)
                
                # Filtrar falsos positivos
                if '/bank' in route:
                    continue
                if route.startswith('http://') or route.startswith('https://'):
                    continue
                if route.startswith('//'):  # URLs protocol-relative
                    continue
                
                # Obtener número de línea
                line_num = content[:match.start()].count('\n') + 1
                
                issues.append({
                    'line': line_num,
                    'match': match.group(0),
                    'description': description
                })
        
        return issues
    
    except Exception as e:
        return None

def main():
    """Función principal"""
    print("=" * 70)
    print("🔍 Verificación de Migración a /bank")
    print("=" * 70)
    print()
    
    # Contadores
    total_files = 0
    files_with_issues = 0
    total_issues = 0
    issues_by_file = defaultdict(list)
    
    # Extensiones a verificar
    extensions = ['.py', '.js', '.html', '.htm']
    
    print("📁 Analizando archivos...")
    print()
    
    # Recorrer todos los archivos
    for ext in extensions:
        for file_path in BASE_DIR.rglob(f'*{ext}'):
            if should_exclude(file_path):
                continue
            
            total_files += 1
            issues = check_file(file_path)
            
            if issues:
                files_with_issues += 1
                total_issues += len(issues)
                issues_by_file[file_path] = issues
    
    # Mostrar resultados
    if issues_by_file:
        print("⚠️  POSIBLES PROBLEMAS ENCONTRADOS:")
        print()
        
        for file_path, issues in sorted(issues_by_file.items()):
            rel_path = file_path.relative_to(BASE_DIR)
            print(f"📄 {rel_path}")
            
            for issue in issues:
                print(f"   Línea {issue['line']}: {issue['description']}")
                print(f"   → {issue['match']}")
            print()
    else:
        print("✅ No se encontraron problemas!")
        print()
    
    # Resumen
    print("=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    print(f"Archivos analizados:      {total_files}")
    print(f"Archivos con problemas:   {files_with_issues}")
    print(f"Total de problemas:       {total_issues}")
    print()
    
    if total_issues == 0:
        print("✨ La migración parece estar completa!")
        print()
        print("Próximos pasos:")
        print("1. Iniciar el servidor: python main.py")
        print("2. Probar en el navegador: http://localhost:8000/bank")
        print("3. Verificar que todo funcione correctamente")
        print("4. Configurar Cloudflare si es necesario")
    else:
        print("⚠️  Se encontraron posibles problemas.")
        print("Revisa los archivos listados arriba y corrige las rutas si es necesario.")
        print()
        print("Nota: Algunos pueden ser falsos positivos (URLs externas, comentarios, etc.)")
    
    print()

if __name__ == '__main__':
    main()
