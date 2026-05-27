# 🚀 Sistema de Servidores Múltiples - DVDcoin

## 📋 Arquitectura

El sistema DVDcoin ahora funciona con **4 servidores independientes** que trabajan simultáneamente:

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUDFLARE TUNNEL                        │
│                  (cloudflared.exe)                          │
│                                                             │
│  https://dvta.ch          → localhost:8000 (Bank)          │
│  https://bank.dvta.ch     → localhost:8000 (Bank)          │
│  https://exams.dvta.ch    → localhost:8001 (Exams)         │
│  https://games.dvta.ch    → localhost:8002 (Games)         │
│  https://social.dvta.ch   → localhost:8003 (Social)        │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Servidores

### 1. **Bank (Puerto 8000)** ✅
- **Ruta:** `src/main.py`
- **Dominio:** https://dvta.ch / https://bank.dvta.ch
- **Funciones:**
  - Dashboard principal
  - Sistema bancario (transacciones, balances)
  - Gestión de usuarios
  - Galería
  - Cuentos
  - Votaciones
  - Estadísticas

### 2. **Exams (Puerto 8001)** ✅
- **Ruta:** `modules/exams/app_exams.py`
- **Dominio:** https://exams.dvta.ch
- **Funciones:**
  - Sistema de oposiciones
  - Tests y exámenes
  - Gestión de preguntas
  - Estadísticas de rendimiento

### 3. **Games (Puerto 8002)** ✅ NUEVO
- **Ruta:** `modules/games/app_games.py`
- **Dominio:** https://games.dvta.ch
- **Funciones:**
  - Pasapalabra
  - Millonario
  - ¿Quién Soy?
  - Cifras y Letras
  - Hundir la Flota
  - Apuestas
  - Sistema de puntuaciones

### 4. **Social (Puerto 8003)** ✅ NUEVO
- **Ruta:** `modules/social/app_social.py`
- **Dominio:** https://social.dvta.ch
- **Funciones:**
  - Chat en tiempo real
  - Mensajería
  - Videollamadas
  - Salas privadas
  - Notificaciones

## 🚀 Cómo Usar

### Opción 1: Iniciar Todos los Servidores (Recomendado)

```cmd
INICIAR_TODOS_SERVIDORES.bat
```

Este script:
1. ✅ Verifica que Python esté instalado
2. ✅ Crea directorios necesarios
3. ✅ Inicia los 4 servidores en ventanas separadas
4. ✅ Verifica que todos estén corriendo
5. ✅ Abre el navegador automáticamente

### Opción 2: Iniciar Servidores Individualmente

**Bank:**
```cmd
cd src
python main.py
```

**Exams:**
```cmd
cd modules\exams
python start_exams.py
```

**Games:**
```cmd
cd modules\games
python start_games.py
```

**Social:**
```cmd
cd modules\social
python start_social.py
```

### Verificar Estado de Servidores

```cmd
VERIFICAR_SERVIDORES.bat
```

Muestra:
- ✅ Estado de cada servidor (corriendo/detenido)
- 📊 Puertos en uso
- 🌐 URLs de acceso

### Detener Todos los Servidores

```cmd
DETENER_TODOS_SERVIDORES.bat
```

Detiene todos los procesos Python en los puertos 8000-8003.

## 🔧 Características Técnicas

### Autenticación Compartida
- Todos los servidores usan el **mismo JWT secret**
- Token almacenado en: `src/config/jwt_secret.txt`
- Cookie compartida: `dvd_token`
- Expiración: 168 horas (1 semana)

### Bases de Datos Independientes
Cada servidor tiene sus propias bases de datos:

**Bank:**
- `data/users.db` - Usuarios principales
- `data/transactions.db` - Transacciones
- `data/rights.db` - Permisos
- `data/stats.db` - Estadísticas
- `data/opo.db` - Oposiciones
- `data/apuestas.db` - Apuestas

**Exams:**
- `modules/exams/data/users_exams.db` - Usuarios de exams
- `modules/exams/data/exams.db` - Exámenes
- `modules/exams/data/opo.db` - Oposiciones

**Games:**
- `modules/games/data/games.db` - Juegos
- `modules/games/data/scores.db` - Puntuaciones

**Social:**
- `modules/social/data/messages.db` - Mensajes
- `modules/social/data/rooms.db` - Salas

### Módulos Compartidos
Todos los servidores usan módulos comunes en `modules/shared/`:
- `jwt_helper.py` - Gestión de JWT
- `db_helper.py` - Helper de base de datos
- `email_service.py` - Servicio de email
- `utils.py` - Utilidades comunes

## 📊 Health Checks

Cada servidor tiene un endpoint de health check:

```bash
# Bank
curl http://localhost:8000/bank/api/health

# Exams
curl http://localhost:8001/api/health

# Games
curl http://localhost:8002/api/health

# Social
curl http://localhost:8003/api/health
```

Respuesta:
```json
{
  "status": "ok",
  "service": "games",
  "port": 8002,
  "timestamp": "2026-05-27T20:30:00"
}
```

## 🌐 URLs de Acceso

### Producción (Cloudflare)
- **Bank:** https://dvta.ch/bank
- **Exams:** https://exams.dvta.ch
- **Games:** https://games.dvta.ch
- **Social:** https://social.dvta.ch

### Local (Desarrollo)
- **Bank:** http://localhost:8000/bank
- **Exams:** http://localhost:8001/exams
- **Games:** http://localhost:8002/games
- **Social:** http://localhost:8003/social

## 🔄 Flujo de Trabajo

### Desarrollo
1. Ejecuta `INICIAR_TODOS_SERVIDORES.bat`
2. Trabaja en el servidor que necesites
3. Los cambios se reflejan automáticamente (hot reload)
4. Usa `VERIFICAR_SERVIDORES.bat` para verificar estado

### Producción
1. Cloudflare Tunnel debe estar corriendo
2. Todos los servidores deben estar activos
3. Verifica con `VERIFICAR_SERVIDORES.bat`
4. Monitorea logs en cada ventana de servidor

## 🛠️ Solución de Problemas

### Problema: Puerto en uso
```cmd
# Ver qué proceso usa el puerto
netstat -ano | findstr ":8000"

# Matar el proceso (reemplaza PID)
taskkill /F /PID <PID>
```

### Problema: Servidor no inicia
1. Verifica que Python esté instalado: `python --version`
2. Instala dependencias: `pip install fastapi uvicorn pydantic`
3. Revisa logs en la ventana del servidor

### Problema: Error de importación
```cmd
# Instalar módulos compartidos
cd modules\shared
pip install -r requirements.txt
```

### Problema: Cloudflare no conecta
1. Verifica que cloudflared esté corriendo
2. Revisa `cloudflare-multi-server.yml`
3. Reinicia el túnel

## 📝 Archivos Creados

### Nuevos Servidores
- ✅ `modules/games/app_games.py` - Servidor Games
- ✅ `modules/games/start_games.py` - Script de inicio Games
- ✅ `modules/social/app_social.py` - Servidor Social
- ✅ `modules/social/start_social.py` - Script de inicio Social

### Scripts de Gestión
- ✅ `INICIAR_TODOS_SERVIDORES.bat` - Inicia todos
- ✅ `DETENER_TODOS_SERVIDORES.bat` - Detiene todos
- ✅ `VERIFICAR_SERVIDORES.bat` - Verifica estado

### Documentación
- ✅ `SERVIDORES_MULTIPLES_README.md` - Este archivo

## 🎉 Ventajas del Sistema Multi-Servidor

1. **Escalabilidad:** Cada servidor puede escalar independientemente
2. **Mantenimiento:** Actualiza un servidor sin afectar los demás
3. **Rendimiento:** Carga distribuida entre múltiples procesos
4. **Organización:** Código modular y fácil de mantener
5. **Desarrollo:** Trabaja en un módulo sin reiniciar todo
6. **Monitoreo:** Logs separados por servicio

## 🔐 Seguridad

- ✅ JWT compartido entre servidores
- ✅ Cookies HTTP-only
- ✅ CORS configurado
- ✅ Rate limiting (en Bank)
- ✅ Autenticación en todos los endpoints protegidos

## 📈 Próximos Pasos

1. ✅ Todos los servidores funcionando
2. ⏳ Agregar más juegos al servidor Games
3. ⏳ Implementar notificaciones push en Social
4. ⏳ Dashboard de monitoreo centralizado
5. ⏳ Sistema de logs centralizado

---

**Fecha de creación:** 27 de mayo de 2026  
**Versión:** 1.0.0  
**Estado:** ✅ Todos los servidores operativos
