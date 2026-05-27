# 🏗️ Arquitectura del Sistema DVDBank

## 📋 Resumen

Sistema modular de alta disponibilidad con múltiples servidores, balanceo de carga y monitoreo automático.

## 🎯 Características

- ✅ **Arquitectura Modular**: Servidores independientes por funcionalidad
- ✅ **Alta Disponibilidad**: Reinicio automático en caso de fallo
- ✅ **Balanceo de Carga**: Cloudflare Tunnel con múltiples rutas
- ✅ **Monitoreo Continuo**: Health checks y alertas automáticas
- ✅ **Escalabilidad**: Fácil añadir nuevos servidores
- ✅ **Gestión Centralizada**: Un solo punto de control

## 🏛️ Arquitectura

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
│  https://api.dvta.ch      → localhost:8000 (API)           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  GESTOR DE SERVIDORES                       │
│              (arquitectura_servidores.py)                   │
│                                                             │
│  • Inicia/detiene servidores                               │
│  • Monitorea salud (health checks)                         │
│  • Reinicia automáticamente si falla                       │
│  • Gestiona configuración                                  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   SERVIDOR   │   │   SERVIDOR   │   │   SERVIDOR   │
│     BANK     │   │    EXAMS     │   │    GAMES     │
│  Puerto 8000 │   │  Puerto 8001 │   │  Puerto 8002 │
│              │   │              │   │              │
│ • Dashboard  │   │ • Oposiciones│   │ • Juegos     │
│ • Transacc.  │   │ • Tests      │   │ • Apuestas   │
│ • Usuarios   │   │ • Exámenes   │   │ • Pasapalabra│
│ • API        │   │ • Estadístic.│   │ • Millonario │
└──────────────┘   └──────────────┘   └──────────────┘

        ┌───────────────────┐
        │   SERVIDOR        │
        │    SOCIAL         │
        │  Puerto 8003      │
        │                   │
        │ • Chat            │
        │ • Mensajes        │
        │ • Videollamadas   │
        │ • Notificaciones  │
        └───────────────────┘
```

## 📁 Estructura de Archivos

```
c:\dvdcoin\
│
├── 🎯 GESTIÓN DEL SISTEMA
│   ├── SISTEMA_COMPLETO.bat              # Menú principal de gestión
│   ├── REINICIAR_SISTEMA.bat             # Reinicio rápido
│   ├── arquitectura_servidores.py        # Gestor de servidores
│   └── servers_config.json               # Configuración de servidores
│
├── ☁️ CLOUDFLARE
│   ├── cloudflare-multi-server.yml       # Config túnel multi-servidor
│   └── cloudflare-dvta-config.yml        # Config túnel simple
│
├── 🖥️ SERVIDORES
│   ├── main.py                           # Servidor Bank (8000)
│   ├── modules/exams/start_exams.py      # Servidor Exams (8001)
│   ├── modules/games/start_games.py      # Servidor Games (8002)
│   └── modules/social/start_social.py    # Servidor Social (8003)
│
├── 📊 BASES DE DATOS
│   ├── users.db                          # Usuarios y autenticación
│   ├── transactions.db                   # Transacciones bancarias
│   ├── rights.db                         # Permisos y roles
│   ├── stats.db                          # Estadísticas
│   ├── opo.db                            # Oposiciones
│   ├── apuestas.db                       # Apuestas y juegos
│   ├── messages.db                       # Mensajería
│   └── votaciones.db                     # Votaciones
│
└── 📚 DOCUMENTACIÓN
    ├── ARQUITECTURA_SISTEMA.md           # Este archivo
    └── EJECUTA_ESTO.txt                  # Guía rápida
```

## 🚀 Uso del Sistema

### Inicio Rápido

```bash
# Opción 1: Menú interactivo
SISTEMA_COMPLETO.bat

# Opción 2: Reinicio rápido
REINICIAR_SISTEMA.bat

# Opción 3: Línea de comandos
python arquitectura_servidores.py start-all
```

### Comandos Principales

```bash
# Iniciar todos los servidores
python arquitectura_servidores.py start-all

# Detener todos los servidores
python arquitectura_servidores.py stop-all

# Ver estado
python arquitectura_servidores.py status

# Iniciar servidor específico
python arquitectura_servidores.py start bank
python arquitectura_servidores.py start exams

# Monitor automático (reinicia si falla)
python arquitectura_servidores.py monitor
```

## 🔧 Configuración de Servidores

### Archivo: `servers_config.json`

```json
{
  "servers": [
    {
      "name": "bank",
      "port": 8000,
      "module": "bank",
      "command": "python main.py",
      "health_check_url": "http://localhost:8000/health",
      "auto_restart": true,
      "max_retries": 3
    },
    {
      "name": "exams",
      "port": 8001,
      "module": "exams",
      "command": "python modules/exams/start_exams.py",
      "health_check_url": "http://localhost:8001/health",
      "auto_restart": true,
      "max_retries": 3
    }
  ]
}
```

### Añadir Nuevo Servidor

1. Edita `servers_config.json`
2. Añade nueva entrada con:
   - `name`: Nombre único
   - `port`: Puerto disponible
   - `module`: Módulo correspondiente
   - `command`: Comando para iniciar
   - `health_check_url`: URL de health check
3. Reinicia el sistema

## 🌐 URLs Disponibles

### Producción (Cloudflare Tunnel)

- **Principal**: https://dvta.ch
- **Bank**: https://bank.dvta.ch
- **Exams**: https://exams.dvta.ch
- **Games**: https://games.dvta.ch
- **Social**: https://social.dvta.ch
- **API**: https://api.dvta.ch

### Local (Desarrollo)

- **Bank**: http://localhost:8000
- **Exams**: http://localhost:8001
- **Games**: http://localhost:8002
- **Social**: http://localhost:8003

## 🏥 Health Checks

Cada servidor expone un endpoint `/health`:

```bash
# Verificar servidor Bank
curl http://localhost:8000/health

# Respuesta:
{
  "status": "healthy",
  "service": "dvdbank",
  "version": "4.0",
  "timestamp": "2026-05-27T20:00:00"
}
```

## 🔄 Flujo de Trabajo

### 1. Desarrollo

```bash
# Iniciar solo el servidor que necesitas
python arquitectura_servidores.py start bank

# Hacer cambios en el código
# ...

# Reiniciar servidor
python arquitectura_servidores.py restart bank
```

### 2. Producción

```bash
# Iniciar sistema completo
SISTEMA_COMPLETO.bat → Opción 12

# O usar el script rápido
REINICIAR_SISTEMA.bat
```

### 3. Monitoreo

```bash
# Iniciar monitor automático
python arquitectura_servidores.py monitor

# El monitor:
# - Verifica cada 30 segundos
# - Reinicia automáticamente si falla
# - Registra eventos
```

## 🛡️ Alta Disponibilidad

### Reinicio Automático

Si un servidor falla:
1. El monitor detecta el fallo (health check)
2. Intenta reiniciar automáticamente
3. Registra el evento
4. Notifica si falla después de max_retries

### Balanceo de Carga

Cloudflare Tunnel distribuye el tráfico:
- Cada subdominio apunta a su servidor
- Failover automático si un servidor cae
- Cache de Cloudflare reduce carga

## 📊 Monitoreo y Logs

### Ver Estado en Tiempo Real

```bash
python arquitectura_servidores.py status
```

Muestra:
- Estado de cada servidor (running/stopped/error)
- PID del proceso
- Puerto
- Salud (healthy/unhealthy)

### Logs

Los logs se guardan en:
- `logs/server.log` - Servidor principal
- `logs/tunnel.log` - Túnel Cloudflare
- `logs/monitor.log` - Monitor automático

## 🔐 Seguridad

- ✅ Túnel Cloudflare encriptado (TLS)
- ✅ Autenticación JWT
- ✅ Rate limiting
- ✅ CORS configurado
- ✅ Health checks protegidos

## 🚨 Solución de Problemas

### Servidor no inicia

```bash
# Ver logs
type logs\server.log

# Verificar puerto ocupado
netstat -ano | findstr ":8000"

# Matar proceso
taskkill /F /PID [PID]
```

### Túnel Cloudflare error 1033

```bash
# Reiniciar túnel
taskkill /F /IM cloudflared.exe
cloudflared.exe tunnel --config cloudflare-multi-server.yml run dvta-tunnel

# Verificar configuración
cloudflared.exe tunnel info dvta-tunnel
```

### Servidor no responde

```bash
# Verificar health check
curl http://localhost:8000/health

# Reiniciar servidor
python arquitectura_servidores.py restart bank
```

## 📈 Escalabilidad

### Añadir Más Servidores

1. Crea el nuevo módulo en `modules/`
2. Añade entrada en `servers_config.json`
3. Añade ruta en `cloudflare-multi-server.yml`
4. Reinicia el sistema

### Ejemplo: Añadir servidor "Admin"

```json
{
  "name": "admin",
  "port": 8004,
  "module": "admin",
  "command": "python modules/admin/start_admin.py",
  "health_check_url": "http://localhost:8004/health",
  "auto_restart": true
}
```

```yaml
# En cloudflare-multi-server.yml
- hostname: admin.dvta.ch
  service: http://localhost:8004
```

## 🎯 Mejores Prácticas

1. **Siempre usa el gestor de servidores** en lugar de iniciar manualmente
2. **Activa el monitor** en producción para reinicio automático
3. **Verifica health checks** antes de hacer deploy
4. **Usa subdominios** para cada módulo (mejor organización)
5. **Haz backups** de las bases de datos regularmente
6. **Monitorea logs** para detectar problemas temprano

## 📞 Soporte

Si tienes problemas:
1. Verifica el estado: `python arquitectura_servidores.py status`
2. Revisa los logs en `logs/`
3. Reinicia el sistema: `REINICIAR_SISTEMA.bat`
4. Consulta esta documentación

---

**Sistema creado**: 27 de mayo de 2026
**Versión**: 1.0
**Autor**: DVDBank Team
