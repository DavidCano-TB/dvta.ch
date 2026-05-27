#!/usr/bin/env python3
"""
Script para corregir errores de sintaxis en f-strings con comillas escapadas
"""

import re

def corregir_sintaxis():
    """Corrige los f-strings con comillas escapadas"""
    
    print("🚀 Corrigiendo sintaxis de f-strings\n")
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón problemático: f"Porra: {porra[\'titulo\']}"
    # Reemplazar por: titulo_porra = porra['titulo'] y luego f"Porra: {titulo_porra}"
    
    # 1. Buscar y reemplazar el patrón de devolución sin ganadores
    pattern1 = r'(\s+)(# Record transaction\s+ct = db_tx\(\)\s+ct\.execute\("""\s+INSERT INTO transactions[^"]+""", \(f"Porra: \{porra\[\\\'titulo\\\'\]\}", a\["username"\], a\["cantidad"\], f"Devolución \(sin ganadores\) - \\\'[^\']+\\\'\"\)\))'
    
    replacement1 = r'''\1# Record transaction
            ct = db_tx()
            titulo_porra = porra['titulo']
            ct.execute("""
                INSERT INTO transactions (from_user, to_user, amount, concept)
                VALUES (?, ?, ?, ?)
            """, (f"Porra: {titulo_porra}", a["username"], a["cantidad"], f"Devolución (sin ganadores) - '{titulo_porra}'"))'''
    
    content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)
    
    # 2. Buscar y reemplazar el patrón de devolución por cancelación
    pattern2 = r'(\(f"Porra: \{porra\[\\\'titulo\\\'\]\}", a\["username"\], a\["cantidad"\], f"Devolución \(cancelada\) - \\\'[^\']+\\\'\"\))'
    
    replacement2 = r'(f"Porra: {titulo_porra}", a["username"], a["cantidad"], f"Devolución (cancelada) - \'{titulo_porra}\'")'
    
    # Buscar el contexto y agregar la variable
    pattern2_context = r'(# Record transaction\s+ct = db_tx\(\)\s+ct\.execute\("""\s+INSERT INTO transactions[^"]+""", \(f"Porra: \{porra\[\\\'titulo\\\'\]\}", a\["username"\], a\["cantidad"\], f"Devolución \(cancelada\) - \\\'[^\']+\\\'\"\)\))'
    
    replacement2_context = r'''# Record transaction
        ct = db_tx()
        titulo_porra = porra['titulo']
        ct.execute("""
            INSERT INTO transactions (from_user, to_user, amount, concept)
            VALUES (?, ?, ?, ?)
        """, (f"Porra: {titulo_porra}", a["username"], a["cantidad"], f"Devolución (cancelada) - '{titulo_porra}'"))'''
    
    content = re.sub(pattern2_context, replacement2_context, content, flags=re.MULTILINE)
    
    # Guardar archivo
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Sintaxis corregida")
    print("   - F-strings con comillas escapadas corregidos")
    print("   - Variables temporales agregadas para evitar backslashes")

if __name__ == '__main__':
    corregir_sintaxis()
