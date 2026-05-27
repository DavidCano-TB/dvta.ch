import sqlite3
import json

# Conectar a las bases de datos
db_bets = sqlite3.connect('data/apuestas.db')
db_bets.row_factory = sqlite3.Row
db_users = sqlite3.connect('data/users.db')
db_users.row_factory = sqlite3.Row
db_tx = sqlite3.connect('data/transactions.db')
db_tx.row_factory = sqlite3.Row

porra_id = 7
resultado_ganador = "no_va_a_llover"  # Los ganadores son dvdrec y victorzahyr

print(f'=== SIMULACIÓN: CERRAR Y RESOLVER PORRA {porra_id} ===\n')

# Ver estado inicial
print('--- ESTADO INICIAL ---')
porra = db_bets.execute('SELECT * FROM porras WHERE id = ?', (porra_id,)).fetchone()
print(f'Porra: {porra["titulo"]}')
print(f'Estado: {porra["estado"]}\n')

apuestas = db_bets.execute('SELECT * FROM apuestas_usuarios WHERE porra_id = ?', (porra_id,)).fetchall()
print('Apuestas:')
total_bote = 0
for a in apuestas:
    balance = db_users.execute('SELECT balance FROM users WHERE username = ?', (a['username'],)).fetchone()
    print(f'  - {a["username"]}: {a["cantidad"]} DVDc en "{a["opcion"]}" (Balance actual: {balance["balance"] if balance else 0} DVDc)')
    total_bote += a['cantidad']

print(f'\nBote total: {total_bote} DVDc')

# Calcular ganadores
ganadores = [a for a in apuestas if a['opcion'] == resultado_ganador]
total_ganadores = sum(a['cantidad'] for a in ganadores)

print(f'\n--- GANADORES (opción: "{resultado_ganador}") ---')
print(f'Total apostado por ganadores: {total_ganadores} DVDc')
print(f'Número de apuestas ganadoras: {len(ganadores)}')

if total_ganadores > 0:
    print('\nDistribución del bote:')
    for a in ganadores:
        proporcion = a['cantidad'] / total_ganadores
        ganancia = total_bote * proporcion
        print(f'  - {a["username"]}: apostó {a["cantidad"]} DVDc ({proporcion:.1%}) → recibe {ganancia:.2f} DVDc')

# Ahora ejecutar la lógica real
print('\n--- EJECUTANDO CIERRE Y RESOLUCIÓN ---')

if total_ganadores == 0:
    print('No hay ganadores, devolviendo todo el dinero')
else:
    for a in ganadores:
        proporcion = a['cantidad'] / total_ganadores
        ganancia = total_bote * proporcion
        
        # Get current balance
        current = db_users.execute('SELECT balance FROM users WHERE username = ?', (a['username'],)).fetchone()
        old_balance = current['balance'] if current else 0
        
        # Update balance
        db_users.execute('UPDATE users SET balance = balance + ? WHERE username = ?', (ganancia, a['username']))
        db_users.commit()
        
        # Get new balance
        new = db_users.execute('SELECT balance FROM users WHERE username = ?', (a['username'],)).fetchone()
        new_balance = new['balance'] if new else 0
        
        print(f'✓ {a["username"]}: {old_balance:.2f} → {new_balance:.2f} DVDc (ganancia: {ganancia:.2f})')
        
        # Record transaction
        db_tx.execute('''
            INSERT INTO transactions (from_user, to_user, amount, concept)
            VALUES (?, ?, ?, ?)
        ''', ('sistema', a['username'], ganancia, f'Ganador porra #{porra_id}'))
        db_tx.commit()
        
        # Update bet record
        db_bets.execute('''
            UPDATE apuestas_usuarios SET pagado = 1, ganancia = ?
            WHERE id = ?
        ''', (ganancia, a['id']))
        db_bets.commit()

# Update porra status
db_bets.execute('''
    UPDATE porras SET estado = 'finalizada', resultado = ?, closed_at = datetime('now'), resolved_at = datetime('now')
    WHERE id = ?
''', (resultado_ganador, porra_id))
db_bets.commit()

print('\n--- ESTADO FINAL ---')
for a in apuestas:
    balance = db_users.execute('SELECT balance FROM users WHERE username = ?', (a['username'],)).fetchone()
    apuesta_actualizada = db_bets.execute('SELECT pagado, ganancia FROM apuestas_usuarios WHERE id = ?', (a['id'],)).fetchone()
    print(f'{a["username"]}: Balance final = {balance["balance"] if balance else 0:.2f} DVDc, Pagado = {apuesta_actualizada["pagado"]}, Ganancia = {apuesta_actualizada["ganancia"]:.2f}')

# Ver transacciones creadas
print('\n--- TRANSACCIONES CREADAS ---')
txs = db_tx.execute('SELECT * FROM transactions WHERE concept LIKE ? ORDER BY id DESC LIMIT 10', (f'%porra #{porra_id}%',)).fetchall()
for tx in txs:
    print(f'{tx["from_user"]} → {tx["to_user"]}: {tx["amount"]:.2f} DVDc ({tx["concept"]})')

db_bets.close()
db_users.close()
db_tx.close()

print('\n✅ SIMULACIÓN COMPLETADA')
