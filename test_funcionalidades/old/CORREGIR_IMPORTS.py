#!/usr/bin/env python3
"""
🔧 CORREGIR IMPORTS
Corrige los imports en todos los archivos de test
"""
from pathlib import Path
import re

def fix_imports_in_file(file_path):
    """Corrige los imports en un archivo"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el patrón de import incorrecto
    old_pattern = r"sys\.path\.append\(os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)\)"
    new_pattern = "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"
    
    if old_pattern in content:
        content = re.sub(old_pattern, new_pattern, content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    return False

def main():
    print("=" * 80)
    print("  🔧 CORRIGIENDO IMPORTS")
    print("=" * 80)
    print()
    
    base_dir = Path(__file__).parent
    
    # Buscar todos los archivos test_*.py
    test_files = list(base_dir.glob("*/test_*.py"))
    
    fixed = 0
    
    for test_file in test_files:
        if fix_imports_in_file(test_file):
            print(f"✅ Corregido: {test_file.parent.name}/{test_file.name}")
            fixed += 1
        else:
            print(f"⏭️  Sin cambios: {test_file.parent.name}/{test_file.name}")
    
    print()
    print("=" * 80)
    print(f"  ✅ CORRECCIÓN COMPLETADA - {fixed} archivos corregidos")
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
