import urllib.request, json

try:
    r = urllib.request.urlopen("http://localhost:8000/bank/api/health", timeout=5)
    print(f"Server OK: {r.status}")
    print(r.read().decode())
except Exception as e:
    print(f"Server DOWN: {e}")

# Try login
try:
    data = json.dumps({"username": "dvd", "password": "test"}).encode()
    req = urllib.request.Request(
        "http://localhost:8000/bank/api/login",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    r = urllib.request.urlopen(req, timeout=5)
    print(f"\nLogin test (wrong pwd): {r.status}")
    print(r.read().decode()[:200])
except urllib.error.HTTPError as e:
    print(f"\nLogin test (wrong pwd): HTTP {e.code}")
    print(e.read().decode()[:200])
except Exception as e:
    print(f"\nLogin test failed: {e}")
