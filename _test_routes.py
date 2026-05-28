import http.client

c = http.client.HTTPConnection('127.0.0.1', 8001, timeout=10)
c.request('GET', '/apuestas')
r = c.getresponse()
loc = r.getheader('location', 'none')
print(f'/apuestas: {r.status} Location: {loc}')
c.close()

c = http.client.HTTPConnection('127.0.0.1', 8001, timeout=10)
c.request('GET', '/votaciones')
r = c.getresponse()
loc = r.getheader('location', 'none')
print(f'/votaciones: {r.status} Location: {loc}')
c.close()

# Test hub page has votaciones card
c = http.client.HTTPConnection('127.0.0.1', 8001, timeout=10)
c.request('GET', '/')
r = c.getresponse()
body = r.read().decode()
print(f'\nHub page: {r.status}, has Votaciones card: {"Votaciones" in body}')
print(f'Has Apuestas card: {"Apuestas" in body}')
c.close()
