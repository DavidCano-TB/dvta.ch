"""Diagnose and fix cuentos issues"""
import urllib.request, urllib.error, json, re, os

# Get token
body = json.dumps({"username": "dvd", "password": "dvd_aGGDdCWQ5Bh3"}).encode()
req = urllib.request.Request("http://localhost:8000/bank/api/login",
    data=body, headers={"Content-Type": "application/json"}, method="POST")
r = urllib.request.urlopen(req, timeout=10)
token = json.loads(r.read())["token"]

# 1. Test cuentos list API
print("[1] GET /bank/api/cuentos:")
req = urllib.request.Request("http://localhost:8000/bank/api/cuentos",
    headers={"Authorization": f"Bearer {token}"})
try:
    r = urllib.request.urlopen(req, timeout=10)
    data = json.loads(r.read())
    print(f"  Status: 200, Items: {len(data)}")
    if data:
        print(f"  First item: {json.dumps(data[0])[:200]}")
except urllib.error.HTTPError as e:
    print(f"  HTTP {e.code}: {e.read().decode()[:200]}")

# 2. Test cuentos status
print("\n[2] GET /bank/api/cuentos/status:")
req = urllib.request.Request("http://localhost:8000/bank/api/cuentos/status",
    headers={"Authorization": f"Bearer {token}"})
try:
    r = urllib.request.urlopen(req, timeout=10)
    print(f"  {r.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"  HTTP {e.code}: {e.read().decode()[:200]}")

# 3. Check cuentos directory
cuentos_dir = os.path.join('static', 'cuentos')
if os.path.exists(cuentos_dir):
    files = os.listdir(cuentos_dir)
    print(f"\n[3] static/cuentos/ directory: {len(files)} files")
    for f in files[:10]:
        print(f"  {f}")
else:
    print(f"\n[3] static/cuentos/ NOT FOUND")

# 4. Check the cuento read endpoint
print("\n[4] GET /bank/cuento/<name> endpoint:")
# Find a cuento name from the list
req = urllib.request.Request("http://localhost:8000/bank/api/cuentos",
    headers={"Authorization": f"Bearer {token}"})
try:
    r = urllib.request.urlopen(req, timeout=10)
    items = json.loads(r.read())
    if items:
        name = items[0].get('name') or items[0].get('filename') or items[0].get('file')
        print(f"  Trying cuento: {name}")
        req2 = urllib.request.Request(
            f"http://localhost:8000/bank/cuento/{urllib.request.quote(name)}?token={token}",
            headers={"Authorization": f"Bearer {token}"})
        try:
            r2 = urllib.request.urlopen(req2, timeout=10)
            body = r2.read().decode('utf-8', errors='ignore')
            print(f"  Status: {r2.status}, Length: {len(body)}")
            print(f"  Content type: {r2.headers.get('content-type')}")
        except urllib.error.HTTPError as e:
            print(f"  HTTP {e.code}: {e.read().decode()[:200]}")
    else:
        print("  No cuentos available")
except Exception as e:
    print(f"  Error: {e}")

# 5. Check the cuentos page HTML
print("\n[5] GET /bank/cuentos page:")
req = urllib.request.Request("http://localhost:8000/bank/cuentos",
    headers={"Authorization": f"Bearer {token}", "User-Agent": "Mozilla/5.0"})
try:
    r = urllib.request.urlopen(req, timeout=10)
    body = r.read().decode('utf-8', errors='ignore')
    print(f"  Status: {r.status}, Length: {len(body)}")
    # Check API calls
    bare_api = len(re.findall(r'(?<!/bank)/api/', body))
    bank_api = len(re.findall(r'/bank/api/', body))
    print(f"  Bare /api/ calls: {bare_api}")
    print(f"  /bank/api/ calls: {bank_api}")
except urllib.error.HTTPError as e:
    print(f"  HTTP {e.code}: {e.read().decode()[:200]}")

# 6. Check through port 8001 (dvta.ch proxy)
print("\n[6] Through proxy (port 8001):")
req = urllib.request.Request("http://localhost:8001/bank/api/cuentos",
    headers={"Authorization": f"Bearer {token}"})
try:
    r = urllib.request.urlopen(req, timeout=10)
    data = json.loads(r.read())
    print(f"  Status: 200, Items: {len(data)}")
except urllib.error.HTTPError as e:
    print(f"  HTTP {e.code}: {e.read().decode()[:200]}")
except Exception as e:
    print(f"  Error: {e}")
