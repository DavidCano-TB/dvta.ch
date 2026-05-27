#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para pagar a los ganadores que nunca recibieron su dinero
"""
import sqlite3
import os

db_bets_path = os.path.join('data', 'apuestas.db')
db_users_path = os.path.join('data', 'users.db')
db_tx_path = os.path.join('data', 'transactions.db')

print('=== PAGANDO GANADORES PENDIENTES ===\n')

# Conectar a las bases de datos
conn_bets = sqlite3.connect(db_bets_path)
conn_bets.row_factory = sqlite3.Row
c_bets = conn_bets.cursor()

conn_users = sqlite3.connect(db_users_path)
c_users = conn_users.cursor()

conn_tx = sqlite3.connect(db_tx_path)
c_tx = conn_tx.cursor()

# Obtener todas las apuestas ganadoras
apuestas_ganadoras = c_bets.execute('''
    SELECT au.porra_id, au.username, au.opcion, au.cantidad, au.ganancia,
           p.titulo, p.resultado
    FROM apuestas_usuarios au
    JOIN porras p ON au.porra_id = p.id
    WHERE p.estado = 'finalizada' AND au.ganancia > 0
    ORDER BY au.porra_id, au.username
''').fetchall()

total_pagado = 0.0
pagos_realizados = 0

for a in apuestas_ganadoras:
    username = a["username"]
    ganancia = a["ganancia"]
    titulo = a["titulo"]
    porra_id = a["porra_id"]
    
    # Verificar si ya existe transacción
    tx_existente = c_tx.execute('''
        SELECT id FROM transactions
        WHERE to_user = ? AND concept LIKE ? AND amount = ?
        LIMIT 1
    ''', (username, f'%{titulo}%', ganancia)).fetchone()
    
    if tx_existente:
        print(f'⏭️  @{username} - Porra #{porra_id}: Ya tiene transacción de pago')
        continue
    
    # Pagar al ganador
    print(f'💰 Pagando a @{username}:')
    print(f'   Porra: {titulo}')
    print(f'   Ganancia: {ganancia} DVDcoins')
    
    # Actualizar balance
    c_users.execute('''
        UPDATE users SET balance = balance + ?
        WHERE username = ?
    ''', (ganancia, username))
    
    # Registrar transacción
    c_tx.execute('''
        INSERT INTO transactions (from_user, to_user, amount, concept)
        VALUES (?, ?, ?, ?)
    ''', (f"Porra: {titulo}", username, ganancia, f"Pago retroactivo - Ganancia en '{titulo}'"))
    
    print(f'   ✅ Pagado correctamente\n')
    
    total_pagado += ganancia
    pagos_realizados += 1

# Commit todos los cambios
conn_users.commit()
conn_tx.commit()

# Cerrar conexiones
conn_bets.close()
conn_users.close()
conn_tx.close()

print(f'\n=== RESUMEN ===')
print(f'Total pagos realizados: {pagos_realizados}')
print(f'Total monto pagado: {total_pagado} DVDcoins')
print(f'\n✅ Proceso completado')

# Mostrar balances actualizados
print(f'\n=== BALANCES ACTUALIZADOS ===')
conn_users = sqlite3.connect(db_users_path)
conn_users.row_factory = sqlite3.Row
c_users = conn_users.cursor()

usuarios_afectados = set(a["username"] for a in apuestas_ganadoras)
for username in usuarios_afectados:
    user = c_users.execute('SELECT balance FROM users WHERE username = ?', (username,)).fetchone()
    if user:
        print(f'@{username}: {user["balance"]} DVDcoins')

conn_users.close()
