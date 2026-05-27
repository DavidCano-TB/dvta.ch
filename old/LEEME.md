# 🏦 DVDcoin Bank - Guía de Inicio Rápido

## 🚀 Inicio Rápido (3 pasos)

### 1️⃣ Instalar Dependencias (solo la primera vez)

```batch
INSTALAR_DEPENDENCIAS.bat
```

### 2️⃣ Probar el Sistema

```batch
PRUEBA_COMPLETA.bat
```

### 3️⃣ Iniciar el Servidor

**Opción A - Con acceso remoto (ngrok):**
```batch
ARRANQUE_AUTOMATICO_COMPLETO.bat
```

**Opción B - Solo local:**
```batch
ARRANCAR.bat
```

## 📁 Scripts Disponibles

| Script | Descripción | Cuándo Usar |
|--------|-------------|-------------|
| `ARRANCAR.bat` | Inicia solo el servidor local | Desarrollo y pruebas locales |
| `ARRANQUE_AUTOMATICO_COMPLETO.bat` | Inicia servidor + ngrok | Acceso remoto rápido |
| `ADMIN_INICIAR_NGROK.bat` | Inicia ngrok (requiere admin) | Si el servidor ya está corriendo |
| `VERIFICAR_SERVIDOR.bat` | Verifica estado del sistema | Diagnóstico de problemas |
| `DETENER_TODO.bat` | Detiene todos los servicios | Antes de reiniciar |
| `INSTALAR_DEPENDENCIAS.bat` | Instala Python packages | Primera instalación |
| `PRUEBA_COMPLETA.bat` | Verifica todo el sistema | Antes de iniciar |

## 🔧 Solución de Problemas

### ❌ Error: ERR_NGROK_8012

**Solución:**
```batch
DETENER_TODO.bat
ARRANQUE_AUTOMATICO_COMPLETO.bat
```

Lee el archivo `SOLUCION_ERROR_NGROK.md` para más detalles.

### ❌ Error: "uvicorn no está instalado"

**Solución:**
```batch
INSTALAR_DEPENDENCIAS.bat
```

### ❌ Error: "Puerto 8000 ocupado"

**Solución:**
```batch
DETENER_TODO.bat
```

### ❌ Error: "Python no encontrado"

**Solución:**
1. Instala Python desde https://www.python.org/
2. Durante la instalación, marca "Add Python to PATH"
3. Reinicia la terminal

## 🌐 URLs del Sistema

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Servidor Local | http://localhost:8000 | Acceso local |
| Panel Ngrok | http://localhost:4040 | Panel de control de ngrok |
| OPO Local | http://localhost:8000/opo | Juego OPO local |
| URL Pública | Ver `ngrok_url.txt` | Acceso desde internet |

## 📚 Documentación Adicional

- `INSTRUCCIONES_ARRANQUE.txt` - Guía detallada de arranque
- `SOLUCION_ERROR_NGROK.md` - Solución al error ERR_NGROK_8012
- `requirements.txt` - Lista de dependencias Python

## 🔐 Usuarios por Defecto

Los usuarios administradores están definidos en el código:
- Superadmins: `dvd`, `nebulosa`
- Admins: `nina`, `victor`, `yu`, `roy`, `admin`, `aitor`

## 🎮 Características

- 🏦 Sistema bancario virtual (DVDcoin)
- 💸 Transferencias entre usuarios
- 🎯 Juegos (OPO, Pasapalabra, Millonario, etc.)
- 🎲 Sistema de apuestas (porras)
- 💬 Mensajería entre usuarios
- 📊 Estadísticas y rankings
- 🎨 Galería de imágenes
- 🗳️ Sistema de votaciones
- 📖 Cuentos interactivos
- 🎥 Videollamadas (en desarrollo)

## 🛠️ Tecnologías

- **Backend:** Python + FastAPI + Uvicorn
- **Base de Datos:** SQLite (5 archivos separados)
- **Autenticación:** JWT + bcrypt
- **WebSockets:** Para tiempo real
- **Túnel Público:** ngrok

## 📝 Notas Importantes

1. **Primera vez:** Ejecuta `INSTALAR_DEPENDENCIAS.bat` antes de iniciar
2. **Ngrok gratuito:** La URL pública cambia cada vez que reinicias ngrok
3. **Puerto 8000:** Asegúrate de que esté libre antes de iniciar
4. **Bases de datos:** Se crean automáticamente en `src/data/`
5. **Logs:** Los logs de ngrok se guardan en `ngrok.log`

## 🆘 Ayuda

Si tienes problemas:

1. Ejecuta `PRUEBA_COMPLETA.bat` para diagnosticar
2. Ejecuta `VERIFICAR_SERVIDOR.bat` para ver el estado
3. Lee `SOLUCION_ERROR_NGROK.md` si aparece error de ngrok
4. Ejecuta `DETENER_TODO.bat` y vuelve a intentar

## 📞 Contacto

Para soporte o preguntas, contacta al administrador del sistema.

---

**Versión:** 4.0  
**Última actualización:** 14 de mayo de 2026  
**Estado:** ✅ Funcionando correctamente
