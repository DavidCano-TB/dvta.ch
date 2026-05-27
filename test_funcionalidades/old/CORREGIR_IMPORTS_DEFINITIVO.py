#!/usr/bin/env python3
"""
🔧 CORREGIR IMPORTS DEFINITIVO
Modifica todos los archivos de test para importar desde el directorio local
"""
from pathlib import Path
import re

def fix_imports_in_file(file_path):
    """Corrige los imports en un archivo"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar las líneas de import
    new_lines = []
    skip_next = False
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
            
        # Si encontramos el import de sys/os
        if 'import sys' in line and i + 1 < len(lines) and 'import os' in lines[i + 1]:
            # Reemplazar con el nuevo código
            new_lines.append('import sys\n')
            new_lines.append('import os\n')
            new_lines.append('\n')
            new_lines.append('# Importar desde directorio local primero\n')
            new_lines.append('sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n')
            
            # Saltar las líneas viejas de sys.path
            j = i + 2
            while j < len(lines) and ('sys.path' in lines[j] or lines[j].strip() == ''):
                j += 1
            
            # Continuar desde después de las líneas saltadas
            for k in range(i + 2, j):
                if k < len(lines):
                    skip_next = True
            
            continue
        
        new_lines.append(line)
    
    # Escribir el archivo modificado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    return True

def main():
    print("=" * 80)
    print("  🔧 CORRIGIENDO IMPORTS DEFINITIVO")
    print("=" * 80)
    print()
    
    base_dir = Path(__file__).parent
    
    # Buscar todos los archivos test_*.py
    test_files = list(base_dir.glob("*/test_*.py"))
    
    fixed = 0
    
    for test_file in test_files:
        try:
            fix_imports_in_file(test_file)
            print(f"✅ Corregido: {test_file.parent.name}/{test_file.name}")
            fixed += 1
        except Exception as e:
            print(f"❌ Error en {test_file.name}: {e}")
    
    print()
    print("=" * 80)
    print(f"  ✅ CORRECCIÓN COMPLETADA - {fixed} archivos corregidos")
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
