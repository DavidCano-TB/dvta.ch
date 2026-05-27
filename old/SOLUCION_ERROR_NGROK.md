# Solución al Error ERR_NGROK_8012

## 🔴 Problema Original

```
ERR_NGROK_8012
Traffic successfully made it to the ngrok agent, but the agent failed to 
establish a connection to the upstream web service at http://localhost:8000.

Error: dial tcp [::1]:8000: connectex: Aucune connexion n'a pu être établie 
car l'ordinateur cible l'a expressément refusée.
```

## 🔍 Causa del Problema

El error ocurría porque:

1. **Ngrok se iniciaba correctamente** y creaba el túnel público
2. **El servidor NO estaba corriendo** en el puerto 8000
3. Cuando alguien accedía a la URL de ngrok, este intentaba conectarse a `localhost:8000` pero no había nada escuchando

### ¿Por qué el servidor no iniciaba?

Los scripts `.bat` usaban comandos incorrectos:

```batch
# ❌ INCORRECTO (lo que estaba antes)
pythonw main.py
```

El problema es que `main.py` es un módulo de FastAPI que necesita ser ejecutado con **uvicorn**, no directamente con Python.

## ✅ Solución Aplicada

### 1. Comando Correcto

Se cambió el comando de inicio del servidor a:

```batch
# ✅ CORRECTO (lo que está ahora)
pythonw -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Este comando:
- `-m uvicorn`: Ejecuta uvicorn como módulo de Python
- `src.main:app`: Importa la aplicación FastAPI desde `src/main.py`
- `--host 0.0.0.0`: Escucha en todas las interfaces de red
- `--port 8000`: Usa el puerto 8000

### 2. Scripts Corregidos

Se actualizaron los siguientes archivos:

#### `ARRANCAR.bat`
```batch
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

#### `ARRANQUE_AUTOMATICO_COMPLETO.bat`
```batch
start /B pythonw -m uvicorn src.main:app --host 0.0.0.0 --port 8000
timeout /t 10 /nobreak >nul  # Aumentado de 8 a 10 segundos
```

#### `ADMIN_INICIAR_NGROK.bat`
```batch
start "DVDcoin Server" pythonw -m uvicorn src.main:app --host 0.0.0.0 --port 8000
timeout /t 10 /nobreak >nul  # Aumentado de 5 a 10 segundos
```

### 3. Nuevos Scripts Creados

#### `VERIFICAR_SERVIDOR.bat`
Verifica el estado del servidor y ngrok:
- Comprueba si el puerto 8000 está en uso
- Prueba la conexión HTTP local
- Verifica si ngrok está corriendo
- Muestra las URLs disponibles

#### `DETENER_TODO.bat`
Detiene todos los servicios de forma limpia:
- Mata procesos Python
- Detiene ngrok
- Libera el puerto 8000

#### `INSTALAR_DEPENDENCIAS.bat`
Instala todas las dependencias necesarias:
- Verifica Python y pip
- Instala FastAPI, uvicorn, etc.
- Verifica la instalación

#### `requirements.txt`
Lista de dependencias del proyecto:
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-jose[cryptography]>=3.3.0
bcrypt>=4.0.1
pydantic>=2.0.0
python-multipart>=0.0.6
slowapi>=0.1.9
websockets>=12.0
```

## 📋 Cómo Usar la Solución

### Opción 1: Arranque Automático (Recomendado)

```batch
# Ejecutar este script
ARRANQUE_AUTOMATICO_COMPLETO.bat
```

Este script:
1. Detiene procesos anteriores
2. Inicia el servidor en segundo plano
3. Espera 10 segundos
4. Inicia ngrok
5. Obtiene la URL pública
6. Abre el navegador automáticamente

### Opción 2: Arranque Manual

```batch
# Paso 1: Iniciar servidor
ARRANCAR.bat

# Paso 2: En otra ventana, iniciar ngrok
ADMIN_INICIAR_NGROK.bat
```

### Opción 3: Solo Servidor Local

```batch
# Solo servidor, sin ngrok
ARRANCAR.bat
```

Luego abrir: http://localhost:8000

## 🔧 Verificación

Después de iniciar, ejecutar:

```batch
VERIFICAR_SERVIDOR.bat
```

Debe mostrar:
```
[OK] Servidor corriendo en puerto 8000
Codigo HTTP: 200
[OK] Ngrok corriendo
```

## 🚨 Solución de Problemas

### Si sigue apareciendo ERR_NGROK_8012:

1. **Detener todo:**
   ```batch
   DETENER_TODO.bat
   ```

2. **Verificar que todo está detenido:**
   ```batch
   VERIFICAR_SERVIDOR.bat
   ```

3. **Instalar dependencias (si es necesario):**
   ```batch
   INSTALAR_DEPENDENCIAS.bat
   ```

4. **Reiniciar:**
   ```batch
   ARRANQUE_AUTOMATICO_COMPLETO.bat
   ```

### Si uvicorn no está instalado:

```batch
pip install uvicorn[standard]
```

O ejecutar:
```batch
INSTALAR_DEPENDENCIAS.bat
```

### Si el puerto 8000 está ocupado:

```batch
# Ver qué proceso usa el puerto
netstat -ano | findstr :8000

# Matar el proceso (reemplazar PID con el número que aparece)
taskkill /F /PID <PID>
```

## 📊 Flujo Correcto

```
┌─────────────────────────────────────────────────────────┐
│ 1. DETENER_TODO.bat                                     │
│    └─> Limpia procesos anteriores                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Iniciar Servidor                                     │
│    └─> uvicorn src.main:app --port 8000                │
│    └─> Esperar 10 segundos                             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Verificar Servidor                                   │
│    └─> curl http://localhost:8000                      │
│    └─> Debe responder HTTP 200                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Iniciar Ngrok                                        │
│    └─> ngrok http 8000                                 │
│    └─> Obtener URL pública                             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Acceder desde Internet                               │
│    └─> https://xxxx.ngrok.io                           │
│    └─> Ngrok redirige a localhost:8000                 │
│    └─> ✅ Funciona correctamente                        │
└─────────────────────────────────────────────────────────┘
```

## 📝 Notas Técnicas

### ¿Por qué uvicorn?

FastAPI es un framework ASGI que necesita un servidor ASGI para ejecutarse. Uvicorn es el servidor ASGI recomendado por FastAPI.

### ¿Por qué pythonw en lugar de python?

- `python`: Muestra una ventana de consola
- `pythonw`: Ejecuta en segundo plano sin ventana (útil para scripts automáticos)

### ¿Por qué esperar 10 segundos?

El servidor necesita tiempo para:
1. Importar todos los módulos
2. Inicializar las bases de datos
3. Configurar las rutas
4. Empezar a escuchar en el puerto 8000

10 segundos es un margen seguro para asegurar que el servidor está completamente listo antes de iniciar ngrok.

## ✅ Resultado Final

Después de aplicar esta solución:

- ✅ El servidor inicia correctamente en puerto 8000
- ✅ Ngrok se conecta exitosamente al servidor
- ✅ La URL pública funciona sin errores
- ✅ No más ERR_NGROK_8012

## 📚 Archivos Modificados

- ✏️ `ARRANCAR.bat` - Comando de inicio corregido
- ✏️ `ARRANQUE_AUTOMATICO_COMPLETO.bat` - Comando y timeout actualizados
- ✏️ `ADMIN_INICIAR_NGROK.bat` - Comando y timeout actualizados
- ➕ `VERIFICAR_SERVIDOR.bat` - Nuevo script de verificación
- ➕ `DETENER_TODO.bat` - Nuevo script de limpieza
- ➕ `INSTALAR_DEPENDENCIAS.bat` - Nuevo script de instalación
- ➕ `requirements.txt` - Nueva lista de dependencias
- ➕ `INSTRUCCIONES_ARRANQUE.txt` - Guía completa de uso
- ➕ `SOLUCION_ERROR_NGROK.md` - Este documento

---

**Fecha de corrección:** 14 de mayo de 2026  
**Problema resuelto:** ERR_NGROK_8012 - Servidor no disponible en puerto 8000
