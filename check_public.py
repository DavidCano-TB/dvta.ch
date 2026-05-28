import httpx, asyncio

async def check():
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as c:
        tests = [
            ("GET",  "https://dvta.ch/",                    None),
            ("GET",  "https://dvta.ch/bank",                None),
            ("POST", "https://dvta.ch/bank/api/login",      {"username":"_x","password":"_y"}),
            ("GET",  "https://dvta.ch/bank/api/me",         None),
            ("GET",  "https://dvta.ch/exams",               None),
            ("GET",  "https://dvta.ch/health",              None),
            ("GET",  "https://bank.dvta.ch/bank",           None),
            ("POST", "https://bank.dvta.ch/bank/api/login", {"username":"_x","password":"_y"}),
        ]
        all_ok = True
        for method, url, body in tests:
            try:
                r = await c.request(method, url, json=body) if body else await c.request(method, url)
                ok = r.status_code < 500
                sym = "OK  " if ok else "FAIL"
                print(f"  [{sym}] {method} {url} -> {r.status_code} ({len(r.content)} bytes)")
                if not ok:
                    all_ok = False
                    print(f"         body: {r.text[:200]}")
            except Exception as e:
                print(f"  [ERR ] {method} {url} -> {e}")
                all_ok = False
        print()
        print("RESULT:", "ALL OK" if all_ok else "SOME FAILURES")

asyncio.run(check())
