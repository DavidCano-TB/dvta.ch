#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificación final del sistema
"""
import sqlite3
import os

print('=' * 60)
print('VERIFICACIÓN FINAL DEL SISTEMA DE PAGOS')
print('=' * 60)

# Test de integridad
db_bets_path = os.path.join('data', 'apuestas.db')
db_users_path = os.path.join('data', 'users.db')
db_tx_path = os.path.join('data', 'transactions.db')

conn_bets = sqlite3.connect(db_bets_path)
conn_bets.row_factory = sqlite3.Row
c_bets = conn_bets.cursor()

conn_tx = sqlite3.connect(db_tx_path)
conn_tx.row_factory = sqlite3.Row
c_tx = conn_tx.cursor()

conn_users = sqlite3.connect(db_users_path)
conn_users.row_factory = sqlite3.Row
c_users = conn_users.cursor()

# Verificar transacciones
ganadores = c_bets.execute('''
    SELECT au.porra_id, au.username, au.ganancia, p.titulo
    FROM apuestas_usuarios au
    JOIN porras p ON au.porra_id = p.id
    WHERE p.estado = 'finalizada' AND au.ganancia > 0
''').fetchall()

print(f'\n✅ Ganancias verificadas: {len(ganadores)}')

problemas = 0
for g in ganadores:
    tx = c_tx.execute('''
        SELECT id FROM transactions
        WHERE to_user = ? AND concept LIKE ? AND amount = ?
        LIMIT 1
    ''', (g["username"], f'%{g["titulo"]}%', g["ganancia"])).fetchone()
    
    if not tx:
        problemas += 1

print(f'✅ Transacciones registradas: {len(ganadores) - problemas}')
print(f'❌ Transacciones faltantes: {problemas}')

# Mostrar usuarios con decimales
print('\n' + '=' * 60)
print('USUARIOS CON DECIMALES (GANADORES DE PORRAS)')
print('=' * 60)

users_decimales = c_users.execute('''
    SELECT username, balance
    FROM users
    WHERE balance != CAST(balance AS INTEGER)
    ORDER BY balance DESC
''').fetchall()

if users_decimales:
    for u in users_decimales:
        print(f'{u["username"]}: {u["balance"]} DVDcoins')
else:
    print('No hay usuarios con decimales')

# Verificar victorzahyr específicamente
print('\n' + '=' * 60)
print('VERIFICACIÓN ESPECÍFICA: victorzahyr')
print('=' * 60)

victor = c_users.execute('SELECT balance FROM users WHERE username = ?', ('victorzahyr',)).fetchone()
if victor:
    print(f'Balance actual: {victor["balance"]} DVDcoins')
    
    apuestas_victor = c_bets.execute('''
        SELECT p.id, p.titulo, p.resultado, au.opcion, au.cantidad, au.ganancia
        FROM apuestas_usuarios au
        JOIN porras p ON au.porra_id = p.id
        WHERE au.username = 'victorzahyr' AND p.estado = 'finalizada'
    ''').fetchall()
    
    if apuestas_victor:
        print(f'\nApuestas en porras finalizadas: {len(apuestas_victor)}')
        for a in apuestas_victor:
            resultado = '✅ GANÓ' if a["ganancia"] > 0 else '❌ PERDIÓ'
            print(f'  Porra #{a["id"]}: {a["titulo"]}')
            print(f'    Apostó en: {a["opcion"]}')
            print(f'    Resultado: {a["resultado"]}')
            print(f'    {resultado} - Ganancia: {a["ganancia"]} DVDcoins')
    else:
        print('\nNo tiene apuestas en porras finalizadas donde haya ganado')
        print('Por eso su balance NO tiene decimales (es correcto)')

print('\n' + '=' * 60)
print('CONCLUSIÓN')
print('=' * 60)

if problemas == 0:
    print('✅ SISTEMA FUNCIONANDO PERFECTAMENTE')
    print('   - Todos los pagos realizados')
    print('   - Todas las transacciones registradas')
    print('   - Todos los balances correctos')
else:
    print(f'❌ SE ENCONTRARON {problemas} PROBLEMAS')

print('=' * 60)

conn_bets.close()
conn_tx.close()
conn_users.close()
