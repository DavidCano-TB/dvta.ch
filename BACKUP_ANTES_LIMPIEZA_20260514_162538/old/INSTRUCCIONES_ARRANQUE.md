# 🚀 DVDcoin Bank - Sistema de Arranque Automático

## ✅ Estado Actual

La aplicación **YA ESTÁ FUNCIONANDO** y configurada para arrancar automáticamente con Windows.

### URLs Activas:
- **Local**: http://localhost:8000
- **Pública**: https://nonflying-unstiffened-oakley.ngrok-free.dev

---

## 📋 Scripts Disponibles

### 1. **ARRANCAR.bat** 
Inicia manualmente el servidor DVDcoin Bank + ngrok
- Usa este script si necesitas reiniciar la aplicación
- Abre automáticamente el navegador con la URL correcta

### 2. **VERIFICAR_ESTADO.bat** ⭐ NUEVO
Verifica si la aplicación está corriendo
- Comprueba el servidor local (puerto 8000)
- Comprueba ngrok (puerto 4040)
- Muestra las URLs disponibles
- Verifica si el arranque automático está instalado

### 3. **install_autostart.bat** ✅ YA EJECUTADO
Instala el arranque automático con Windows
- Crea un acceso directo en la carpeta de inicio
- La aplicación se iniciará automáticamente al encender el PC
- **YA ESTÁ INSTALADO Y FUNCIONANDO**

### 4. **uninstall_autostart.bat**
Desinstala el arranque automático
- Elimina el acceso directo de la carpeta de inicio
- Usa esto si NO quieres que la app arranque con Windows

---

## 🔧 Cómo Funciona el Arranque Automático

1. **start_dvdcoin_hidden.vbs**: Script invisible que ejecuta Python sin mostrar ventanas
2. **Acceso directo en Startup**: Windows ejecuta el VBS al iniciar sesión
3. **src/start.py**: Script Python que:
   - Verifica dependencias
   - Libera el puerto 8000 si está ocupado
   - Inicia el servidor FastAPI
   - Configura y arranca ngrok con el dominio reservado
   - Mantiene todo corriendo en segundo plano

---

## 🛠️ Solución de Problemas

### La aplicación no arrancó con Windows
1. Ejecuta **VERIFICAR_ESTADO.bat** para ver qué falla
2. Si el arranque automático no está instalado, ejecuta **install_autostart.bat**
3. Reinicia Windows para probar

### Error "endpoint is offline" en ngrok
**SOLUCIONADO**: El script ahora:
- Usa el dominio reservado: `nonflying-unstiffened-oakley.ngrok-free.dev`
- Si el dominio falla, usa una URL aleatoria automáticamente
- Configura el token de ngrok correctamente

### El servidor no responde
1. Ejecuta **VERIFICAR_ESTADO.bat**
2. Si no está corriendo, ejecuta **ARRANCAR.bat**
3. Revisa los logs: `server.log` y `ngrok.log`

### Quiero ver las ventanas de consola
- Ejecuta **ARRANCAR.bat** manualmente
- El arranque automático usa ventanas ocultas para no molestar

---

## 📁 Ubicación del Arranque Automático

El acceso directo está en:
```
C:\Users\[TU_USUARIO]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\DVDcoin Bank.lnk
```

Puedes acceder rápidamente presionando:
- `Win + R`
- Escribe: `shell:startup`
- Enter

---

## 🎯 Próximos Pasos

1. **Reinicia Windows** para probar el arranque automático
2. Después del reinicio, ejecuta **VERIFICAR_ESTADO.bat** para confirmar
3. Si todo funciona, ¡ya no necesitas hacer nada más!

---

## 📝 Notas Técnicas

- **Puerto local**: 8000
- **Puerto ngrok API**: 4040
- **Dominio ngrok**: nonflying-unstiffened-oakley.ngrok-free.dev
- **Token ngrok**: Configurado en `config/.ngrok_token`
- **Logs**: `server.log` y `ngrok_*.log`

---

## ❓ Comandos Útiles

```bash
# Ver procesos de Python corriendo
tasklist | findstr python

# Ver qué está usando el puerto 8000
netstat -ano | findstr :8000

# Matar proceso por PID (si es necesario)
taskkill /PID [numero] /F
```

---

**✅ TODO CONFIGURADO Y FUNCIONANDO**

La aplicación está corriendo ahora y se iniciará automáticamente cada vez que arranques Windows.
