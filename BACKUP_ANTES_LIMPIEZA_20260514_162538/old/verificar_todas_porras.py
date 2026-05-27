#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar TODAS las porras y sus pagos
"""
import sqlite3
import os

db_bets_path = os.path.join('data', 'apuestas.db')
db_users_path = os.path.join('data', 'users.db')
db_tx_path = os.path.join('data', 'transactions.db')

conn_bets = sqlite3.connect(db_bets_path)
conn_bets.row_factory = sqlite3.Row
c_bets = conn_bets.cursor()

conn_tx = sqlite3.connect(db_tx_path)
conn_tx.row_factory = sqlite3.Row
c_tx = conn_tx.cursor()

print('=== TODAS LAS PORRAS FINALIZADAS ===\n')

porras = c_bets.execute('''
    SELECT id, titulo, estado, resultado
    FROM porras
    WHERE estado = 'finalizada'
    ORDER BY id
''').fetchall()

print(f'Total porras finalizadas: {len(porras)}\n')

total_sin_pagar = 0
usuarios_afectados = set()

for porra in porras:
    print(f'\n--- Porra #{porra["id"]}: {porra["titulo"]} ---')
    print(f'Resultado: {porra["resultado"]}')
    
    # Obtener todas las apuestas
    apuestas = c_bets.execute('''
        SELECT username, opcion, cantidad, ganancia, pagado
        FROM apuestas_usuarios
        WHERE porra_id = ?
        ORDER BY username
    ''', (porra["id"],)).fetchall()
    
    print(f'Total apuestas: {len(apuestas)}')
    
    # Verificar ganadores
    ganadores = [a for a in apuestas if a["ganancia"] and a["ganancia"] > 0]
    
    if ganadores:
        print(f'Ganadores: {len(ganadores)}')
        for g in ganadores:
            # Verificar transacción
            tx = c_tx.execute('''
                SELECT id, amount FROM transactions
                WHERE to_user = ? AND concept LIKE ? AND amount = ?
                LIMIT 1
            ''', (g["username"], f'%{porra["titulo"]}%', g["ganancia"])).fetchone()
            
            if tx:
                print(f'  ✅ @{g["username"]}: {g["ganancia"]} DVDcoins - PAGADO')
            else:
                print(f'  ❌ @{g["username"]}: {g["ganancia"]} DVDcoins - SIN TRANSACCIÓN')
                total_sin_pagar += g["ganancia"]
                usuarios_afectados.add(g["username"])
    else:
        print('Sin ganadores (empate o devolución)')

print(f'\n\n=== RESUMEN FINAL ===')
print(f'Total sin pagar: {total_sin_pagar} DVDcoins')
print(f'Usuarios afectados: {len(usuarios_afectados)}')
if usuarios_afectados:
    print(f'Usuarios: {", ".join(usuarios_afectados)}')

conn_bets.close()
conn_tx.close()
