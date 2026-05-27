import sqlite3

conn_apuestas = sqlite3.connect('data/apuestas.db')
cursor_apuestas = conn_apuestas.cursor()

conn_users = sqlite3.connect('data/users.db')
cursor_users = conn_users.cursor()

print('=== RECUPERANDO PORRA 7 ===\n')

# Get all bets for porra 7
cursor_apuestas.execute('SELECT username, opcion, cantidad, pagado, ganancia FROM apuestas_usuarios WHERE porra_id=7')
apuestas = cursor_apuestas.fetchall()

print(f'Apuestas encontradas: {len(apuestas)}')
total_devuelto = 0
for username, opcion, cantidad, pagado, ganancia in apuestas:
    print(f'  {username}: {opcion} - {cantidad} DVDcoins (pagado={pagado}, ganancia={ganancia})')
    
    # If user was paid, subtract the winnings they received
    if pagado == 1 and ganancia > 0:
        cursor_users.execute('SELECT balance FROM users WHERE username=?', (username,))
        user_row = cursor_users.fetchone()
        if user_row:
            current_balance = user_row[0]
            # Remove the winnings they got
            new_balance = current_balance - ganancia
            cursor_users.execute('UPDATE users SET balance=? WHERE username=?', (new_balance, username))
            print(f'    Retirando ganancia: {current_balance} -> {new_balance} (-{ganancia})')
            total_devuelto -= ganancia

# Reset all bets to unpaid
cursor_apuestas.execute('UPDATE apuestas_usuarios SET pagado=0, ganancia=0.0 WHERE porra_id=7')

# Clear porra result and set to abierta
cursor_apuestas.execute('''
    UPDATE porras 
    SET estado = 'abierta',
        resultado = NULL,
        closed_at = NULL,
        resolved_at = NULL
    WHERE id = 7
''')

conn_apuestas.commit()
conn_users.commit()

print(f'\n✓ Ganancias retiradas (total: {abs(total_devuelto)} DVDcoins)')
print('✓ Todas las apuestas marcadas como no pagadas')
print('✓ Porra 7 actualizada a estado "abierta"')
print('✓ Resultado eliminado')
print('✓ Fechas de cierre eliminadas')

# Verify
cursor_apuestas.execute('SELECT id, titulo, estado, resultado FROM porras WHERE id=7')
final = cursor_apuestas.fetchone()
print(f'\nEstado final: ID={final[0]}, Estado={final[2]}, Resultado={final[3]}')

conn_apuestas.close()
conn_users.close()

print('\n✓✓✓ PORRA 7 RECUPERADA Y ACTIVA ✓✓✓')
