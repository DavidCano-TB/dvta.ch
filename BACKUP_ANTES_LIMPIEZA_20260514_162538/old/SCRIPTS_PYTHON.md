# 📚 Scripts Python de DVDcoin Bank

Este documento describe todos los scripts Python útiles del proyecto, cómo usarlos y para qué sirven.

---

## 🚀 Scripts de Arranque y Gestión

### `main.py`
**Descripción:** Servidor principal de DVDcoin Bank (FastAPI + Uvicorn)

**Uso:**
```bash
python main.py
```

**Función:**
- Servidor web FastAPI en puerto 8000
- API REST completa para el banco
- Sistema de autenticación JWT
- Gestión de usuarios, transacciones, juegos
- Sistema de apuestas (porras deportivas)
- Chat y videollamadas
- Integración con IA (Claude, OpenAI, Groq)

**Notas:**
- Este es el archivo principal del proyecto
- Contiene toda la lógica del backend
- Se ejecuta automáticamente con `start.py`

---

### `start.py`
**Descripción:** Launcher definitivo que arranca servidor + ngrok

**Uso:**
```bash
python start.py
```

**Función:**
- Verifica dependencias (instala si faltan)
- Libera puerto 8000 si está ocupado
- Arranca `main.py` en segundo plano
- Configura y arranca ngrok con dominio reservado
- Muestra URL pública y local
- Abre navegador automáticamente
- Gestiona logs (server.log, ngrok.log)

**Notas:**
- **Recomendado para uso diario**
- Maneja todo el proceso de arranque
- Ctrl+C detiene todo limpiamente

---

### `_restart_all.py`
**Descripción:** Reinicia servidor y ngrok completamente

**Uso:**
```bash
python _restart_all.py
```

**Función:**
- Mata procesos en puerto 8000
- Mata procesos ngrok
- Reinicia servidor
- Reinicia ngrok
- Verifica que todo funcione

**Notas:**
- Útil cuando algo se queda colgado
- Hace limpieza completa de procesos

---

## 🔧 Scripts de Servicio Windows

### `service_launcher.py`
**Descripción:** Launcher silencioso para servicio Windows

**Uso:**
```bash
python service_launcher.py
```

**Función:**
- Arranca servidor sin ventana
- Logs a archivo (server.log)
- Monitorea servidor y reinicia si muere
- Arranca ngrok automáticamente
- Diseñado para ejecutarse como servicio

**Notas:**
- Usado por el servicio Windows DVDcoinBank
- No requiere interacción del usuario
- Se ejecuta en segundo plano

---

### `watchdog.py`
**Descripción:** Monitor que verifica salud del servidor cada 10 minutos

**Uso:**
```bash
python watchdog.py
```

**Función:**
- Verifica cada 10 minutos que http://localhost:8000 responde
- Si falla 2 veces consecutivas, reinicia el servidor
- Mata procesos en puerto 8000 si es necesario
- Logs detallados en watchdog.log
- Guarda PID en watchdog.pid

**Notas:**
- Útil para mantener servidor siempre activo
- Se ejecuta en segundo plano
- Reinicia automáticamente si hay problemas

---

### `_do_restart.py`
**Descripción:** Script simple de reinicio rápido

**Uso:**
```bash
python _do_restart.py
```

**Función:**
- Mata puerto 8000
- Arranca main.py
- Verifica endpoint /api/health
- Verifica endpoint /api/ice-servers

**Notas:**
- Más simple que `_restart_all.py`
- Solo reinicia servidor (no ngrok)

---

### `_setup_autostart.py`
**Descripción:** Configura arranque automático en Windows

**Uso:**
```bash
python _setup_autostart.py
```
**(Ejecutar como Administrador)**

**Función:**
- Borra archivos obsoletos del proyecto
- Elimina tareas programadas antiguas
- Crea tarea "DVDcoin-Autostart" en Windows
- Configura arranque al iniciar sesión
- Reinicia servidor con versión actualizada

**Notas:**
- **Ejecutar solo una vez** para configurar autostart
- Requiere permisos de administrador
- El servidor arrancará automáticamente al iniciar Windows

---

## 🧪 Scripts de Testing

### `tests/test_ai_integration.py`
**Descripción:** Tests de integración con APIs de IA

**Uso:**
```bash
python tests/test_ai_integration.py
```

**Función:**
- Prueba integración con Claude (Anthropic)
- Prueba integración con OpenAI
- Prueba integración con Groq
- Verifica que las claves API funcionan

---

### `tests/test_video_call.py`
**Descripción:** Tests del sistema de videollamadas

**Uso:**
```bash
python tests/test_video_call.py
```

**Función:**
- Prueba creación de salas de video
- Prueba unirse a salas
- Prueba invitaciones
- Verifica WebRTC y señalización

---

### `tests/test_video_manual.py`
**Descripción:** Tests manuales de video

**Uso:**
```bash
python tests/test_video_manual.py
```

**Función:**
- Tests interactivos de videollamadas
- Permite probar manualmente funcionalidades
- Útil para debugging

---

## 📊 Archivos de Datos

### `data/fix_passwords.py`
**Descripción:** Script para resetear contraseñas en la base de datos

**Ubicación:** `data/fix_passwords.py`

**Uso:**
```bash
cd data
python fix_passwords.py
```

**Función:**
- Resetea contraseñas de usuarios
- Útil si alguien olvida su contraseña
- Modifica directamente la base de datos

**Notas:**
- **Usar con precaución**
- Hace cambios permanentes en la BD
- Hacer backup antes de usar

---

## 🎯 Recomendaciones de Uso

### Para desarrollo diario:
```bash
python start.py
```

### Para producción (servicio Windows):
```bash
python service_launcher.py
```

### Para configurar autostart (una sola vez):
```bash
python _setup_autostart.py
```
*(Como Administrador)*

### Si algo falla:
```bash
python _restart_all.py
```

### Para monitoreo continuo:
```bash
python watchdog.py
```
*(En segundo plano)*

---

## 📝 Logs

Todos los scripts generan logs en la raíz del proyecto:

- **server.log** - Log del servidor principal
- **ngrok.log** - Log de ngrok
- **watchdog.log** - Log del watchdog
- **logs/app.log** - Log general de la aplicación
- **logs/ngrok_url.log** - URL pública de ngrok

---

## ⚠️ Notas Importantes

1. **Puerto 8000:** Todos los scripts usan el puerto 8000 por defecto
2. **ngrok:** Requiere token configurado en `conf/.ngrok_token`
3. **Python:** Requiere Python 3.8 o superior
4. **Dependencias:** Se instalan automáticamente con `start.py`
5. **Windows:** Algunos scripts son específicos para Windows (taskkill, netstat)

---

## 🔄 Flujo de Trabajo Típico

1. **Primera vez:**
   ```bash
   python _setup_autostart.py  # Como Admin
   ```

2. **Uso diario:**
   ```bash
   python start.py
   ```

3. **Si hay problemas:**
   ```bash
   python _restart_all.py
   ```

4. **Para producción:**
   - Configurar servicio Windows con `service_launcher.py`
   - Activar watchdog con `watchdog.py`

---

## 📞 Soporte

Si tienes problemas con algún script:

1. Revisa los logs correspondientes
2. Verifica que el puerto 8000 esté libre
3. Asegúrate de tener las dependencias instaladas
4. Comprueba que ngrok esté configurado (si lo usas)

---

**Última actualización:** Mayo 2026
**Versión del proyecto:** DVDcoin Bank v5.1
