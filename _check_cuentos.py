import http.client, re

# 1. Check cuentos page
c = http.client.HTTPConnection('127.0.0.1', 8000, timeout=10)
c.request('GET', '/bank/cuentos')
r = c.getresponse()
body = r.read().decode('utf-8', 'replace')
print(f"1. /bank/cuentos: {r.status}, {len(body)} bytes")
c.close()

# Find all fetch calls
fetches = re.findall(r"fetch\(['\"]([^'\"]+)['\"]", body)
print(f"   Fetch URLs: {fetches}")

# Find all API references
apis = re.findall(r"['\"](/[^'\"]*api[^'\"]*)['\"]", body)
print(f"   API refs: {apis[:10]}")

# 2. Check cuentos status API
c = http.client.HTTPConnection('127.0.0.1', 8000, timeout=10)
c.request('GET', '/bank/api/cuentos/status')
r = c.getresponse()
print(f"\n2. /bank/api/cuentos/status: {r.status} -> {r.read().decode()}")
c.close()

# 3. Check cuentos list API
c = http.client.HTTPConnection('127.0.0.1', 8000, timeout=10)
c.request('GET', '/bank/api/cuentos/list')
r = c.getresponse()
data = r.read().decode()
print(f"\n3. /bank/api/cuentos/list: {r.status} -> {data[:200]}")
c.close()

# 4. Check if there's a /bank/cuento/ route
c = http.client.HTTPConnection('127.0.0.1', 8000, timeout=10)
c.request('GET', '/bank/api/cuentos')
r = c.getresponse()
print(f"\n4. /bank/api/cuentos: {r.status} -> {r.read().decode()[:200]}")
c.close()
