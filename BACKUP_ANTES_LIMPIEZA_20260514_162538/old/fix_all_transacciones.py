#!/usr/bin/env python3
"""
Script para corregir TODAS las transacciones de una vez
"""

with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar y corregir línea por línea
for i, line in enumerate(lines):
    # Corregir f-strings con backslashes
    if r"f\"Porra: {porra[\'titulo\']}" in line:
        # Reemplazar por variable temporal
        lines[i] = line.replace(r"f\"Porra: {porra[\'titulo\']}", 'f"Porra: {titulo_porra}"')
        # Agregar línea anterior con la variable
        if i > 0 and 'titulo_porra = ' not in lines[i-1]:
            indent = len(line) - len(line.lstrip())
            lines.insert(i, ' ' * indent + "titulo_porra = porra['titulo']\n")
    
    if r"f\"Devolución (sin ganadores) - \'{porra[\'titulo\']}\'" in line:
        lines[i] = line.replace(r"f\"Devolución (sin ganadores) - \'{porra[\'titulo\']}\'", 'f"Devolución (sin ganadores) - \'{titulo_porra}\'"')
    
    if r"f\"Devolución (cancelada) - \'{porra[\'titulo\']}\'" in line:
        lines[i] = line.replace(r"f\"Devolución (cancelada) - \'{porra[\'titulo\']}\'", 'f"Devolución (cancelada) - \'{titulo_porra}\'"')

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Transacciones corregidas")
