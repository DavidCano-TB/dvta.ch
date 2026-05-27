#!/usr/bin/env python3
"""
Script final para aplicar TODOS los cambios de transacciones correctamente
"""

import re

def aplicar_cambios():
    """Aplica todos los cambios de transacciones"""
    
    print("🚀 Aplicando cambios de transacciones\n")
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    cambios = []
    
    # 1. Cambiar transacción de apuesta: obtener título y usarlo
    pattern1 = r'(# Record transaction for bet\s+ct = db_tx\(\)\s+ct\.execute\("""\s+INSERT INTO transactions[^"]+""", \(user, "sistema", body\.cantidad, f"Apuesta porra #\{body\.porra_id\} - \{body\.opcion\}"\)\))'
    
    replacement1 = '''# Get porra title for transaction
    porra_titulo = c.execute("SELECT titulo FROM porras WHERE id = ?", (body.porra_id,)).fetchone()
    titulo = porra_titulo["titulo"] if porra_titulo else f"Porra #{body.porra_id}"
    
    # Record transaction for bet
    ct = db_tx()
    ct.execute("""
        INSERT INTO transactions (from_user, to_user, amount, concept)
        VALUES (?, ?, ?, ?)
    """, (user, f"Porra: {titulo}", body.cantidad, f"Apuesta en '{titulo}' - Opción: {body.opcion}"))'''
    
    if re.search(pattern1, content):
        content = re.sub(pattern1, replacement1, content)
        cambios.append("Transacción de apuesta")
    
    # 2. Cambiar transacciones de ganancia (3 lugares)
    # 2a. En porra_resolver
    pattern2a = r'(\("sistema", a\["username"\], ganancia, f"Ganador porra: \{body\.porra_id\}"\))'
    replacement2a = r'(f"Porra: {porra[\'titulo\']}", a["username"], ganancia, f"Ganancia en \'{porra[\'titulo\']}\'")'
    
    count2a = len(re.findall(pattern2a, content))
    if count2a > 0:
        content = re.sub(pattern2a, replacement2a, content)
        cambios.append(f"Ganancia en porra_resolver: {count2a}")
    
    # 2b. En porra_cerrar_y_resolver
    pattern2b = r'(\("sistema", a\["username"\], ganancia, f"Ganador porra #\{porra_id\}"\))'
    replacement2b = r'(f"Porra: {porra[\'titulo\']}", a["username"], ganancia, f"Ganancia en \'{porra[\'titulo\']}\'")'
    
    count2b = len(re.findall(pattern2b, content))
    if count2b > 0:
        content = re.sub(pattern2b, replacement2b, content)
        cambios.append(f"Ganancia en cerrar_y_resolver: {count2b}")
    
    # 2c. En porra_cerrar_y_resolver_admin
    pattern2c = r'(\("sistema", a\["username"\], ganancia, f"Ganador porra #\{porra_id\} \(resuelto por admin \{user\}\)"\))'
    replacement2c = r'(f"Porra: {porra[\'titulo\']}", a["username"], ganancia, f"Ganancia en \'{porra[\'titulo\']}\' (resuelto por admin {user})")'
    
    count2c = len(re.findall(pattern2c, content))
    if count2c > 0:
        content = re.sub(pattern2c, replacement2c, content)
        cambios.append(f"Ganancia en admin: {count2c}")
    
    # 3. Cambiar devoluciones sin ganadores (2 lugares)
    pattern3 = r'(\("sistema", a\["username"\], a\["cantidad"\], f"Devolución porra sin ganadores: \{porra\[\'titulo\'\]\}"\))'
    replacement3 = r'(f"Porra: {porra[\'titulo\']}", a["username"], a["cantidad"], f"Devolución (sin ganadores) - \'{porra[\'titulo\']}\'")'
    
    count3 = len(re.findall(pattern3, content))
    if count3 > 0:
        content = re.sub(pattern3, replacement3, content)
        cambios.append(f"Devolución sin ganadores: {count3}")
    
    # 4. Cambiar devolución por cancelación
    pattern4 = r'(\("sistema", a\["username"\], a\["cantidad"\], f"Devolución por cancelación de porra: \{porra\[\'titulo\'\]\}"\))'
    replacement4 = r'(f"Porra: {porra[\'titulo\']}", a["username"], a["cantidad"], f"Devolución (cancelada) - \'{porra[\'titulo\']}\'")'
    
    count4 = len(re.findall(pattern4, content))
    if count4 > 0:
        content = re.sub(pattern4, replacement4, content)
        cambios.append(f"Devolución por cancelación: {count4}")
    
    # 5. Asegurar que porra_resolver obtiene el título
    pattern5 = r'(porra = c\.execute\("""\s+SELECT estado, comision, opciones_json FROM porras WHERE id = \?)'
    replacement5 = r'porra = c.execute("""\n        SELECT estado, comision, opciones_json, titulo FROM porras WHERE id = ?'
    
    if re.search(pattern5, content):
        content = re.sub(pattern5, replacement5, content)
        cambios.append("Agregado titulo en SELECT de porra_resolver")
    
    # 6. Actualizar _create_porra_page para crear archivos con nombres descriptivos
    pattern6 = r'(# Write page\s+page_path = os\.path\.join\(page_dir, f"porra_\{porra_id\}\.html"\)\s+with open\(page_path, \'w\', encoding=\'utf-8\'\) as f:\s+f\.write\(html_content\)\s+logger\.info\(f"Created porra page: porra_\{porra_id\}\.html"\))'
    
    replacement6 = '''# Sanitize titulo for filename (remove special characters)
        import re
        titulo_safe = re.sub(r'[<>:"/\\\\|?*]', '', titulo)  # Remove invalid filename chars
        titulo_safe = titulo_safe.strip()[:50]  # Limit length to 50 chars
        
        # Write page with descriptive name: porra "Titulo de la Porra".html
        # But keep porra_ID.html for backwards compatibility
        page_path_descriptive = os.path.join(page_dir, f'porra "{titulo_safe}".html')
        page_path_id = os.path.join(page_dir, f"porra_{porra_id}.html")
        
        # Write both files (same content, different names)
        with open(page_path_descriptive, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        with open(page_path_id, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f'Created porra pages: porra "{titulo_safe}".html and porra_{porra_id}.html')'''
    
    if re.search(pattern6, content):
        content = re.sub(pattern6, replacement6, content)
        cambios.append("Actualizado _create_porra_page para nombres descriptivos")
    
    # Guardar archivo
    if cambios:
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Cambios aplicados:")
        for cambio in cambios:
            print(f"   - {cambio}")
        print(f"\n✅ Total de cambios: {len(cambios)}")
        return True
    else:
        print("ℹ️  No se encontraron cambios para aplicar")
        return False

if __name__ == '__main__':
    aplicar_cambios()
