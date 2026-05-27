# 🏦 DVDcoin Bank - Documentación del Proyecto

**Versión:** v5.1  
**Fecha:** Mayo 2026  
**Estado:** ✅ Producción

---

## 📖 Índice de Documentación

### 📚 Documentación Principal

#### 1. **SCRIPTS_PYTHON.md** 🐍
Guía completa de todos los scripts Python del proyecto.
- Descripción de cada script
- Cómo usarlos
- Ejemplos de uso
- Flujo de trabajo recomendado

**Leer cuando:** Necesites ejecutar o entender algún script Python del proyecto.

---

#### 2. **RESUMEN_LIMPIEZA_Y_MEJORAS.md** 🧹
Resumen de la última limpieza y mejoras del proyecto.
- Bugs corregidos
- Traducciones añadidas
- Archivos eliminados
- Mejoras implementadas

**Leer cuando:** Quieras saber qué cambios recientes se han hecho.

---

#### 3. **SISTEMA_APUESTAS_FINAL.md** 🎲
Documentación completa del sistema de apuestas deportivas.
- Arquitectura del sistema
- API endpoints
- Base de datos
- Flujo de trabajo
- Funcionalidades admin

**Leer cuando:** Trabajes con el sistema de apuestas o porras.

---

#### 4. **TASK_3_TRANSACTION_HISTORY_COMPLETED.md** 💰
Documentación del sistema de historial de transacciones.
- Implementación del historial
- Filtros y ordenación
- Optimizaciones
- API endpoints

**Leer cuando:** Trabajes con transacciones o historial bancario.

---

#### 5. **GRAPHIFY_INTEGRATION.md** 🧠
Documentación de integración de Graphify (Knowledge Graph).
- Qué es Graphify y para qué sirve
- Instalación y configuración
- Generación de grafos de conocimiento
- Casos de uso y ejemplos

**Leer cuando:** Quieras visualizar la arquitectura del proyecto o hacer onboarding de nuevos desarrolladores.

---

### 📁 Documentación en `.kiro/`

#### 6. **VIDEOLLAMADAS_FINAL.md**
Documentación final del sistema de videollamadas.

#### 7. **VIDEOLLAMADAS_FIXES.md**
Correcciones aplicadas al sistema de video.

#### 8. **VIDEOLLAMADAS_IMPLEMENTACION.md**
Detalles de implementación de videollamadas.

#### 9. **VIDEOLLAMADAS_JITSI.md**
Integración con Jitsi para videollamadas.

**Leer cuando:** Trabajes con el sistema de videollamadas o salas.

---

## 🚀 Inicio Rápido

### Primera vez:
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar autostart (opcional, como Admin)
python _setup_autostart.py

# 3. Arrancar servidor
python start.py
```

### Uso diario:
```bash
python start.py
```

### Si hay problemas:
```bash
python _restart_all.py
```

### Generar grafo de conocimiento (nuevo):
```bash
GENERAR_GRAFO_CONOCIMIENTO.bat
```

---

## 📂 Estructura del Proyecto

```
dvdcoin/
├── main.py                    # Servidor principal (FastAPI)
├── start.py                   # Launcher recomendado
├── _restart_all.py            # Reinicio completo
├── service_launcher.py        # Launcher para servicio Windows
├── watchdog.py                # Monitor de salud
├── _setup_autostart.py        # Configuración autostart
│
├── static/                    # Frontend
│   ├── index.html            # Aplicación principal
│   ├── i18n/                 # Traducciones (7 idiomas)
│   ├── css/                  # Estilos
│   ├── pages/                # Páginas adicionales
│   └── gallery/              # Galería de imágenes
│
├── game_pages/               # Juegos
│   ├── apuestas/            # Sistema de apuestas
│   ├── millonario/          # Juego del Millonario
│   ├── quiensoy/            # ¿Quién soy?
│   ├── cifrasletras/        # Cifras y Letras
│   ├── pasapalabra/         # Pasapalabra
│   └── messages/            # Chat y mensajes
│
├── data/                     # Bases de datos
│   ├── dvdcoin.db           # BD principal
│   ├── apuestas.db          # BD de apuestas
│   ├── messages.db          # BD de mensajes
│   └── stats.db             # BD de estadísticas
│
├── conf/                     # Configuración
│   ├── .ngrok_token         # Token de ngrok
│   └── .jwt_secret          # Secret para JWT
│
├── config/                   # Configuración adicional
│   ├── .openai_key          # API key de OpenAI
│   ├── .groq_key            # API key de Groq
│   └── master.txt           # Contraseña maestra
│
├── logs/                     # Logs
│   ├── app.log              # Log de aplicación
│   └── ngrok_url.log        # URL de ngrok
│
├── tests/                    # Tests
│   ├── test_ai_integration.py
│   ├── test_video_call.py
│   └── test_video_manual.py
│
└── docs/                     # Documentación adicional
    ├── SCRIPTS_PYTHON.md
    ├── RESUMEN_LIMPIEZA_Y_MEJORAS.md
    ├── SISTEMA_APUESTAS_FINAL.md
    └── TASK_3_TRANSACTION_HISTORY_COMPLETED.md
```

---

## 🌍 Idiomas Soportados

El proyecto soporta **7 idiomas** completos:

- 🇪🇸 Español (es)
- 🇬🇧 Inglés (en)
- 🇫🇷 Francés (fr)
- 🇩🇪 Alemán (de)
- 🇮🇹 Italiano (it)
- Catalán (ca)
- Euskera (eu)

**Archivos de traducción:** `static/i18n/*.json`

---

## 🎮 Funcionalidades

### 💰 Sistema Bancario
- Registro y autenticación de usuarios
- Transferencias entre usuarios
- Historial de transacciones
- Saldo y balance
- Sistema de administración

### 🎲 Sistema de Apuestas
- Creación de porras deportivas
- Apuestas múltiples
- Gestión de premios
- Estadísticas de usuario
- Panel de administración

### 💬 Sistema Social
- Chat grupal
- Mensajes directos
- Videollamadas (Jitsi)
- Salas de video
- Notificaciones en tiempo real

### 🎯 Juegos
- Millonario
- ¿Quién soy?
- Cifras y Letras
- Pasapalabra
- OPO (Simulacro de examen)

### 📖 Cuentos
- Biblioteca de historias
- Subida de cuentos (.docx, .txt)
- Gestión de contenido

### 🤖 Integración IA
- Claude (Anthropic)
- OpenAI (GPT)
- Groq
- Generación de contenido
- Asistente inteligente

---

## 🔧 Tecnologías

### Backend:
- **Python 3.8+**
- **FastAPI** - Framework web
- **Uvicorn** - Servidor ASGI
- **SQLite** - Base de datos
- **JWT** - Autenticación
- **WebSockets** - Tiempo real

### Frontend:
- **HTML5 / CSS3 / JavaScript**
- **Vanilla JS** - Sin frameworks
- **WebRTC** - Videollamadas
- **Jitsi** - Infraestructura de video

### Infraestructura:
- **ngrok** - Túnel público
- **Windows Service** - Servicio en segundo plano
- **Watchdog** - Monitor de salud

---

## 📊 Base de Datos

### Principales tablas:

#### `dvdcoin.db`
- `users` - Usuarios del sistema
- `transactions` - Transacciones bancarias
- `sessions` - Sesiones de usuario

#### `apuestas.db`
- `porras` - Porras deportivas
- `apuestas_usuarios` - Apuestas de usuarios
- `opciones` - Opciones de apuesta

#### `messages.db`
- `messages` - Mensajes de chat
- `msg_reads` - Lecturas de mensajes
- `msg_reactions` - Reacciones a mensajes

#### `stats.db`
- `user_stats` - Estadísticas de usuario
- `game_stats` - Estadísticas de juegos

---

## 🔐 Seguridad

- **JWT** para autenticación
- **Bcrypt** para contraseñas
- **Rate limiting** en API
- **CORS** configurado
- **Validación de entrada**
- **Sanitización de datos**

---

## 📝 Logs

Todos los logs se guardan en:
- `server.log` - Log del servidor
- `ngrok.log` - Log de ngrok
- `watchdog.log` - Log del watchdog
- `logs/app.log` - Log general

---

## 🐛 Debugging

### Ver logs en tiempo real:
```bash
# Windows
Get-Content server.log -Wait -Tail 50

# Linux/Mac
tail -f server.log
```

### Verificar estado del servidor:
```bash
curl http://localhost:8000/api/health
```

### Verificar base de datos:
```bash
sqlite3 data/dvdcoin.db "SELECT * FROM users;"
```

---

## 🚨 Solución de Problemas

### El servidor no arranca:
1. Verificar que el puerto 8000 esté libre
2. Revisar `server.log` para errores
3. Ejecutar `python _restart_all.py`

### ngrok no funciona:
1. Verificar token en `conf/.ngrok_token`
2. Revisar `ngrok.log`
3. Probar manualmente: `ngrok http 8000`

### Base de datos corrupta:
1. Hacer backup de `data/*.db`
2. Restaurar desde backup más reciente
3. O recrear desde cero (perderás datos)

---

## 📞 Contacto y Soporte

Para problemas o preguntas:
1. Revisar esta documentación
2. Revisar logs del sistema
3. Consultar documentación específica en `docs/`

---

## 📜 Licencia

Proyecto privado - DVDcoin Bank  
© 2026 - Todos los derechos reservados

---

## 🎉 Contribuciones

Este proyecto es mantenido por el equipo de DVDcoin Bank.

**Desarrolladores principales:**
- dvd
- nebulosa

---

**Última actualización:** 4 de Mayo de 2026  
**Versión:** v5.1  
**Estado:** ✅ Producción Estable
