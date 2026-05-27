import requests

# Login as DVD
login_resp = requests.post('http://localhost:8000/api/login', json={
    'username': 'dvd',
    'password': 'dvd_aGGDdCWQ5Bh3'
})

if login_resp.status_code != 200:
    print(f'Login failed: {login_resp.status_code}')
    exit(1)

token = login_resp.json()['token']
headers = {'Authorization': f'Bearer {token}'}

# Get porras list
list_resp = requests.get('http://localhost:8000/api/porras/list', headers=headers)
data = list_resp.json()

print(f'Total porras: {len(data.get("porras", []))}')

# Find porra 7
porras = data.get('porras', [])
p7 = [p for p in porras if p['id'] == 7]

if p7:
    print(f'\n✓ PORRA 7 ENCONTRADA:')
    print(f'  ID: {p7[0]["id"]}')
    print(f'  Título: {p7[0]["titulo"]}')
    print(f'  Estado: {p7[0]["estado"]}')
    print(f'  Tipo: {p7[0]["tipo"]}')
    print(f'  Visible: SÍ')
else:
    print('\n✗ PORRA 7 NO ENCONTRADA EN LA LISTA')

# Get porra 7 details
detail_resp = requests.get('http://localhost:8000/api/porras/7', headers=headers)
if detail_resp.status_code == 200:
    detail = detail_resp.json()
    print(f'\n✓ DETALLES PORRA 7:')
    print(f'  Estado: {detail.get("estado")}')
    print(f'  Resultado: {detail.get("resultado")}')
    print(f'  Opciones: {len(detail.get("opciones", []))}')
else:
    print(f'\n✗ Error obteniendo detalles: {detail_resp.status_code}')
