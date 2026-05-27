#!/usr/bin/env python3
"""
🔧 CORREGIR TODOS LOS IMPORTS
Modifica todos los archivos de test para importar desde el directorio local
"""
from pathlib import Path
import re

def fix_imports_in_file(file_path):
    """Corrige los imports en un archivo"""
    print(f"Procesando: {file_path.parent.name}/{file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón a buscar: las líneas que modifican sys.path
    old_pattern = r'import sys\nimport os\nsys\.path\.append\(os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)\)'
    
    # Nuevo código
    new_code = '''import sys
import os

# Importar desde directorio local primero
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))'''
    
    # Reemplazar
    if 'sys.path.append(os.path.dirname(os.path.dirname' in content:
        content = re.sub(old_pattern, new_code, content)
        
        # Escribir el archivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Corregido")
        return True
    else:
        print(f"  ⚠️  No se encontró el patrón a corregir")
        return False

def main():
    print("=" * 80)
    print("  🔧 CORRIGIENDO TODOS LOS IMPORTS")
    print("=" * 80)
    print()
    
    base_dir = Path(__file__).parent
    
    # Buscar todos los archivos test_*.py en subdirectorios
    test_files = []
    for subdir in base_dir.iterdir():
        if subdir.is_dir() and not subdir.name.startswith('.'):
            for test_file in subdir.glob("test_*.py"):
                test_files.append(test_file)
    
    print(f"Encontrados {len(test_files)} archivos de test\n")
    
    fixed = 0
    
    for test_file in sorted(test_files):
        try:
            if fix_imports_in_file(test_file):
                fixed += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print()
    print("=" * 80)
    print(f"  ✅ CORRECCIÓN COMPLETADA - {fixed}/{len(test_files)} archivos corregidos")
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
