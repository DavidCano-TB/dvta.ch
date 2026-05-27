#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que el sistema de pagos funciona correctamente
"""
import sqlite3
import os

def verificar_integridad_pagos():
    """Verifica que todos los pagos estén correctos"""
    
    db_bets_path = os.path.join('data', 'apuestas.db')
    db_users_path = os.path.join('data', 'users.db')
    db_tx_path = os.path.join('data', 'transactions.db')
    
    conn_bets = sqlite3.connect(db_bets_path)
    conn_bets.row_factory = sqlite3.Row
    c_bets = conn_bets.cursor()
    
    conn_tx = sqlite3.connect(db_tx_path)
    conn_tx.row_factory = sqlite3.Row
    c_tx = conn_tx.cursor()
    
    print('=' * 60)
    print('VERIFICACIÓN DE INTEGRIDAD DEL SISTEMA DE PAGOS')
    print('=' * 60)
    
    # 1. Verificar que todas las apuestas con ganancia > 0 tengan transacción
    print('\n1. Verificando transacciones de ganadores...')
    
    ganadores = c_bets.execute('''
        SELECT au.porra_id, au.username, au.ganancia, p.titulo
        FROM apuestas_usuarios au
        JOIN porras p ON au.porra_id = p.id
        WHERE p.estado = 'finalizada' AND au.ganancia > 0
    ''').fetchall()
    
    problemas_transacciones = []
    
    for g in ganadores:
        tx = c_tx.execute('''
            SELECT id FROM transactions
            WHERE to_user = ? AND concept LIKE ? AND amount = ?
            LIMIT 1
        ''', (g["username"], f'%{g["titulo"]}%', g["ganancia"])).fetchone()
        
        if not tx:
            problemas_transacciones.append({
                'usuario': g["username"],
                'porra': g["porra_id"],
                'ganancia': g["ganancia"]
            })
    
    if problemas_transacciones:
        print(f'   ❌ ENCONTRADOS {len(problemas_transacciones)} PAGOS SIN TRANSACCIÓN:')
        for p in problemas_transacciones:
            print(f'      - @{p["usuario"]} - Porra #{p["porra"]} - {p["ganancia"]} DVDcoins')
    else:
        print(f'   ✅ Todas las ganancias tienen transacción registrada ({len(ganadores)} verificadas)')
    
    # 2. Verificar que todas las apuestas en porras finalizadas estén marcadas como pagadas
    print('\n2. Verificando estado de pagos...')
    
    apuestas_sin_pagar = c_bets.execute('''
        SELECT COUNT(*) as count
        FROM apuestas_usuarios au
        JOIN porras p ON au.porra_id = p.id
        WHERE p.estado = 'finalizada' AND au.pagado = 0
    ''').fetchone()
    
    if apuestas_sin_pagar["count"] > 0:
        print(f'   ❌ HAY {apuestas_sin_pagar["count"]} APUESTAS SIN MARCAR COMO PAGADAS')
        
        # Mostrar detalles
        sin_pagar = c_bets.execute('''
            SELECT au.porra_id, au.username, au.cantidad, p.titulo
            FROM apuestas_usuarios au
            JOIN porras p ON au.porra_id = p.id
            WHERE p.estado = 'finalizada' AND au.pagado = 0
        ''').fetchall()
        
        for a in sin_pagar:
            print(f'      - Porra #{a["porra_id"]}: @{a["username"]} - {a["cantidad"]} DVDcoins')
    else:
        print(f'   ✅ Todas las apuestas en porras finalizadas están marcadas como pagadas')
    
    # 3. Verificar consistencia de ganancias
    print('\n3. Verificando consistencia de ganancias...')
    
    porras_finalizadas = c_bets.execute('''
        SELECT id, titulo, resultado FROM porras WHERE estado = 'finalizada'
    ''').fetchall()
    
    problemas_consistencia = []
    
    for porra in porras_finalizadas:
        # Obtener todas las apuestas
        apuestas = c_bets.execute('''
            SELECT username, opcion, cantidad, ganancia
            FROM apuestas_usuarios
            WHERE porra_id = ?
        ''', (porra["id"],)).fetchall()
        
        total_apostado = sum(a["cantidad"] for a in apuestas)
        total_pagado = sum(a["ganancia"] for a in apuestas if a["ganancia"])
        
        # Verificar que el total pagado no exceda el total apostado
        if total_pagado > total_apostado + 0.01:  # Margen de error por redondeo
            problemas_consistencia.append({
                'porra_id': porra["id"],
                'titulo': porra["titulo"],
                'apostado': total_apostado,
                'pagado': total_pagado
            })
    
    if problemas_consistencia:
        print(f'   ❌ ENCONTRADOS {len(problemas_consistencia)} PROBLEMAS DE CONSISTENCIA:')
        for p in problemas_consistencia:
            print(f'      - Porra #{p["porra_id"]}: Apostado: {p["apostado"]}, Pagado: {p["pagado"]}')
    else:
        print(f'   ✅ Todas las porras tienen ganancias consistentes ({len(porras_finalizadas)} verificadas)')
    
    # Resumen final
    print('\n' + '=' * 60)
    print('RESUMEN')
    print('=' * 60)
    
    total_problemas = len(problemas_transacciones) + apuestas_sin_pagar["count"] + len(problemas_consistencia)
    
    if total_problemas == 0:
        print('✅ SISTEMA FUNCIONANDO CORRECTAMENTE')
        print('   - Todas las transacciones registradas')
        print('   - Todos los pagos marcados correctamente')
        print('   - Todas las ganancias son consistentes')
    else:
        print(f'❌ SE ENCONTRARON {total_problemas} PROBLEMAS')
        print('   Revisar los detalles arriba')
    
    print('=' * 60)
    
    conn_bets.close()
    conn_tx.close()
    
    return total_problemas == 0

if __name__ == '__main__':
    resultado = verificar_integridad_pagos()
    exit(0 if resultado else 1)
