# 🔍 INSTRUCCIONES DE VERIFICACIÓN - SISTEMA DE APUESTAS

## ✅ Cómo Verificar que Todo Funciona Correctamente

---

## 📋 VERIFICACIÓN 1: Sistema de Reparto Sin Comisiones

### 🎯 Objetivo
Verificar que el bote se reparte 100% entre acertantes, proporcional a lo apostado.

### 📝 Pasos para Verificar:

#### 1. Crear una Porra de Prueba
```
Título: "Prueba Reparto"
Opciones: "Sí" y "No"
Deadline: Fecha futura
```

#### 2. Realizar Apuestas
```
Usuario A: 10 DVDc a "Sí"
Usuario B: 30 DVDc a "Sí"
Usuario C: 20 DVDc a "No"
Usuario D: 40 DVDc a "No"

Bote Total: 100 DVDc
```

#### 3. Cerrar y Resolver la Porra
```
Opción Ganadora: "Sí"
```

#### 4. Verificar Ganancias
```
Total apostado a "Sí": 40 DVDc

Usuario A debería recibir: 100 × (10/40) = 25 DVDc
Usuario B debería recibir: 100 × (30/40) = 75 DVDc

Total repartido: 100 DVDc ✅
```

#### 5. Verificar en la Base de Datos
```sql
-- Abrir apuestas.db
SELECT username, opcion, cantidad, ganancia 
FROM apuestas_usuarios 
WHERE porra_id = [ID_PORRA_PRUEBA];
```

**Resultado Esperado:**
```
Usuario A | Sí | 10 | 25.0
Usuario B | Sí | 30 | 75.0
Usuario C | No | 20 | 0.0
Usuario D | No | 40 | 0.0
```

### ✅ Checklist de Verificación:
- [ ] Bote total = Suma de todas las apuestas
- [ ] Ganancia Usuario A = 25 DVDc
- [ ] Ganancia Usuario B = 75 DVDc
- [ ] Ganancia Usuario C = 0 DVDc
- [ ] Ganancia Usuario D = 0 DVDc
- [ ] Total repartido = 100 DVDc (100% del bote)
- [ ] Sin comisiones deducidas

---

## 📋 VERIFICACIÓN 2: Validación de Deadline

### 🎯 Objetivo
Verificar que no se puede apostar después de la deadline.

### 📝 Pasos para Verificar:

#### 1. Crear una Porra con Deadline Pasada
```
Título: "Prueba Deadline"
Deadline: Fecha pasada (ej: 01/05/2026 10:00)
Estado: abierta
```

#### 2. Abrir la Página de la Porra
```
URL: /apuestas/porras/porra_X.html?token=[TU_TOKEN]
```

#### 3. Verificar Frontend
**Resultado Esperado:**
```
✅ Debe mostrar: "⏰ Ya no se puede apostar más"
✅ Debe incluir: "La fecha límite (01/05/2026 10:00) ha pasado."
✅ Panel de apuestas debe estar oculto o mostrar mensaje
✅ No debe permitir seleccionar opciones
```

#### 4. Intentar Apostar (Bypass Frontend)
```bash
# Usar curl o Postman para intentar apostar
curl -X POST http://localhost:8000/api/porras/apostar \
  -H "Authorization: Bearer [TU_TOKEN]" \
  -H "Content-Type: application/json" \
  -d '{
    "porra_id": [ID_PORRA],
    "opcion": "si",
    "cantidad": 10
  }'
```

**Resultado Esperado:**
```json
{
  "detail": "La fecha límite ha pasado (01/05/2026 10:00). Porra cerrada automáticamente."
}
```

#### 5. Verificar Estado de la Porra
```sql
-- Abrir apuestas.db
SELECT id, titulo, estado, fecha_limite, closed_at 
FROM porras 
WHERE id = [ID_PORRA];
```

**Resultado Esperado:**
```
Estado: cerrada
closed_at: [FECHA_ACTUAL]
```

### ✅ Checklist de Verificación:
- [ ] Frontend muestra "Ya no se puede apostar más"
- [ ] Frontend incluye fecha límite formateada
- [ ] Panel de apuestas está oculto
- [ ] Backend rechaza apuesta con HTTP 400
- [ ] Backend cierra automáticamente la porra
- [ ] Mensaje de error es claro
- [ ] Estado de la porra cambia a "cerrada"

---

## 📋 VERIFICACIÓN 3: Todas las Porras Actualizadas

### 🎯 Objetivo
Verificar que las 10 porras tienen la validación de deadline.

### 📝 Pasos para Verificar:

#### 1. Buscar el Código de Validación
```bash
# Buscar en todas las porras
grep -r "Ya no se puede apostar más" game_pages/apuestas/porras/
```

**Resultado Esperado:**
```
porra_2.html: Ya no se puede apostar más
porra_3.html: Ya no se puede apostar más
porra_7.html: Ya no se puede apostar más
porra_8.html: Ya no se puede apostar más
porra_9.html: Ya no se puede apostar más
porra_11.html: Ya no se puede apostar más
porra_12.html: Ya no se puede apostar más
porra_13.html: Ya no se puede apostar más
porra_14.html: Ya no se puede apostar más
porra_15.html: Ya no se puede apostar más
```

#### 2. Verificar Cada Porra Manualmente
```
1. Abrir porra_2.html
2. Buscar: "Ya no se puede apostar más"
3. Verificar que existe el código de validación
4. Repetir para todas las porras
```

### ✅ Checklist de Verificación:
- [ ] porra_2.html tiene validación
- [ ] porra_3.html tiene validación
- [ ] porra_7.html tiene validación
- [ ] porra_8.html tiene validación
- [ ] porra_9.html tiene validación
- [ ] porra_11.html tiene validación
- [ ] porra_12.html tiene validación
- [ ] porra_13.html tiene validación
- [ ] porra_14.html tiene validación
- [ ] porra_15.html tiene validación

---

## 📋 VERIFICACIÓN 4: Casos de Prueba Completos

### 🎯 Objetivo
Verificar todos los casos de uso del sistema.

### 📝 Casos de Prueba:

#### Caso 1: Apuesta Normal (Deadline NO pasada)
```
1. Crear porra con deadline futura
2. Realizar apuesta
3. Verificar que se acepta
4. Verificar que se descuenta el saldo
5. Verificar que se registra en la BD
```

**Resultado Esperado:** ✅ Apuesta aceptada

#### Caso 2: Apuesta con Deadline Pasada (Frontend)
```
1. Crear porra con deadline pasada
2. Abrir página de la porra
3. Verificar mensaje "Ya no se puede apostar más"
4. Verificar que no se puede apostar
```

**Resultado Esperado:** ❌ Apuesta bloqueada en frontend

#### Caso 3: Apuesta con Deadline Pasada (Backend)
```
1. Crear porra con deadline pasada
2. Intentar apostar con API directamente
3. Verificar que se rechaza con HTTP 400
4. Verificar que la porra se cierra automáticamente
```

**Resultado Esperado:** ❌ Apuesta rechazada en backend

#### Caso 4: Reparto de Bote
```
1. Crear porra con 2 opciones
2. Realizar múltiples apuestas
3. Cerrar y resolver la porra
4. Verificar que el reparto es correcto
5. Verificar que no hay comisiones
```

**Resultado Esperado:** ✅ Reparto 100% proporcional

#### Caso 5: Múltiples Apuestas del Mismo Usuario
```
1. Crear porra
2. Usuario apuesta 10 DVDc a "Sí"
3. Usuario apuesta 20 DVDc a "Sí"
4. Usuario apuesta 15 DVDc a "No"
5. Verificar que todas se registran
```

**Resultado Esperado:** ✅ Todas las apuestas registradas

### ✅ Checklist de Verificación:
- [ ] Caso 1: Apuesta normal funciona
- [ ] Caso 2: Frontend bloquea deadline
- [ ] Caso 3: Backend bloquea deadline
- [ ] Caso 4: Reparto correcto
- [ ] Caso 5: Múltiples apuestas funcionan

---

## 🛠️ Herramientas de Verificación

### 1. Consola del Navegador
```javascript
// Abrir consola (F12)
// Buscar mensajes de deadline
console.log('⏰ Deadline pasada:', fechaFormateada);
```

### 2. Logs del Servidor
```bash
# Ver logs en tiempo real
tail -f logs/dvdcoin.log

# Buscar errores de deadline
grep "Error parsing fecha_limite" logs/dvdcoin.log
```

### 3. Base de Datos
```bash
# Abrir base de datos
sqlite3 data/apuestas.db

# Ver porras
SELECT * FROM porras;

# Ver apuestas
SELECT * FROM apuestas_usuarios;

# Ver estadísticas
SELECT * FROM estadisticas_porras;
```

### 4. API Testing
```bash
# Probar endpoint de apuestas
curl -X POST http://localhost:8000/api/porras/apostar \
  -H "Authorization: Bearer [TOKEN]" \
  -H "Content-Type: application/json" \
  -d '{"porra_id": 1, "opcion": "si", "cantidad": 10}'

# Ver porra específica
curl http://localhost:8000/api/porras/1 \
  -H "Authorization: Bearer [TOKEN]"
```

---

## 📊 Checklist Final de Verificación

### Sistema de Reparto:
- [ ] Bote se reparte 100% entre acertantes
- [ ] Reparto proporcional a lo apostado
- [ ] Sin comisiones
- [ ] Cálculo correcto verificado
- [ ] Funciona con múltiples apuestas

### Validación de Deadline:
- [ ] Frontend bloquea apuestas si deadline pasó
- [ ] Frontend muestra mensaje claro
- [ ] Backend rechaza apuestas si deadline pasó
- [ ] Backend cierra automáticamente la porra
- [ ] Mensaje de error es claro
- [ ] 10 porras actualizadas (100%)
- [ ] Manejo de errores correcto

### Documentación:
- [ ] Guía completa para usuarios
- [ ] Documentación técnica
- [ ] Ejemplos claros
- [ ] Instrucciones de verificación

---

## 🎯 Resultado Esperado

**Después de completar todas las verificaciones:**

✅ Sistema de reparto funciona correctamente  
✅ Validación de deadline funciona en todas las porras  
✅ Mensajes claros al usuario  
✅ Sin errores en logs  
✅ Base de datos consistente  

---

## 🆘 Solución de Problemas

### Problema 1: Frontend no muestra mensaje de deadline
**Solución:**
1. Verificar que la porra tiene `fecha_limite` en la BD
2. Verificar que el código de validación está en el HTML
3. Abrir consola del navegador y buscar errores
4. Verificar que la fecha está en formato correcto

### Problema 2: Backend no rechaza apuestas
**Solución:**
1. Verificar que la función `porra_apostar` tiene la validación
2. Verificar logs del servidor
3. Verificar que la fecha límite está en la BD
4. Probar con curl para ver el error exacto

### Problema 3: Reparto incorrecto
**Solución:**
1. Verificar que la función de reparto es la correcta
2. Verificar que no hay comisiones en el cálculo
3. Verificar que el total apostado a la opción ganadora es correcto
4. Revisar logs del servidor

### Problema 4: Porra no se cierra automáticamente
**Solución:**
1. Verificar que el backend tiene el código de cierre automático
2. Verificar que la fecha límite está en formato correcto
3. Verificar permisos de escritura en la BD
4. Revisar logs del servidor

---

**Fecha de Creación**: Mayo 2026  
**Sistema de Apuestas DVDcoin**  
**Instrucciones de Verificación Completas**
