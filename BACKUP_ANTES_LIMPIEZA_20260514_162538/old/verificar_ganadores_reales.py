#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import os

db_bets_path = os.path.join('data', 'apuestas.db')

conn = sqlite3.connect(db_bets_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print('=== VERIFICANDO GANADORES CON GANANCIA > 0 ===\n')

# Obtener todas las apuestas con ganancia > 0
apuestas_ganadoras = c.execute('''
    SELECT au.porra_id, au.username, au.opcion, au.cantidad, au.ganancia, au.pagado,
           p.titulo, p.resultado
    FROM apuestas_usuarios au
    JOIN porras p ON au.porra_id = p.id
    WHERE p.estado = 'finalizada' AND au.ganancia > 0
    ORDER BY au.porra_id, au.username
''').fetchall()

print(f'Total apuestas ganadoras encontradas: {len(apuestas_ganadoras)}\n')

for a in apuestas_ganadoras:
    print(f'Porra #{a["porra_id"]}: {a["titulo"]}')
    print(f'  Resultado: {a["resultado"]}')
    print(f'  Ganador: @{a["username"]}')
    print(f'  Apostó: {a["cantidad"]} en "{a["opcion"]}"')
    print(f'  Ganancia calculada: {a["ganancia"]} DVDcoins')
    print(f'  Pagado: {"✅ SÍ" if a["pagado"] == 1 else "❌ NO"}')
    print()

# Verificar transacciones
print('\n=== VERIFICANDO TRANSACCIONES DE PAGO ===\n')

db_tx_path = os.path.join('data', 'transactions.db')
conn_tx = sqlite3.connect(db_tx_path)
conn_tx.row_factory = sqlite3.Row
c_tx = conn_tx.cursor()

for a in apuestas_ganadoras:
    # Buscar transacción de pago
    tx = c_tx.execute('''
        SELECT * FROM transactions
        WHERE to_user = ? AND concept LIKE ?
        ORDER BY id DESC
        LIMIT 1
    ''', (a["username"], f'%{a["titulo"]}%')).fetchone()
    
    if tx:
        print(f'✅ @{a["username"]} - Porra #{a["porra_id"]}: Transacción encontrada por {tx["amount"]} DVDcoins')
    else:
        print(f'❌ @{a["username"]} - Porra #{a["porra_id"]}: NO HAY TRANSACCIÓN DE PAGO - GANANCIA: {a["ganancia"]} DVDcoins')

conn.close()
conn_tx.close()
