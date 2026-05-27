# ✅ Sistema de Admin para Porras - IMPLEMENTADO

## 📋 RESUMEN DE CAMBIOS

Se ha implementado un sistema que permite a los **admins del DVDBank** cerrar y resolver porras usando el código de admin **"12345"**.

## 🎯 FUNCIONALIDAD IMPLEMENTADA

### Quién puede hacer qué:

#### 🔴 **DVD (SUPERADMIN)**
- ✅ Cerrar porras manualmente
- ✅ Resolver porras (elegir ganador)
- ✅ Cerrar y resolver en un solo paso
- ✅ Cancelar porras
- ✅ Relanzar porras
- ✅ Enmascarar/mostrar porras
- ✅ Borrar porras
- ✅ Ver todas las estadísticas

#### 🟡 **ADMINS DEL DVDBANK** (nebulosa, nina, victor, yu, roy, admin, aitor)
- ✅ **Cerrar y resolver porras con código "12345"**
- ✅ Ver porcentaje del bote por opción
- ❌ No pueden cancelar, relanzar, enmascarar o borrar porras

#### 🟢 **USUARIOS NORMALES**
- ✅ Apostar en porras abiertas
- ✅ Ver sus propias apuestas
- ✅ Ver solo el porcentaje del bote (no detalles)

## 🔧 CAMBIOS TÉCNICOS

### Backend (`main.py`)

#### 1. Nuevo Modelo de Request
```python
class CerrarYResolverAdminRequest(BaseModel):
    resultado: str  # valor de la opción ganadora
    admin_password: str  # código de admin (12345)
```

#### 2. Nuevo Endpoint
```python
@app.post("/api/porras/cerrar-y-resolver-admin/{porra_id}")
async def porra_cerrar_y_resolver_admin(porra_id: int, body: CerrarYResolverAdminRequest, user: str = Depends(get_current_user)):
```

**Características:**
- ✅ Verifica que el usuario sea admin del DVDBank
- ✅ Verifica que la contraseña sea "12345"
- ✅ Cierra la porra automáticamente
- ✅ Reparte el bote proporcionalmente entre ganadores
- ✅ Registra transacciones con nota de quién resolvió
- ✅ Actualiza estadísticas de usuarios
- ✅ Envía notificaciones a ganadores
- ✅ Logs detallados de toda la operación

### Frontend (`game_pages/apuestas/apuestas.html`)

#### 1. Detección de Admins
```javascript
const isDvd = me && me.username === 'dvd';
const isAdmin = me && me.is_admin; // Admin del DVDBank
```

#### 2. Botones de Admin
- **DVD**: Ve todos los botones (Cerrar, Resolver, Cancelar, Relanzar, Enmascarar, Borrar)
- **Admins**: Solo ven botón "🔐 Cerrar y Resolver (Admin)"

#### 3. Nueva Función JavaScript
```javascript
async function cerrarYResolverAdmin(porraId)
```

**Flujo:**
1. Pide código de admin (12345)
2. Muestra lista de opciones
3. Admin selecciona opción ganadora
4. Confirma la acción
5. Envía request al backend
6. Muestra resultado con detalles

## 🎮 CÓMO USAR (Para Admins)

### Paso a Paso:

1. **Iniciar sesión** como admin del DVDBank (nebulosa, nina, victor, yu, roy, admin, aitor)

2. **Ir a la página de Apuestas** (`/apuestas`)

3. **Buscar la porra** que quieres cerrar y resolver

4. **Hacer clic** en el botón **"🔐 Cerrar y Resolver (Admin)"**

5. **Introducir código de admin**: `12345`

6. **Seleccionar opción ganadora**: Introducir el número de la opción (1, 2, 3, etc.)

7. **Confirmar**: Revisar y confirmar la acción

8. **¡Listo!** El sistema:
   - Cierra la porra
   - Calcula el reparto proporcional
   - Acredita las ganancias a los ganadores
   - Registra todas las transacciones
   - Actualiza estadísticas

## 💰 REPARTO DEL BOTE

### Cómo funciona:

El bote se reparte **proporcionalmente** según la cantidad apostada por cada ganador:

```
Proporción = Cantidad apostada por usuario / Total apostado por todos los ganadores
Ganancia = Bote total × Proporción
```

### Ejemplo:

**Porra:** "¿Quién ganará el partido?"
- **Bote total:** 1000 DVDc
- **Opción ganadora:** "Equipo A"

**Apuestas en "Equipo A":**
- Usuario1: 100 DVDc
- Usuario2: 200 DVDc
- Usuario3: 200 DVDc
- **Total ganadores:** 500 DVDc

**Reparto:**
- Usuario1: 1000 × (100/500) = **200 DVDc** (ganó 100 DVDc)
- Usuario2: 1000 × (200/500) = **400 DVDc** (ganó 200 DVDc)
- Usuario3: 1000 × (200/500) = **400 DVDc** (ganó 200 DVDc)

## 🔒 SEGURIDAD

### Verificaciones implementadas:

1. ✅ **Autenticación JWT**: Usuario debe estar autenticado
2. ✅ **Verificación de rol**: Usuario debe ser admin del DVDBank
3. ✅ **Contraseña de admin**: Debe introducir "12345" correctamente
4. ✅ **Estado de porra**: No se puede resolver una porra ya finalizada
5. ✅ **Confirmación**: Doble confirmación antes de ejecutar
6. ✅ **Logs**: Todas las acciones quedan registradas con el nombre del admin

### Mensajes de error:

- `"Solo admins del DVDBank pueden usar esta función"` - Usuario no es admin
- `"Contraseña de admin incorrecta"` - Código incorrecto
- `"Porra no encontrada"` - ID inválido
- `"Esta porra ya fue resuelta"` - Porra ya finalizada
- `"No hay apuestas en esta porra"` - Porra sin apuestas

## 📊 LOGS Y TRAZABILIDAD

Cada resolución por admin genera logs detallados:

```
[ADMIN-CERRAR-RESOLVER] Admin nebulosa cerrando porra 7: Bote total=1000, Ganadores=3, Total apostado por ganadores=500
[ADMIN-CERRAR-RESOLVER] Distribuyendo bote de 1000.00 DVDc entre 3 apuestas ganadoras
[ADMIN-CERRAR-RESOLVER] Procesando ganador usuario1: apostó 100.00, proporción 20.00%, ganancia 200.00
[ADMIN-CERRAR-RESOLVER] Balance de usuario1: 500.00 → 700.00 (diferencia: 200.00)
[ADMIN-CERRAR-RESOLVER] Transacción registrada: sistema → usuario1: 200.00 DVDc
[ADMIN-CERRAR-RESOLVER] Admin nebulosa cerró y resolvió porra 7. Ganadores: 3, Bote: 1000.00 DVDc
```

## 🎯 TRANSACCIONES

Cada ganancia genera una transacción en el banco:

```sql
INSERT INTO transactions (from_user, to_user, amount, concept)
VALUES ('sistema', 'usuario1', 200.0, 'Ganador porra #7 (resuelto por admin nebulosa)')
```

Esto permite:
- ✅ Auditoría completa
- ✅ Historial de transacciones
- ✅ Saber quién resolvió cada porra
- ✅ Rastrear todas las ganancias

## ✅ TESTING

### Para probar el sistema:

1. **Crear una porra de prueba** (como DVD)
2. **Hacer apuestas** con varios usuarios
3. **Iniciar sesión como admin** (ej: nebulosa)
4. **Cerrar y resolver** con código "12345"
5. **Verificar**:
   - ✅ Balances actualizados correctamente
   - ✅ Transacciones registradas
   - ✅ Estadísticas actualizadas
   - ✅ Notificaciones enviadas

## 📝 NOTAS IMPORTANTES

1. **Código "12345" es fijo** - No se puede cambiar desde la interfaz
2. **Acción irreversible** - Una vez resuelta, no se puede deshacer
3. **Solo admins del DVDBank** - Lista definida en `ADMINS` en `main.py`
4. **Reparto automático** - No requiere intervención manual
5. **100% del bote** - Todo el dinero va a los ganadores (sin comisión)

## 🔄 FLUJO COMPLETO

```
1. Usuario crea porra → Estado: "abierta"
2. Usuarios apuestan → Dinero se descuenta de sus balances
3. Llega fecha límite → Estado: "cerrada" (automático al intentar apostar)
   O Admin/DVD cierra manualmente
4. Admin introduce código "12345" y elige ganador
5. Sistema calcula reparto proporcional
6. Sistema acredita ganancias a ganadores
7. Sistema registra transacciones
8. Sistema actualiza estadísticas
9. Sistema envía notificaciones
10. Estado: "finalizada"
```

## 🎉 RESULTADO

Ahora los admins del DVDBank pueden:
- ✅ Cerrar porras cuando sea necesario
- ✅ Elegir la opción ganadora
- ✅ Repartir el bote automáticamente
- ✅ Todo con un simple código "12345"

¡Sistema completamente funcional y seguro! 🚀
