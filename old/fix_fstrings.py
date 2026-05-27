#!/usr/bin/env python3
"""
Script simple para corregir f-strings con backslashes
"""

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar el patrón problemático
content = content.replace(
    r'(f"Porra: {porra[\'titulo\']}", a["username"], a["cantidad"], f"Devolución (sin ganadores) - \'{porra[\'titulo\']}\'")',
    r'(f"Porra: {titulo_porra}", a["username"], a["cantidad"], f"Devolución (sin ganadores) - ''{titulo_porra}''")'
)

content = content.replace(
    r'(f"Porra: {porra[\'titulo\']}", a["username"], a["cantidad"], f"Devolución (cancelada) - \'{porra[\'titulo\']}\'")',
    r'(f"Porra: {titulo_porra}", a["username"], a["cantidad"], f"Devolución (cancelada) - ''{titulo_porra}''")'
)

# Agregar la variable titulo_porra antes de cada uso
import re

# Patrón: buscar "# Record transaction" seguido de ct = db_tx() y ct.execute con el f-string problemático
pattern = r'(# Record transaction\s+ct = db_tx\(\)\s+ct\.execute\("""[^"]+""", \(f"Porra: \{titulo_porra\}")'

replacement = r'# Record transaction\n            ct = db_tx()\n            titulo_porra = porra[\'titulo\']\n            ct.execute("""\n                INSERT INTO transactions (from_user, to_user, amount, concept)\n                VALUES (?, ?, ?, ?)\n            """, (f"Porra: {titulo_porra}"'

content = re.sub(pattern, replacement, content)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ F-strings corregidos")
