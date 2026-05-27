#!/usr/bin/env python3
"""Complete audit of all betting payments."""
import sqlite3

def auditoria_completa():
    print("=" * 80)
    print("AUDITORÍA COMPLETA SISTEMA DE APUESTAS")
    print("=" * 80)
    
    conn_bets = sqlite3.connect("data/apuestas.db")
    conn_bets.row_factory = sqlite3.Row
    
    conn_users = sqlite3.connect("data/users.db")
    conn_users.row_factory = sqlite3.Row
    
    conn_tx = sqlite3.connect("data/transactions.db")
    conn_tx.row_factory = sqlite3.Row
    
    # 1. Check all finalized porras
    print("\n1. PORRAS FINALIZADAS")
    print("-" * 80)
    
    porras = conn_bets.execute("""
        SELECT id, titulo, estado, resultado 
        FROM porras 
        WHERE estado = 'finalizada'
        ORDER BY id
    """).fetchall()
    
    for porra in porras:
        print(f"\nPorra #{porra['id']}: {porra['titulo']}")
        print(f"  Resultado: {porra['resultado']}")
        
        # Get all bets for this porra
        apuestas = conn_bets.execute("""
            SELECT username, opcion, cantidad, pagado, ganancia
            FROM apuestas_usuarios
            WHERE porra_id = ?
            ORDER BY username
        """, (porra['id'],)).fetchall()
        
        total_apostado = sum(a['cantidad'] for a in apuestas)
        ganadores = [a for a in apuestas if a['opcion'] == porra['resultado']]
        perdedores = [a for a in apuestas if a['opcion'] != porra['resultado']]
        
        sin_pagar = [a for a in apuestas if a['pagado'] == 0]
        
        print(f"  Total apostado: {total_apostado} DVDcoins")
        print(f"  Ganadores: {len(ganadores)} apuestas")
        print(f"  Perdedores: {len(perdedores)} apuestas")
        print(f"  Sin pagar: {len(sin_pagar)} apuestas")
        
        if sin_pagar:
            print(f"  ⚠️  PROBLEMA: Hay {len(sin_pagar)} apuestas sin marcar como pagadas")
            for a in sin_pagar:
                print(f"     - {a['username']}: {a['cantidad']} DVDcoins (opción: {a['opcion']})")
        
        # Check transactions for winners
        for ganador in ganadores:
            # Look for payment transaction
            tx = conn_tx.execute("""
                SELECT amount, concept
                FROM transactions
                WHERE to_user = ? 
                AND concept LIKE ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (ganador['username'], f"%{porra['titulo']}%")).fetchone()
            
            if not tx:
                print(f"  ❌ {ganador['username']}: Ganó {ganador['ganancia']} pero NO hay transacción")
            elif abs(tx['amount'] - ganador['ganancia']) > 0.01:
                print(f"  ⚠️  {ganador['username']}: Ganancia registrada {ganador['ganancia']} != Transacción {tx['amount']}")
    
    # 2. Check Victor's complete history
    print("\n" + "=" * 80)
    print("2. HISTORIAL COMPLETO DE @victorzahyr")
    print("-" * 80)
    
    victor_bets = conn_bets.execute("""
        SELECT au.*, p.titulo, p.estado, p.resultado
        FROM apuestas_usuarios au
        JOIN porras p ON au.porra_id = p.id
        WHERE au.username = 'victorzahyr'
        ORDER BY au.porra_id
    """).fetchall()
    
    if not victor_bets:
        print("  ℹ️  Victor no tiene apuestas registradas")
    else:
        total_apostado_victor = 0
        total_ganado_victor = 0
        
        for bet in victor_bets:
            print(f"\nPorra #{bet['porra_id']}: {bet['titulo']}")
            print(f"  Estado: {bet['estado']}")
            print(f"  Apostó: {bet['cantidad']} en opción '{bet['opcion']}'")
            
            total_apostado_victor += bet['cantidad']
            
            if bet['estado'] == 'finalizada':
                es_ganador = bet['opcion'] == bet['resultado']
                print(f"  Resultado: {bet['resultado']} - {'✅ GANÓ' if es_ganador else '❌ PERDIÓ'}")
                print(f"  Pagado: {'✅ Sí' if bet['pagado'] else '❌ No'}")
                print(f"  Ganancia: {bet['ganancia']} DVDcoins")
                
                if es_ganador:
                    total_ganado_victor += bet['ganancia']
                    
                    # Check transaction
                    tx = conn_tx.execute("""
                        SELECT amount, created_at
                        FROM transactions
                        WHERE to_user = 'victorzahyr'
                        AND concept LIKE ?
                    """, (f"%{bet['titulo']}%",)).fetchone()
                    
                    if not tx:
                        print(f"  ❌ PROBLEMA: No hay transacción de pago")
                    elif abs(tx['amount'] - bet['ganancia']) > 0.01:
                        print(f"  ⚠️  PROBLEMA: Transacción {tx['amount']} != Ganancia {bet['ganancia']}")
        
        print(f"\n{'=' * 80}")
        print(f"RESUMEN VICTOR:")
        print(f"  Total apostado: {total_apostado_victor} DVDcoins")
        print(f"  Total ganado: {total_ganado_victor} DVDcoins")
        print(f"  Balance neto: {total_ganado_victor - total_apostado_victor} DVDcoins")
        
        # Check Victor's current balance
        victor_user = conn_users.execute("""
            SELECT balance FROM users WHERE username = 'victorzahyr'
        """).fetchone()
        
        if victor_user:
            print(f"  Balance actual: {victor_user['balance']} DVDcoins")
            tiene_decimales = victor_user['balance'] != int(victor_user['balance'])
            print(f"  ¿Tiene decimales? {'✅ Sí' if tiene_decimales else '❌ No'}")
    
    # 3. Check all users with winning bets
    print("\n" + "=" * 80)
    print("3. TODOS LOS GANADORES EN PORRAS FINALIZADAS")
    print("-" * 80)
    
    ganadores_todos = conn_bets.execute("""
        SELECT au.username, au.porra_id, p.titulo, au.cantidad, au.ganancia, au.pagado
        FROM apuestas_usuarios au
        JOIN porras p ON au.porra_id = p.id
        WHERE p.estado = 'finalizada'
        AND au.opcion = p.resultado
        ORDER BY au.username, au.porra_id
    """).fetchall()
    
    usuarios_con_problemas = set()
    
    for ganador in ganadores_todos:
        # Check if there's a transaction
        tx = conn_tx.execute("""
            SELECT amount
            FROM transactions
            WHERE to_user = ?
            AND concept LIKE ?
        """, (ganador['username'], f"%{ganador['titulo']}%")).fetchone()
        
        if not tx:
            print(f"❌ {ganador['username']} - Porra #{ganador['porra_id']}: Ganó {ganador['ganancia']} pero NO hay transacción")
            usuarios_con_problemas.add(ganador['username'])
        elif ganador['pagado'] == 0:
            print(f"⚠️  {ganador['username']} - Porra #{ganador['porra_id']}: Transacción existe pero pagado=0")
            usuarios_con_problemas.add(ganador['username'])
    
    if not usuarios_con_problemas:
        print("✅ Todos los ganadores tienen sus transacciones correctas")
    
    # 4. Summary
    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    
    total_porras = len(porras)
    total_apuestas = conn_bets.execute("SELECT COUNT(*) as c FROM apuestas_usuarios").fetchone()['c']
    apuestas_sin_pagar = conn_bets.execute("""
        SELECT COUNT(*) as c FROM apuestas_usuarios au
        JOIN porras p ON au.porra_id = p.id
        WHERE p.estado = 'finalizada' AND au.pagado = 0
    """).fetchone()['c']
    
    print(f"Total porras finalizadas: {total_porras}")
    print(f"Total apuestas: {total_apuestas}")
    print(f"Apuestas sin pagar: {apuestas_sin_pagar}")
    
    if apuestas_sin_pagar > 0:
        print(f"\n❌ HAY {apuestas_sin_pagar} APUESTAS SIN PAGAR")
    else:
        print("\n✅ TODAS LAS APUESTAS ESTÁN PAGADAS")
    
    if usuarios_con_problemas:
        print(f"\n⚠️  Usuarios con problemas de pago: {', '.join(usuarios_con_problemas)}")
    
    conn_bets.close()
    conn_users.close()
    conn_tx.close()

if __name__ == "__main__":
    auditoria_completa()
