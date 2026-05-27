#!/usr/bin/env python3
"""
Script para actualizar todas las transacciones de "sistema" a nombre de porra
"""

import re

def actualizar_transacciones():
    """Actualiza las transacciones en main.py"""
    
    print("🚀 Actualizando transacciones en main.py\n")
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    cambios = []
    
    # 1. Devolución sin ganadores (2 ocurrencias)
    pattern1 = r'\("sistema", a\["username"\], a\["cantidad"\], f"Devolución porra sin ganadores: \{porra\[\'titulo\'\]\}"\)'
    replacement1 = r'(f"Porra: {porra[\'titulo\']}", a["username"], a["cantidad"], f"Devolución (sin ganadores) - \'{porra[\'titulo\']}\'")'
    
    count1 = len(re.findall(pattern1, content))
    if count1 > 0:
        content = re.sub(pattern1, replacement1, content)
        cambios.append(f"Devolución sin ganadores: {count1} ocurrencias")
    
    # 2. Devolución por cancelación
    pattern2 = r'\("sistema", a\["username"\], a\["cantidad"\], f"Devolución por cancelación de porra: \{porra\[\'titulo\'\]\}"\)'
    replacement2 = r'(f"Porra: {porra[\'titulo\']}", a["username"], a["cantidad"], f"Devolución (cancelada) - \'{porra[\'titulo\']}\'")'
    
    count2 = len(re.findall(pattern2, content))
    if count2 > 0:
        content = re.sub(pattern2, replacement2, content)
        cambios.append(f"Devolución por cancelación: {count2} ocurrencias")
    
    # Guardar archivo
    if cambios:
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Cambios aplicados:")
        for cambio in cambios:
            print(f"   - {cambio}")
        print(f"\n✅ Total de transacciones actualizadas: {count1 + count2}")
        return True
    else:
        print("ℹ️  No se encontraron transacciones para actualizar")
        return False

if __name__ == '__main__':
    actualizar_transacciones()
