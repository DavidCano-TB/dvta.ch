# 📖 INSTRUCCIONES DE USO - Suite de Tests Funcionales

## 🎯 Objetivo

Esta suite de tests verifica **exhaustivamente** todas las funcionalidades de DVDcoin Bank, incluyendo:
- ✅ Endpoints de API (REST)
- ✅ WebSockets en tiempo real
- ✅ Autenticación y autorización
- ✅ Validaciones de datos
- ✅ Flujos completos de usuario
- ✅ Integración frontend-backend
- ✅ Manejo de errores

## 📋 Requisitos Previos

### 1. Python 3.8+
```bash
python --version
```

### 2. Dependencias
```bash
pip install requests websocket-client
```

### 3. Servidor en ejecución
El servidor debe estar corriendo en `http://localhost:8000` (o la URL configurada)

## ⚙️ Configuración

### 1. Editar `config.json`

```json
{
  "server": {
    "base_url": "http://localhost:8000",  // URL del servidor
    "ws_url": "ws://localhost:8000",      // URL WebSocket
    "timeout": 30
  },
  "credentials": {
    "admin": {
      "username": "dvd",                  // Usuario admin
      "password": "tu_password"           // Contraseña admin
    },
    "test_user": {
      "username": "test_user",            // Usuario de prueba 1
      "password": "test123"
    },
    "test_user2": {
      "username": "test_user2",           // Usuario de prueba 2
      "password": "test123"
    }
  }
}
```

### 2. Crear usuarios de prueba (opcional)

Si los usuarios de prueba no existen, créalos desde la aplicación o mediante:
```bash
python -c "import requests; requests.post('http://localhost:8000/api/register', json={'username':'test_user','password':'test123'})"
python -c "import requests; requests.post('http://localhost:8000/api/register', json={'username':'test_user2','password':'test123'})"
```

## 🚀 Ejecución

### Opción 1: Ejecutar TODOS los tests

**Windows:**
```bash
EJECUTAR_TODOS_LOS_TESTS.bat
```

**Linux/Mac:**
```bash
python RUN_ALL_TESTS.py
```

### Opción 2: Ejecutar un test individual

**Windows:**
```bash
cd 01_transferencias
EJECUTAR_TEST.bat
```

**Linux/Mac:**
```bash
cd 01_transferencias
python test_transferencias.py
```

## 📊 Interpretación de Resultados

### Logs

Cada test genera un log detallado en `logs/test_[nombre]_[timestamp].log`

Ejemplo:
```
2026-05-11 10:30:15 | INFO     | ================================================================================
2026-05-11 10:30:15 | INFO     | 🧪 INICIANDO TEST: TRANSFERENCIAS
2026-05-11 10:30:15 | INFO     | ================================================================================
2026-05-11 10:30:16 | INFO     | ✅ Login exitoso como dvd
2026-05-11 10:30:17 | INFO     | ✅ Transferencia básica: Status 200 ✓
2026-05-11 10:30:18 | ERROR    | ❌ Validación falló: Se permitió monto negativo
```

### Resumen Final

Al final de cada test verás:
```
================================================================================
📊 RESUMEN DEL TEST
================================================================================
✅ Tests exitosos:  45
❌ Tests fallidos:  2
⚠️  Advertencias:    3
📈 Tasa de éxito:   95.7%
================================================================================
```

### Código de Salida

- `0` = Todos los tests pasaron ✅
- `1` = Algunos tests fallaron ❌

## 📁 Estructura de Tests

```
test_funcionalidades/
├── 01_transferencias/          # Sistema de transacciones
│   ├── test_transferencias.py
│   ├── EJECUTAR_TEST.bat
│   └── logs/
├── 02_opo/                     # Sistema de oposiciones
│   ├── test_opo.py
│   ├── EJECUTAR_TEST.bat
│   └── logs/
├── 03_millonario/              # Juego Millonario
│   ├── test_millonario.py
│   ├── EJECUTAR_TEST.bat
│   └── logs/
├── 04_video/                   # Sistema de video WebRTC
│   ├── test_video.py
│   ├── EJECUTAR_TEST.bat
│   └── logs/
├── 05_cifras_letras/           # Juego Cifras y Letras
│   ├── test_cifras_letras.py
│   ├── EJECUTAR_TEST.bat
│   └── logs/
├── 06_pasapalabra/             # Juego Pasapalabra
│   ├── test_pasapalabra.py
│   ├── EJECUTAR_TEST.bat
│   └── logs/
├── 07_hundir_flota/            # Juego Hundir la Flota
│   ├── test_hundir_flota.py
│   ├── EJECUTAR_TEST.bat
│   └── logs/
├── 08_mensajes/                # Sistema de mensajería
│   ├── test_mensajes.py
│   ├── EJECUTAR_TEST.bat
│   └── logs/
├── 09_apuestas/                # Sistema de apuestas
│   ├── test_apuestas.py
│   ├── EJECUTAR_TEST.bat
│   └── logs/
├── 10_votaciones/              # Sistema de votaciones
│   ├── test_votaciones.py
│   ├── EJECUTAR_TEST.bat
│   └── logs/
├── 11_cuentos/                 # Sistema de cuentos
│   ├── test_cuentos.py
│   ├── EJECUTAR_TEST.bat
│   └── logs/
├── test_utils.py               # Utilidades comunes
├── config.json                 # Configuración
├── RUN_ALL_TESTS.py            # Ejecutor principal
├── EJECUTAR_TODOS_LOS_TESTS.bat
├── README.md
└── INSTRUCCIONES.md            # Este archivo
```

## 🔍 Qué Verifica Cada Test

### 01_transferencias
- ✅ Login y autenticación
- ✅ Consulta de balance
- ✅ Transferencias básicas
- ✅ Validaciones (monto negativo, saldo insuficiente, etc.)
- ✅ Historial de transacciones
- ✅ Rate limiting
- ✅ Estadísticas

### 02_opo
- ✅ Gestión de jugadores
- ✅ Carga de preguntas
- ✅ Inicio de sesión
- ✅ Respuestas de usuarios
- ✅ Resultados y rankings
- ✅ Historial de sesiones

### 03_millonario
- ✅ Conexión WebSocket
- ✅ Configuración del juego
- ✅ Preguntas y respuestas
- ✅ Comodín 50/50
- ✅ Plantarse
- ✅ Reinicio

### 04_video
- ✅ ICE servers
- ✅ Salas de video
- ✅ Señalización WebRTC (offer/answer)
- ✅ ICE candidates
- ✅ Control de cámara/micrófono
- ✅ Participantes en sala

### 05_cifras_letras
- ✅ Configuración del juego
- ✅ Rondas de letras
- ✅ Rondas de números
- ✅ Temporizador
- ✅ Envío de respuestas
- ✅ Revelación de resultados

### 06_pasapalabra
- ✅ Configuración de jugadores
- ✅ Rosco de letras
- ✅ Preguntas y respuestas
- ✅ Pasar palabra
- ✅ Temporizador por jugador
- ✅ Pausa/reanudación

### 07_hundir_flota
- ✅ Configuración del tablero
- ✅ Colocación de barcos
- ✅ Validación de posiciones
- ✅ Ataques
- ✅ Detección de impactos/fallos
- ✅ Victoria

### 08_mensajes
- ✅ Mensajes directos
- ✅ Mensajes grupales
- ✅ Marcar como leído
- ✅ Mensajes no leídos
- ✅ Búsqueda de mensajes
- ✅ Eliminación (admin)

### 09_apuestas
- ✅ Crear porras
- ✅ Realizar apuestas
- ✅ Cerrar porras
- ✅ Resolver porras
- ✅ Estadísticas
- ✅ Historial

### 10_votaciones
- ✅ Crear votaciones
- ✅ Emitir votos
- ✅ Prevenir votos duplicados
- ✅ Resultados
- ✅ Cerrar votaciones
- ✅ Eliminación

### 11_cuentos
- ✅ Habilitar/deshabilitar
- ✅ Subir archivos
- ✅ Listar cuentos
- ✅ Enmascarar/desenmascarar
- ✅ Eliminación
- ✅ Permisos de acceso

## 🐛 Solución de Problemas

### Error: "No se pudo conectar al servidor"
- Verifica que el servidor esté corriendo
- Comprueba la URL en `config.json`
- Revisa el firewall

### Error: "Login fallido"
- Verifica las credenciales en `config.json`
- Asegúrate de que los usuarios existen
- Comprueba que las contraseñas sean correctas

### Error: "WebSocket no se conectó"
- Verifica que el servidor soporte WebSockets
- Comprueba la URL WebSocket en `config.json`
- Revisa los logs del servidor

### Error: "ModuleNotFoundError"
```bash
pip install requests websocket-client
```

## 📈 Mejores Prácticas

1. **Ejecuta los tests regularmente** después de cambios en el código
2. **Revisa los logs detallados** cuando un test falle
3. **Mantén actualizado** el `config.json` con las credenciales correctas
4. **Ejecuta primero tests individuales** antes de la suite completa
5. **Guarda los logs** de tests exitosos como referencia

## 🎓 Extender los Tests

Para añadir nuevos tests:

1. Crea una nueva carpeta: `12_nueva_funcionalidad/`
2. Copia la estructura de un test existente
3. Modifica el contenido según tu funcionalidad
4. Añade el test a `RUN_ALL_TESTS.py`
5. Crea el archivo `EJECUTAR_TEST.bat`

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs en `logs/`
2. Verifica la configuración en `config.json`
3. Comprueba que el servidor esté funcionando correctamente
4. Revisa la documentación de la API

---

**¡Buena suerte con los tests! 🚀**
