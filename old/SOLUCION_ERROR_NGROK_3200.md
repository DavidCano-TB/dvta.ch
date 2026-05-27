# Solución al Error ERR_NGROK_3200

## ¿Qué significa este error?

El error **ERR_NGROK_3200** indica que el endpoint de ngrok está **offline**, es decir:
- El servidor local no está corriendo, O
- Ngrok no está conectado al servidor, O
- El dominio reservado de ngrok expiró o cambió

## Solución Rápida (Recomendada)

### Opción 1: Script Automático
Ejecuta el script que acabamos de crear:

```bash
SOLUCIONAR_NGROK_AHORA.bat
```

Este script:
1. ✓ Detiene todos los procesos antiguos
2. ✓ Libera los puertos 8000 y 4040
3. ✓ Verifica la configuración de ngrok
4. ✓ Inicia el servidor y ngrok
5. ✓ Verifica que todo funcione
6. ✓ Abre el navegador con la URL pública

### Opción 2: Manual

1. **Detener todo:**
   ```bash
   taskkill /F /IM python.exe
   taskkill /F /IM ngrok.exe
   ```

2. **Iniciar el servidor:**
   ```bash
   python start.py
   ```

3. **Esperar 15-20 segundos** para que todo arranque

4. **Verificar que funciona:**
   - Servidor local: http://localhost:8000
   - Panel ngrok: http://localhost:4040
   - URL pública: https://unhidden-patient-cradling.ngrok-free.dev

## Diagnóstico de Problemas

Si la solución rápida no funciona, ejecuta:

```bash
DIAGNOSTICAR_Y_REPARAR_NGROK.bat
```

Este script te dirá exactamente qué está fallando.

## Problemas Comunes

### 1. Token de ngrok inválido o expirado

**Síntoma:** Ngrok no se conecta

**Solución:**
1. Ve a https://dashboard.ngrok.com/get-started/your-authtoken
2. Copia tu token
3. Edita `config/ngrok_config.txt`
4. Reemplaza el valor de `NGROK_TOKEN=` con tu token
5. Guarda y ejecuta `SOLUCIONAR_NGROK_AHORA.bat`

### 2. Dominio reservado expiró

**Síntoma:** Ngrok se conecta pero el dominio no responde

**Solución:**
1. Ve a https://dashboard.ngrok.com/cloud-edge/domains
2. Verifica que el dominio `unhidden-patient-cradling.ngrok-free.dev` esté activo
3. Si no existe o expiró, crea uno nuevo
4. Edita `config/ngrok_config.txt`
5. Actualiza `NGROK_DOMAIN=` con tu nuevo dominio
6. Ejecuta `SOLUCIONAR_NGROK_AHORA.bat`

### 3. Puerto 8000 ocupado

**Síntoma:** Error al iniciar el servidor

**Solución:**
```bash
# Liberar puerto 8000
for /f "tokens=5" %a in ('netstat -aon ^| findstr ":8000 "') do taskkill /PID %a /F
```

### 4. Firewall bloqueando ngrok

**Síntoma:** Ngrok no puede conectarse a internet

**Solución:**
1. Abre Windows Defender Firewall
2. Permite `ngrok.exe` en redes privadas y públicas
3. Reinicia ngrok

### 5. Servidor se cae inmediatamente

**Síntoma:** El servidor arranca pero se detiene enseguida

**Solución:**
1. Revisa `server.log` para ver el error
2. Verifica que todas las dependencias estén instaladas:
   ```bash
   pip install -r requirements.txt
   ```
3. Verifica que la base de datos exista:
   ```bash
   dir data\users.db
   ```

## Verificación Manual

### 1. Verificar servidor local
```bash
curl http://localhost:8000
```
Debería devolver HTML o JSON, no un error de conexión.

### 2. Verificar ngrok
```bash
curl http://localhost:4040/api/tunnels
```
Debería devolver JSON con información de los túneles.

### 3. Verificar dominio público
```bash
curl https://unhidden-patient-cradling.ngrok-free.dev
```
Debería devolver el mismo contenido que el servidor local.

## Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| `SOLUCIONAR_NGROK_AHORA.bat` | Solución automática completa |
| `DIAGNOSTICAR_Y_REPARAR_NGROK.bat` | Diagnóstico detallado |
| `REINICIAR_TODO.bat` | Reinicia todo el sistema |
| `python start.py` | Inicia servidor + ngrok manualmente |

## URLs Importantes

- **Panel de ngrok:** https://dashboard.ngrok.com
- **Obtener token:** https://dashboard.ngrok.com/get-started/your-authtoken
- **Dominios reservados:** https://dashboard.ngrok.com/cloud-edge/domains
- **Documentación ngrok:** https://ngrok.com/docs

## Logs para Revisar

Si algo falla, revisa estos archivos:
- `server.log` - Logs del servidor Python
- `ngrok_*.log` - Logs de ngrok
- `watchdog.log` - Logs del watchdog (si está activo)

## Contacto y Soporte

Si ninguna solución funciona:
1. Revisa los logs mencionados arriba
2. Verifica tu cuenta de ngrok en el dashboard
3. Asegúrate de tener la última versión de ngrok
4. Verifica que tu conexión a internet funcione correctamente

---

**Última actualización:** 2026-05-10
