#!/usr/bin/env python3
"""
Script para corregir porras pasadas:
1. Descontar dinero de apuestas que no se descontaron
2. Verificar transacciones
3. Mostrar estado actual
"""
import sqlite3
import json
from datetime import datetime

def db_bets():
    """Connect to bets database"""
    conn = sqlite3.connect("data/apuestas.db")
    conn.row_factory = sqlite3.Row
    return conn

def db_users():
    """Connect to users database"""
    conn = sqlite3.connect("data/dvdcoin.db")
    conn.row_factory = sqlite3.Row
    return conn

def db_tx():
    """Connect to transactions database"""
    conn = sqlite3.connect("data/transactions.db")
    conn.row_factory = sqlite3.Row
    return conn

def main():
    print("=" * 80)
    print("CORRECCIÓN DE PORRAS PASADAS")
    print("=" * 80)
    
    c = db_bets()
    cu = db_users()
    ct = db_tx()
    
    # 1. Get all bets
    print("\n[1] Analizando apuestas...")
    apuestas = c.execute("""
        SELECT a.id, a.porra_id, a.username, a.opcion, a.cantidad, a.pagado, a.ganancia,
               p.titulo, p.estado, p.resultado
        FROM apuestas_usuarios a
        JOIN porras p ON a.porra_id = p.id
        ORDER BY a.porra_id, a.username
    """).fetchall()
    
    print(f"   Total apuestas: {len(apuestas)}")
    
    # 2. Check which bets have corresponding debit transactions
    print("\n[2] Verificando transacciones de apuestas...")
    apuestas_sin_descuento = []
    
    for a in apuestas:
        # Check if there's a transaction for this bet
        tx = ct.execute("""
            SELECT id FROM transactions
            WHERE from_user = ? AND amount = ? AND concept LIKE ?
        """, (a["username"], a["cantidad"], f"%{a['titulo']}%")).fetchone()
        
        if not tx:
            apuestas_sin_descuento.append(a)
            print(f"   ⚠️  Apuesta sin descuento: {a['username']} apostó {a['cantidad']} en '{a['titulo']}'")
    
    print(f"\n   Apuestas sin descuento: {len(apuestas_sin_descuento)}")
    
    if apuestas_sin_descuento:
        print("\n[3] ¿Descontar dinero de estas apuestas? (s/n)")
        respuesta = input("   > ").strip().lower()
        
        if respuesta == 's':
            print("\n   Procesando...")
            for a in apuestas_sin_descuento:
                # Check user balance
                user_data = cu.execute("SELECT balance FROM users WHERE username = ?", (a["username"],)).fetchone()
                if not user_data:
                    print(f"   ❌ Usuario {a['username']} no encontrado")
                    continue
                
                # Deduct balance
                new_balance = user_data["balance"] - a["cantidad"]
                cu.execute("UPDATE users SET balance = ? WHERE username = ?", (new_balance, a["username"]))
                cu.commit()
                
                # Record transaction
                ct.execute("""
                    INSERT INTO transactions (from_user, to_user, amount, concept, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (a["username"], f"Porra: {a['titulo']}", a["cantidad"], 
                      f"Apuesta en '{a['titulo']}' - Opción: {a['opcion']} (corrección retroactiva)",
                      datetime.now().isoformat()))
                ct.commit()
                
                print(f"   ✅ Descontado: {a['username']} - {a['cantidad']} DVDc (nuevo balance: {new_balance:.1f})")
            
            print(f"\n   ✅ {len(apuestas_sin_descuento)} apuestas corregidas")
        else:
            print("\n   ⏭️  Saltando corrección")
    
    # 4. Show porras status
    print("\n[4] Estado de porras:")
    porras = c.execute("""
        SELECT id, titulo, estado, resultado,
               (SELECT COUNT(*) FROM apuestas_usuarios WHERE porra_id = porras.id) as total_apuestas,
               (SELECT SUM(cantidad) FROM apuestas_usuarios WHERE porra_id = porras.id) as bote_total
        FROM porras
        ORDER BY id
    """).fetchall()
    
    for p in porras:
        print(f"\n   Porra #{p['id']}: {p['titulo']}")
        print(f"      Estado: {p['estado']}")
        print(f"      Apuestas: {p['total_apuestas']}")
        print(f"      Bote: {p['bote_total'] or 0} DVDc")
        if p['resultado']:
            print(f"      Resultado: {p['resultado']}")
        
        # Show bets for this porra
        apuestas_porra = c.execute("""
            SELECT username, opcion, cantidad, pagado, ganancia
            FROM apuestas_usuarios
            WHERE porra_id = ?
        """, (p['id'],)).fetchall()
        
        for ap in apuestas_porra:
            status = "✅ Pagado" if ap['pagado'] else "⏳ Pendiente"
            ganancia_str = f" (ganó {ap['ganancia']:.1f})" if ap['ganancia'] else ""
            print(f"         - {ap['username']}: {ap['cantidad']} en '{ap['opcion']}' {status}{ganancia_str}")
    
    # 5. Show user balances
    print("\n[5] Balances de usuarios:")
    users = cu.execute("SELECT username, balance FROM users ORDER BY username").fetchall()
    for u in users:
        print(f"   {u['username']}: {u['balance']:.1f} DVDc")
    
    c.close()
    cu.close()
    ct.close()
    
    print("\n" + "=" * 80)
    print("ANÁLISIS COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    main()
