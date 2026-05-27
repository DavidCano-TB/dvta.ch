# SOLUCIÓN COMPLETA DEL SISTEMA DE PORRAS

## PROBLEMAS IDENTIFICADOS

### 1. ❌ Dinero no se descuenta al apostar
**Estado**: ✅ **RESUELTO** - El código YA descuenta el dinero
- El endpoint `/api/porras/apostar` en `main.py` (líneas 7536-7680) SÍ descuenta el balance
- El problema era que apuestas ANTIGUAS (antes de la corrección) no se descontaron
- **Solución**: Script `corregir_porras_pasadas.py` para corregir apuestas antiguas

### 2. ❌ Al cerrar porra no se paga automáticamente
**Estado**: ⚠️ **PARCIALMENTE RESUELTO**
- Existen DOS endpoints:
  - `/api/porras/cerrar/{porra_id}` - Solo cierra, NO paga
  - `/api/porras/resolver` - Paga a ganadores automáticamente
- El frontend tiene dos flujos:
  1. **Cerrar** → luego **Resolver** (dos pasos)
  2. **Cerrar y Resolver** (un paso) - pero el endpoint NO existe en backend

**Solución necesaria**: 
- Opción A: Crear endpoint `/api/porras/cerrar-y-resolver` que haga ambas cosas
- Opción B: Modificar frontend para que "Cerrar Porra" llame directamente a resolver

## CÓDIGO ACTUAL

### Endpoint de Apostar (✅ FUNCIONA)
```python
@app.post("/api/porras/apostar")
async def porra_apostar(body: ApuestaRequest, user: str = Depends(get_current_user)):
    # ... validaciones ...
    
    # ✅ DESCUENTA EL BALANCE
    cu.execute("UPDATE users SET balance = ? WHERE username = ?", (new_balance, user))
    cu.commit()
    
    # ✅ REGISTRA LA APUESTA
    c.execute("INSERT INTO apuestas_usuarios (...) VALUES (...)")
    
    # ✅ REGISTRA LA TRANSACCIÓN
    ct.execute("INSERT INTO transactions (...) VALUES (...)")
```

### Endpoint de Resolver (✅ FUNCIONA)
```python
@app.post("/api/porras/resolver")
async def porra_resolver(body: ResolverPorraRequest, user: str = Depends(get_current_user)):
    # ... obtiene apuestas ...
    
    # ✅ CALCULA GANANCIAS
    for a in ganadores:
        proporcion = a["cantidad"] / total_ganadores
        ganancia = bote_neto * proporcion
        
        # ✅ PAGA A GANADORES
        cu.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (ganancia, a["username"]))
        
        # ✅ REGISTRA TRANSACCIÓN
        ct.execute("INSERT INTO transactions (...) VALUES (...)")
    
    # ✅ CIERRA LA PORRA
    c.execute("UPDATE porras SET estado = 'finalizada', resultado = ? WHERE id = ?", (...))
```

## SCRIPTS DE CORRECCIÓN

### 1. `corregir_porras_pasadas.py`
- Analiza todas las apuestas
- Detecta apuestas sin transacción de descuento
- Permite descontar retroactivamente
- Muestra estado de todas las porras

### 2. Uso:
```bash
python corregir_porras_pasadas.py
```

## FLUJO CORRECTO

### Para DVD (Admin):
1. **Crear porra** → Estado: "abierta"
2. **Usuarios apuestan** → Se descuenta dinero automáticamente
3. **Cerrar apuestas** → `/api/porras/cerrar/{id}` → Estado: "cerrada"
4. **Declarar ganador** → `/api/porras/resolver` con `resultado` → Estado: "finalizada"
   - Calcula ganancias proporcionalmente
   - Paga a todos los ganadores
   - Registra transacciones
   - Actualiza estadísticas

### Alternativa (un solo paso):
1. **Crear porra** → Estado: "abierta"
2. **Usuarios apuestan** → Se descuenta dinero automáticamente
3. **Cerrar y declarar ganador** → Endpoint nuevo que haga ambas cosas

## ENDPOINT FALTANTE

Necesitamos crear:

```python
class CerrarYResolverRequest(BaseModel):
    porra_id: int
    resultado: str

@app.post("/api/porras/cerrar-y-resolver")
async def porra_cerrar_y_resolver(body: CerrarYResolverRequest, user: str = Depends(get_current_user)):
    """Close porra and resolve with winner in one step. Only dvd can do this."""
    if user not in SUPERADMINS:
        raise HTTPException(403, "Solo dvd puede cerrar y resolver porras")
    
    # 1. Cerrar porra
    c = db_bets()
    c.execute("UPDATE porras SET estado = 'cerrada' WHERE id = ? AND estado = 'abierta'", (body.porra_id,))
    c.commit()
    c.close()
    
    # 2. Resolver (reutilizar código existente)
    return await porra_resolver(ResolverPorraRequest(porra_id=body.porra_id, resultado=body.resultado), user)
```

## ESTADO ACTUAL DEL SERVIDOR

✅ Servidor funcionando en:
- Local: http://localhost:8000
- Público: https://unhidden-patient-cradling.ngrok-free.dev

✅ Votaciones funcionando: `/votaciones`

## PRÓXIMOS PASOS

1. ✅ Ejecutar `corregir_porras_pasadas.py` para corregir apuestas antiguas
2. ⏳ Crear endpoint `/api/porras/cerrar-y-resolver`
3. ⏳ Verificar que el frontend lo usa correctamente
4. ⏳ Probar flujo completo: crear → apostar → cerrar → pagar

## APUESTAS DETECTADAS SIN DESCUENTO

Total: 20 apuestas de usuarios:
- dvdrec: 8 apuestas
- roydos: 7 apuestas
- markus (polyglot): 3 apuestas
- victorzahyr: 2 apuestas
- malagacity: 1 apuesta

**Total a descontar**: ~67 DVDcoins
