#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar todos los balances y transacciones
"""
import sqlite3
import os

db_bets_path = os.path.join('data', 'apuestas.db')
db_users_path = os.path.join('data', 'users.db')
db_tx_path = os.path.join('data', 'transactions.db')

print('=== BALANCES ACTUALES DE USUARIOS ===\n')

conn_users = sqlite3.connect(db_users_path)
conn_users.row_factory = sqlite3.Row
c_users = conn_users.cursor()

usuarios = c_users.execute('SELECT username, balance FROM users ORDER BY username').fetchall()
for u in usuarios:
    print(f'{u["username"]}: {u["balance"]} DVDcoins')

print('\n=== VERIFICANDO HISTORIAL DE APUESTAS POR USUARIO ===\n')

conn_bets = sqlite3.connect(db_bets_path)
conn_bets.row_factory = sqlite3.Row
c_bets = conn_bets.cursor()

conn_tx = sqlite3.connect(db_tx_path)
conn_tx.row_factory = sqlite3.Row
c_tx = conn_tx.cursor()

# Verificar victorzahyr específicamente
print('--- USUARIO: victorzahyr ---')
apuestas_victor = c_bets.execute('''
    SELECT au.porra_id, au.opcion, au.cantidad, au.ganancia, au.pagado,
           p.titulo, p.resultado, p.estado
    FROM apuestas_usuarios au
    JOIN porras p ON au.porra_id = p.id
    WHERE au.username = 'victorzahyr'
    ORDER BY au.porra_id
''').fetchall()

if apuestas_victor:
    for a in apuestas_victor:
        print(f'\nPorra #{a["porra_id"]}: {a["titulo"]}')
        print(f'  Estado: {a["estado"]}')
        print(f'  Apostó: {a["cantidad"]} en "{a["opcion"]}"')
        print(f'  Resultado: {a["resultado"]}')
        print(f'  Ganancia: {a["ganancia"]} DVDcoins')
        print(f'  Pagado: {"✅ SÍ" if a["pagado"] == 1 else "❌ NO"}')
        
        # Buscar transacción de pago
        if a["ganancia"] and a["ganancia"] > 0:
            tx = c_tx.execute('''
                SELECT * FROM transactions
                WHERE to_user = 'victorzahyr' AND concept LIKE ?
                ORDER BY id DESC LIMIT 1
            ''', (f'%{a["titulo"]}%',)).fetchone()
            
            if tx:
                print(f'  Transacción: ✅ Encontrada - {tx["amount"]} DVDcoins')
            else:
                print(f'  Transacción: ❌ NO ENCONTRADA - FALTA PAGO DE {a["ganancia"]} DVDcoins')
else:
    print('No tiene apuestas registradas')

# Verificar TODOS los usuarios con ganancias
print('\n\n=== VERIFICANDO TODOS LOS GANADORES ===\n')

todas_ganancias = c_bets.execute('''
    SELECT au.porra_id, au.username, au.opcion, au.cantidad, au.ganancia, au.pagado,
           p.titulo, p.resultado, p.estado
    FROM apuestas_usuarios au
    JOIN porras p ON au.porra_id = p.id
    WHERE p.estado = 'finalizada' AND au.ganancia > 0
    ORDER BY au.username, au.porra_id
''').fetchall()

usuarios_con_problemas = {}

for a in todas_ganancias:
    # Buscar transacción
    tx = c_tx.execute('''
        SELECT * FROM transactions
        WHERE to_user = ? AND concept LIKE ? AND amount = ?
        ORDER BY id DESC LIMIT 1
    ''', (a["username"], f'%{a["titulo"]}%', a["ganancia"])).fetchone()
    
    if not tx:
        if a["username"] not in usuarios_con_problemas:
            usuarios_con_problemas[a["username"]] = []
        usuarios_con_problemas[a["username"]].append({
            'porra_id': a["porra_id"],
            'titulo': a["titulo"],
            'ganancia': a["ganancia"]
        })

if usuarios_con_problemas:
    print('❌ USUARIOS CON PAGOS FALTANTES:\n')
    total_faltante = 0
    for username, problemas in usuarios_con_problemas.items():
        print(f'@{username}:')
        for p in problemas:
            print(f'  - Porra #{p["porra_id"]}: {p["titulo"]} - FALTA: {p["ganancia"]} DVDcoins')
            total_faltante += p["ganancia"]
        print()
    print(f'TOTAL FALTANTE: {total_faltante} DVDcoins')
else:
    print('✅ Todos los ganadores tienen sus transacciones de pago registradas')

conn_users.close()
conn_bets.close()
conn_tx.close()
