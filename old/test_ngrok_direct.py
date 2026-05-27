import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=" * 60)
print("TEST NGROK CON DIFERENTES METODOS")
print("=" * 60)

# Method 1: Normal request
print("\n[1] Request normal:")
try:
    response = requests.post(
        "https://premium-size-unreached.ngrok-free.dev/api/login",
        json={"username": "dvd", "password": "3666"},
        timeout=15
    )
    print(f"✅ Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ LOGIN EXITOSO: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Method 2: Without SSL verification
print("\n[2] Request sin verificar SSL:")
try:
    response = requests.post(
        "https://premium-size-unreached.ngrok-free.dev/api/login",
        json={"username": "dvd", "password": "3666"},
        verify=False,
        timeout=15
    )
    print(f"✅ Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ LOGIN EXITOSO: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Method 3: With custom headers
print("\n[3] Request con headers personalizados:")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/json'
    }
    response = requests.post(
        "https://premium-size-unreached.ngrok-free.dev/api/login",
        json={"username": "dvd", "password": "3666"},
        headers=headers,
        verify=False,
        timeout=15
    )
    print(f"✅ Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ LOGIN EXITOSO: {response.json()}")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")

# Method 4: Test homepage first
print("\n[4] Test homepage primero:")
try:
    response = requests.get(
        "https://premium-size-unreached.ngrok-free.dev/",
        verify=False,
        timeout=15
    )
    print(f"✅ Homepage Status: {response.status_code}")
    print(f"Content length: {len(response.text)} bytes")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
