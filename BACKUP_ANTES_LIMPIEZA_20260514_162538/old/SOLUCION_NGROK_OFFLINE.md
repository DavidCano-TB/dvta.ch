# ✅ SOLUCIÓN: Error "ERR_NGROK_3200 - Endpoint is offline"

## 🔍 Problema
El endpoint de ngrok `unhidden-patient-cradling.ngrok-free.dev` está offline porque:
- El servidor FastAPI no está corriendo en el puerto 8000
- El túnel ngrok no está activo
- O ambos servicios están detenidos

## 🚀 SOLUCIÓN RÁPIDA (Recomendada)

### Opción 1: Script Automático (TODO EN UNO)
Ejecuta este nuevo script que reinicia todo automáticamente:

```bash
REINICIAR_TODO_NGROK.bat
```

Este script:
1. ✓ Detiene todos los procesos antiguos (Python y ngrok)
2. ✓ Libera los puertos 8000 y 4040
3. ✓ Inicia el servidor FastAPI en segundo plano
4. ✓ Inicia ngrok en segundo plano
5. ✓ Obtiene la URL pública automáticamente
6. ✓ Abre el navegador con autenticación

**IMPORTANTE:** No cierres la ventana del script mientras uses la aplicación.

---

### Opción 2: Manual (Dos Terminales)

Si prefieres control manual:

#### Terminal 1 - Servidor:
```bash
REINICIAR_SERVIDOR_LIMPIO.bat
```
O directamente:
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Ngrok:
```bash
ngrok http 8000
```

#### Terminal 3 - Abrir Navegador:
```bash
ABRIR_NGROK_APUESTAS.bat
```

---

## 📋 Verificación

### 1. Verificar que el servidor está corriendo:
Abre en tu navegador: http://localhost:8000

Deberías ver la aplicación o una respuesta del servidor.

### 2. Verificar que ngrok está corriendo:
Abre en tu navegador: http://127.0.0.1:4040

Deberías ver el panel de control de ngrok con la URL pública.

### 3. Verificar los puertos:
```powershell
Get-NetTCPConnection -LocalPort 8000,4040 -ErrorAction SilentlyContinue
```

Deberías ver ambos puertos en estado "Listen".

---

## 🔧 Solución de Problemas

### Error: "Puerto 8000 ya está en uso"
```bash
# Matar proceso en puerto 8000
for /f "tokens=5" %a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %a
```

### Error: "ngrok no se reconoce como comando"
Ngrok no está instalado o no está en el PATH.

**Solución:**
1. Descarga ngrok desde: https://ngrok.com/download
2. Extrae el archivo `ngrok.exe`
3. Colócalo en una carpeta en el PATH o en la carpeta del proyecto

### Error: "No se pudo obtener el token"
La base de datos no tiene el usuario "dvd" o la columna token no existe.

**Solución:**
Verifica la base de datos:
```bash
python -c "import sqlite3; c=sqlite3.connect('data/users.db'); print(c.execute('SELECT username, token FROM users').fetchall())"
```

---

## 📝 URLs Importantes

Una vez todo esté corriendo:

- **Servidor Local:** http://localhost:8000
- **Panel ngrok:** http://127.0.0.1:4040
- **URL Pública:** Se muestra en el panel de ngrok o en la salida del script

### Endpoints de la aplicación:
- Lista de porras: `/apuestas`
- Porra específica: `/apuestas/porra/1`
- Votaciones: `/votaciones`

---

## ⚠️ IMPORTANTE

1. **No cierres las ventanas** de los scripts mientras uses la aplicación
2. **Ngrok gratuito** genera URLs aleatorias cada vez que se reinicia
3. **La URL cambia** cada vez que reinicias ngrok
4. Para **detener todo**, presiona cualquier tecla en la ventana del script `REINICIAR_TODO_NGROK.bat`

---

## 🎯 Resumen de Scripts Disponibles

| Script | Función |
|--------|---------|
| `REINICIAR_TODO_NGROK.bat` | ⭐ Reinicia servidor + ngrok automáticamente |
| `REINICIAR_SERVIDOR_LIMPIO.bat` | Reinicia solo el servidor FastAPI |
| `ABRIR_APUESTAS.bat` | Abre la app localmente (sin ngrok) |
| `ABRIR_NGROK_APUESTAS.bat` | Obtiene URL de ngrok y abre navegador |
| `startdvdcoin.bat` | Inicia el servidor (método original) |

---

## ✅ Estado Actual

- ✓ Código verificado sin errores de sintaxis
- ✓ Script de reinicio automático creado
- ✓ Script de reinicio limpio mejorado
- ✓ Documentación completa generada

**Siguiente paso:** Ejecuta `REINICIAR_TODO_NGROK.bat` y todo debería funcionar.
