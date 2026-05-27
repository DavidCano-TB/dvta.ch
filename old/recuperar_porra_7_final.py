import sqlite3

conn = sqlite3.connect('data/apuestas.db')
cursor = conn.cursor()

# Check current state
cursor.execute('SELECT id, titulo, estado, tipo FROM porras WHERE id=7')
row = cursor.fetchone()
print(f'Estado actual Porra 7: {row}')

cursor.execute('SELECT usuario, opcion, cantidad FROM apuestas WHERE porra_id=7')
apuestas = cursor.fetchall()
print(f'\nApuestas totales: {len(apuestas)}')
for a in apuestas:
    print(f'  {a[0]}: {a[1]} - {a[2]} DVDcoins')

# Calculate total bote from bets
bote_total = sum([a[2] for a in apuestas])
print(f'\nBote calculado: {bote_total} DVDcoins')

# Check if there were winners (estado = finalizada)
if row and row[2] == 'finalizada':
    print(f'\nPorra estaba finalizada. Devolviendo dinero a los usuarios...')
    
    # Get users database
    conn_users = sqlite3.connect('data/users.db')
    cursor_users = conn_users.cursor()
    
    # Return money to each user who bet
    for usuario, opcion, cantidad in apuestas:
        cursor_users.execute('SELECT balance FROM users WHERE username=?', (usuario,))
        user_row = cursor_users.fetchone()
        if user_row:
            current_balance = user_row[0]
            new_balance = current_balance + cantidad
            cursor_users.execute('UPDATE users SET balance=? WHERE username=?', (new_balance, usuario))
            print(f'  {usuario}: {current_balance} -> {new_balance} (+{cantidad})')
    
    conn_users.commit()
    conn_users.close()
    print('Dinero devuelto a todos los usuarios')

# Update porra to "abierta" state
cursor.execute('''
    UPDATE porras 
    SET estado = 'abierta',
        opcion_ganadora = NULL,
        fecha_cierre = NULL
    WHERE id = 7
''')

conn.commit()
print('\n✓ Porra 7 actualizada a estado "abierta"')
print('✓ Opción ganadora eliminada')
print('✓ Fecha de cierre eliminada')

# Verify final state
cursor.execute('SELECT id, titulo, estado, opcion_ganadora FROM porras WHERE id=7')
final_row = cursor.fetchone()
print(f'\nEstado final: {final_row}')

conn.close()
print('\n✓ Porra 7 recuperada y activa')
