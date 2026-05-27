import requests

# Login as dvd
login_resp = requests.post('http://localhost:8000/api/login', json={
    'username': 'dvd',
    'password': 'dvd_aGGDdCWQ5Bh3'
})

if login_resp.status_code == 200:
    token = login_resp.json()['token']
    print(f"✅ Logged in as dvd")
    
    # Test admin stats endpoint
    print("\nTesting /api/porras/admin/stats...")
    resp = requests.get('http://localhost:8000/api/porras/admin/stats', 
                       headers={'Authorization': f'Bearer {token}'})
    
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"\n✅ SUCCESS! Admin panel data received")
        print(f"\nGlobal Summary:")
        print(f"  Total Porras: {data['resumen_global']['total_porras']}")
        print(f"  Abiertas: {data['resumen_global']['porras_abiertas']}")
        print(f"  Cerradas: {data['resumen_global']['porras_cerradas']}")
        print(f"  Finalizadas: {data['resumen_global']['porras_finalizadas']}")
        print(f"  Total Users: {data['resumen_global']['total_usuarios']}")
        print(f"  Total Bote: {data['resumen_global']['total_bote_sistema']:.1f} DVDc")
        print(f"  Total Comisión: {data['resumen_global']['total_comision_sistema']:.1f} DVDc")
        
        print(f"\nUsers with bets: {len(data['usuarios'])}")
        for u in data['usuarios'][:5]:
            print(f"  - {u['username']}: {u['total_apuestas']} bets, {u['total_apostado']:.1f} DVDc wagered")
        
        print(f"\nPorras with details: {len(data['porras'])}")
        for p in data['porras'][:3]:
            print(f"  - {p['titulo']}: {p['bote_total']:.1f} DVDc pot, {p['total_apostantes']} bettors, {p['total_apuestas']} bets")
    else:
        print(f"❌ Error: {resp.text}")
else:
    print(f"❌ Login failed: {login_resp.text}")
