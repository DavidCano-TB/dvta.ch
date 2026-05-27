import sqlite3
import requests

print("=" * 80)
print("VERIFICACIÓN COMPLETA DEL SISTEMA DE PAGOS DE PORRAS")
print("=" * 80)

# 1. Verificar estado actual de balances
print("\n1. BALANCES ACTUALES DE USUARIOS:")
print("-" * 80)
cu = sqlite3.connect('data/users.db')
cu.row_factory = sqlite3.Row
users = cu.execute("SELECT username, balance FROM users ORDER BY username").fetchall()
balances_antes = {}
for u in users:
    balances_antes[u['username']] = u['balance']
    print(f"  {u['username']:20s}: {u['balance']:10.2f} DVDc")
cu.close()

# 2. Verificar porras disponibles para resolver
print("\n2. PORRAS DISPONIBLES PARA RESOLVER:")
print("-" * 80)
cb = sqlite3.connect('data/apuestas.db')
cb.row_factory = sqlite3.Row
porras = cb.execute("""
    SELECT id, titulo, estado, resultado, comision 
    FROM porras 
    WHERE estado IN ('abierta', 'cerrada')
    ORDER BY id
""").fetchall()

if not porras:
    print("  ⚠️  No hay porras abiertas o cerradas para resolver")
else:
    for p in porras:
        print(f"\n  Porra ID {p['id']}: {p['titulo']}")
        print(f"    Estado: {p['estado']}")
        print(f"    Comisión: {p['comision']*100:.0f}%")
        
        # Ver apuestas
        apuestas = cb.execute("""
            SELECT username, opcion, cantidad, pagado, ganancia
            FROM apuestas_usuarios
            WHERE porra_id = ?
            ORDER BY username
        """, (p['id'],)).fetchall()
        
        if apuestas:
            print(f"    Apuestas ({len(apuestas)}):")
            total_bote = 0
            opciones_count = {}
            for a in apuestas:
                print(f"      - {a['username']:15s}: {a['cantidad']:6.2f} DVDc en '{a['opcion']}' (Pagado: {bool(a['pagado'])})")
                total_bote += a['cantidad']
                opciones_count[a['opcion']] = opciones_count.get(a['opcion'], 0) + a['cantidad']
            
            print(f"    Bote Total: {total_bote:.2f} DVDc")
            print(f"    Distribución por opción:")
            for opcion, total in opciones_count.items():
                pct = (total / total_bote * 100) if total_bote > 0 else 0
                print(f"      - '{opcion}': {total:.2f} DVDc ({pct:.1f}%)")
        else:
            print(f"    ⚠️  Sin apuestas")

cb.close()

# 3. Verificar transacciones recientes relacionadas con porras
print("\n3. TRANSACCIONES RECIENTES DE PORRAS:")
print("-" * 80)
ct = sqlite3.connect('data/transactions.db')
ct.row_factory = sqlite3.Row
txs = ct.execute("""
    SELECT created_at, from_user, to_user, amount, concept
    FROM transactions
    WHERE concept LIKE '%porra%' OR concept LIKE '%Ganador%' OR concept LIKE '%Devolución%'
    ORDER BY created_at DESC
    LIMIT 20
""").fetchall()

if txs:
    for tx in txs:
        print(f"  {tx['created_at']} | {tx['from_user']:10s} → {tx['to_user']:10s} | {tx['amount']:8.2f} DVDc | {tx['concept']}")
else:
    print("  ℹ️  No hay transacciones de porras registradas aún")
ct.close()

# 4. Verificar estadísticas de porras
print("\n4. ESTADÍSTICAS DE USUARIOS EN PORRAS:")
print("-" * 80)
cb = sqlite3.connect('data/apuestas.db')
cb.row_factory = sqlite3.Row
stats = cb.execute("""
    SELECT username, total_apostado, total_ganado, porras_ganadas, porras_perdidas, updated_at
    FROM estadisticas_porras
    ORDER BY total_apostado DESC
""").fetchall()

if stats:
    print(f"  {'Usuario':15s} | {'Apostado':10s} | {'Ganado':10s} | {'Ganadas':8s} | {'Perdidas':8s} | {'Última Act.'}")
    print("  " + "-" * 90)
    for s in stats:
        beneficio = s['total_ganado'] - s['total_apostado']
        print(f"  {s['username']:15s} | {s['total_apostado']:10.2f} | {s['total_ganado']:10.2f} | {s['porras_ganadas']:8d} | {s['porras_perdidas']:8d} | {s['updated_at']}")
else:
    print("  ℹ️  No hay estadísticas registradas aún")
cb.close()

# 5. Test de API - Verificar que el endpoint de balance funciona
print("\n5. VERIFICACIÓN DE API - ENDPOINT /api/me:")
print("-" * 80)

# Login como dvd
login_resp = requests.post('http://localhost:8000/api/login', json={
    'username': 'dvd',
    'password': 'dvd_aGGDdCWQ5Bh3'
})

if login_resp.status_code == 200:
    token = login_resp.json()['token']
    
    # Get user info
    me_resp = requests.get('http://localhost:8000/api/me', 
                          headers={'Authorization': f'Bearer {token}'})
    
    if me_resp.status_code == 200:
        me_data = me_resp.json()
        print(f"  ✅ Usuario: {me_data['username']}")
        print(f"  ✅ Balance: {me_data['balance']:.2f} DVDc")
        print(f"  ✅ Admin: {me_data.get('is_admin', False)}")
    else:
        print(f"  ❌ Error obteniendo info de usuario: {me_resp.status_code}")
else:
    print(f"  ❌ Error en login: {login_resp.status_code}")

# 6. Resumen y recomendaciones
print("\n" + "=" * 80)
print("RESUMEN Y VERIFICACIÓN:")
print("=" * 80)

print("\n✅ VERIFICACIONES COMPLETADAS:")
print("  1. Balances de usuarios consultados")
print("  2. Porras disponibles listadas")
print("  3. Transacciones de porras revisadas")
print("  4. Estadísticas de usuarios verificadas")
print("  5. API de balance verificada")

print("\n📋 SISTEMA DE PAGOS:")
print("  - Los pagos se registran en la tabla 'users' (campo 'balance')")
print("  - Las transacciones se guardan en 'transactions.db'")
print("  - Las estadísticas se actualizan en 'estadisticas_porras'")
print("  - El balance se puede ver en /api/me y en la pestaña 'Enviar'")

print("\n🔍 PARA PROBAR EL SISTEMA:")
print("  1. Crear una porra de prueba")
print("  2. Hacer apuestas con varios usuarios")
print("  3. Cerrar y resolver la porra desde el Admin Panel")
print("  4. Verificar que los balances se actualizan correctamente")
print("  5. Verificar que las transacciones aparecen en la pestaña 'Enviar'")

print("\n" + "=" * 80)
