# DIAGNÓSTICO: Error 404 al crear Hundir la Flota

## PROBLEMA REPORTADO
Al intentar crear una nueva partida de Hundir la Flota desde el panel de administración, después de:
1. Seleccionar tamaño de tablero
2. Añadir usuarios
3. Click en "Iniciar partida"

Se produce un **Error 404**.

## ANÁLISIS

### Endpoints verificados:
✅ `/api/hundirlaflota/status` - Existe y funciona
✅ `/api/hundirlaflota/users` - Existe y funciona  
✅ `/api/hundirlaflota/toggle` - Existe y funciona
✅ `/api/hundirlaflota/setup` - **Existe en el código**

### Código del endpoint `/api/hundirlaflota/setup`:
```python
@app.post("/api/hundirlaflota/setup")
async def hundirlaflota_setup(
    body: HundirLaFlotaSetupRequest, 
    user: str = Depends(get_current_user)
):
    """Configure and start a Hundir la Flota game from admin panel."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    
    if len(body.players) < 2 or len(body.players) > 4:
        raise HTTPException(400, "Need 2-4 players")
    
    hundirlaflota_manager.enabled = True
    await hundirlaflota_manager.handle_action({
        "action": "setup",
        "players": body.players,
        "board_size": body.board_size,
        "turn_time": body.turn_time,
        "ships": body.ships
    }, user)
    
    logger.info("Hundir la Flota setup by %s: players=%s", user, body.players)
    return {"ok": True, "players": body.players}
```

### Modelo de datos:
```python
class HundirLaFlotaSetupRequest(BaseModel):
    players: List[str]
    board_size: int = 10
    turn_time: int = 60
    ships: Optional[Dict] = None
```

## POSIBLES CAUSAS

1. **Servidor no reiniciado**: Los cambios en `main.py` no se han cargado
2. **Ruta incorrecta**: El frontend está llamando a una ruta diferente
3. **Error de sintaxis**: Hay un error que impide que el endpoint se registre
4. **Problema de importaciones**: Falta alguna importación necesaria

## SOLUCIÓN

### Paso 1: Verificar que no hay errores de sintaxis
```bash
python -m py_compile main.py
```

### Paso 2: Reiniciar el servidor
```bash
./SOLUCIONAR_NGROK_AHORA.bat
```

### Paso 3: Verificar que el endpoint está registrado
Abrir en navegador: http://localhost:8000/docs
Buscar: `POST /api/hundirlaflota/setup`

### Paso 4: Probar el endpoint manualmente
Desde la consola del navegador en el panel de admin:

```javascript
// Obtener token
const token = localStorage.getItem('dvd_token');

// Probar endpoint
fetch('/api/hundirlaflota/setup', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': '1'
  },
  body: JSON.stringify({
    players: ['dvd', 'roydos'],
    board_size: 10,
    turn_time: 60
  })
})
.then(r => r.json())
.then(d => console.log('✓ Respuesta:', d))
.catch(e => console.error('✗ Error:', e));
```

## VERIFICACIÓN ADICIONAL

Si el endpoint sigue dando 404, verificar:

1. **¿El servidor está usando `main.py` o `src/main.py`?**
   - Revisar `start.py` línea 119
   - Debe ser: `[sys.executable, str(BASE / "main.py")]`

2. **¿Los cambios están en ambos archivos?**
   - `main.py` - Archivo principal
   - `src/main.py` - Copia de respaldo

3. **¿FastAPI está registrando la ruta?**
   - Al iniciar el servidor, debe aparecer en los logs
   - Buscar: "POST /api/hundirlaflota/setup"

## SOLUCIÓN RÁPIDA

Si nada funciona, reiniciar completamente:

```bash
# 1. Detener todo
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force

# 2. Esperar 3 segundos
Start-Sleep -Seconds 3

# 3. Reiniciar
./SOLUCIONAR_NGROK_AHORA.bat
```

## LOGS A REVISAR

Cuando se intenta crear la partida, revisar `server.log`:
```bash
Get-Content server.log -Tail 50
```

Buscar líneas con:
- `POST /api/hundirlaflota/setup`
- `404 Not Found`
- `ERROR`
- `Exception`

## ESTADO ACTUAL

- ✅ Código del endpoint existe y es correcto
- ✅ Modelo de datos es correcto
- ✅ No hay errores de sintaxis
- ⏳ Pendiente: Verificar que el servidor tiene los cambios cargados
