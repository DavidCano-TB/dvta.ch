import httpx, asyncio

async def check():
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
        tests = [
            ("GET",  "http://localhost:8001/",                    None),
            ("GET",  "http://localhost:8001/hub",                 None),
            ("GET",  "http://localhost:8001/bank",                None),
            ("POST", "http://localhost:8001/bank/api/login",      {"username":"_x","password":"_y"}),
            ("GET",  "http://localhost:8001/bank/api/me",         None),
            ("GET",  "http://localhost:8001/exams",               None),
            ("GET",  "http://localhost:8001/health",              None),
            ("GET",  "http://localhost:8000/bank",                None),
            ("POST", "http://localhost:8000/bank/api/login",      {"username":"_x","password":"_y"}),
            ("GET",  "http://localhost:8000/bank/api/me",         None),
        ]
        all_ok = True
        for method, url, body in tests:
            try:
                r = await c.request(method, url, json=body) if body else await c.request(method, url)
                ok = r.status_code < 500
                sym = "OK" if ok else "FAIL"
                short = url.replace("http://localhost:8001","[8001]").replace("http://localhost:8000","[8000]")
                print(f"  [{sym}] {method} {short} -> {r.status_code} ({len(r.content)} bytes)")
                if not ok:
                    all_ok = False
            except Exception as e:
                print(f"  [ERR] {method} {url} -> {e}")
                all_ok = False
        print()
        print("RESULT:", "ALL OK" if all_ok else "SOME FAILURES")

asyncio.run(check())
