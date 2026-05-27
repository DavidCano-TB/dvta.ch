import requests

# Login
login_resp = requests.post('http://localhost:8000/api/login', json={
    'username': 'dvd',
    'password': 'dvd_aGGDdCWQ5Bh3'
})

if login_resp.status_code != 200:
    print(f'Login failed: {login_resp.status_code}')
    exit(1)

token = login_resp.json()['token']
headers = {'Authorization': f'Bearer {token}'}

# Test mis-apuestas endpoint
print('Testing /api/porras/mis-apuestas...')
resp = requests.get('http://localhost:8000/api/porras/mis-apuestas', headers=headers)
print(f'Status: {resp.status_code}')
if resp.status_code != 200:
    print(f'Error: {resp.text}')
else:
    data = resp.json()
    print(f'Success! Found {len(data.get("apuestas", []))} bets')
    if 'resumen' in data:
        print(f'Summary: {data["resumen"]}')
