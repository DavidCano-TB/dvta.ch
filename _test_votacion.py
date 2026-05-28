import httpx, asyncio

async def main():
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post('http://localhost:8000/bank/api/login', json={'username':'dvd','password':'dvd'})
        print('Login:', r.status_code)
        tok = r.json().get('token','')
        
        r2 = await c.post('http://localhost:8000/bank/api/votaciones/create',
            json={'titulo':'Test Votacion','descripcion':'desc','opciones':['Opcion A','Opcion B'],'multiple':False,'anonima':True},
            headers={'Authorization': f'Bearer {tok}'})
        print('Create:', r2.status_code, r2.text[:300])

asyncio.run(main())
