import requests
import json

# Test local
print("=" * 60)
print("TESTING LOCAL LOGIN")
print("=" * 60)
try:
    response = requests.post(
        "http://localhost:8000/api/login",
        json={"username": "dvd", "password": "3666"},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ LOGIN EXITOSO")
        print(f"Username: {data.get('username')}")
        print(f"Admin: {data.get('is_admin')}")
        print(f"Superadmin: {data.get('is_superadmin')}")
        print(f"Token: {data.get('token')[:20]}...")
    else:
        print(f"❌ ERROR: {response.text}")
except Exception as e:
    print(f"❌ EXCEPTION: {e}")

print("\n" + "=" * 60)
print("TESTING NGROK LOGIN")
print("=" * 60)
try:
    response = requests.post(
        "https://premium-size-unreached.ngrok-free.dev/api/login",
        json={"username": "dvd", "password": "3666"},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ LOGIN EXITOSO")
        print(f"Username: {data.get('username')}")
        print(f"Admin: {data.get('is_admin')}")
        print(f"Superadmin: {data.get('is_superadmin')}")
        print(f"Token: {data.get('token')[:20]}...")
    else:
        print(f"❌ ERROR: {response.text}")
except Exception as e:
    print(f"❌ EXCEPTION: {e}")
