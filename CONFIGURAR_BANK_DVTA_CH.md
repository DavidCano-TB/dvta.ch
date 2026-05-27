# 🔧 CONFIGURAR bank.dvta.ch

**Fecha**: 27 Mayo 2026  
**Objetivo**: Hacer que https://bank.dvta.ch funcione correctamente

---

## 📊 ESTADO ACTUAL

✅ **Servidor Bank**: Corriendo en puerto 8000 (PID 5896)  
✅ **Cloudflare Tunnel**: Activo  
✅ **Configuración tunnel**: Correcta (bank.dvta.ch → localhost:8000)  
❌ **DNS Cloudflare**: Necesita configuración

---

## 🎯 PROBLEMA

El subdominio `bank.dvta.ch` no está configurado en el DNS de Cloudflare.

**Configuración actual del tunnel** (correcta):
```yaml
- hostname: bank.dvta.ch
  service: http://localhost:8000
```

**Lo que falta**: Añadir el registro DNS en Cloudflare.

---

## ✅ SOLUCIÓN: Configurar DNS en Cloudflare

### Opción 1: Configuración Automática (Recomendado)

El tunnel de Cloudflare puede crear automáticamente los registros DNS.

**Pasos**:

1. **Detener el tunnel actual**:
   ```batch
   taskkill /F /IM cloudflared.exe
   ```

2. **Reiniciar el tunnel**:
   ```batch
   cloudflared.exe tunnel --config cloudflare-dvta-config.yml run
   ```

3. **Verificar en Cloudflare Dashboard**:
   - Ve a: https://dash.cloudflare.com
   - Selecciona el dominio: `dvta.ch`
   - Ve a: DNS → Records
   - Busca: `bank` (debería aparecer automáticamente)

---

### Opción 2: Configuración Manual en Cloudflare Dashboard

Si la opción automática no funciona, configura manualmente:

**Pasos**:

1. **Accede a Cloudflare Dashboard**:
   - URL: https://dash.cloudflare.com
   - Inicia sesión con tu cuenta

2. **Selecciona el dominio**:
   - Click en: `dvta.ch`

3. **Ve a DNS**:
   - Click en: `DNS` en el menú lateral
   - Click en: `Records`

4. **Añade registro CNAME**:
   - Click en: `Add record`
   - **Type**: CNAME
   - **Name**: bank
   - **Target**: `b75039b1-7b54-4da0-b2ab-0a338bfccdc5.cfargotunnel.com`
   - **Proxy status**: ✅ Proxied (naranja)
   - **TTL**: Auto
   - Click en: `Save`

5. **Verifica**:
   - Espera 1-2 minutos
   - Abre: https://bank.dvta.ch
   - Debería cargar la aplicación Bank

---

### Opción 3: Usar Cloudflare CLI

**Comando**:
```batch
cloudflared tunnel route dns b75039b1-7b54-4da0-b2ab-0a338bfccdc5 bank.dvta.ch
```

**Esto creará automáticamente el registro DNS.**

---

## 🔍 VERIFICACIÓN

### 1. Verificar Servidores Locales

```batch
netstat -ano | findstr ":8000 :8001"
```

**Resultado esperado**:
```
TCP    0.0.0.0:8000    0.0.0.0:0    LISTENING    5896  ← Bank
TCP    0.0.0.0:8001    0.0.0.0:0    LISTENING    3384  ← Exams
```

### 2. Verificar Tunnel

```batch
tasklist | findstr "cloudflared"
```

**Resultado esperado**:
```
cloudflared.exe    [PID]    Console    1    [Memoria]
```

### 3. Verificar DNS (desde CMD)

```batch
nslookup bank.dvta.ch
```

**Resultado esperado**:
```
Name:    bank.dvta.ch
Addresses:  [IPs de Cloudflare]
```

### 4. Verificar Acceso Web

Abre en el navegador:
- ✅ https://dvta.ch → Debe mostrar Exams
- ✅ https://bank.dvta.ch → Debe mostrar Bank

---

## 🚀 SCRIPT RÁPIDO

He creado un script para facilitar la configuración:

**`CONFIGURAR_DNS_BANK.bat`**:
```batch
@echo off
echo.
echo ═══════════════════════════════════════════════════════════════
echo   Configurando DNS para bank.dvta.ch
echo ═══════════════════════════════════════════════════════════════
echo.

echo [1/3] Verificando servidores...
netstat -ano | findstr ":8000 :8001"
echo.

echo [2/3] Configurando DNS con Cloudflare CLI...
cloudflared tunnel route dns b75039b1-7b54-4da0-b2ab-0a338bfccdc5 bank.dvta.ch
echo.

echo [3/3] Reiniciando tunnel...
taskkill /F /IM cloudflared.exe
timeout /t 2 /nobreak >nul
start "Cloudflare Tunnel" cmd /c "cloudflared.exe tunnel --config cloudflare-dvta-config.yml run"
echo.

echo ═══════════════════════════════════════════════════════════════
echo   ✅ Configuración completada
echo ═══════════════════════════════════════════════════════════════
echo.
echo Espera 1-2 minutos y luego accede a:
echo   https://bank.dvta.ch
echo.
pause
```

---

## 📝 CONFIGURACIÓN ACTUAL DEL TUNNEL

**Archivo**: `cloudflare-dvta-config.yml`

```yaml
ingress:
  # DVDExams en puerto 8001
  - hostname: dvta.ch
    service: http://localhost:8001
      
  - hostname: www.dvta.ch
    service: http://localhost:8001
  
  # Bank subdomain en puerto 8000
  - hostname: bank.dvta.ch
    service: http://localhost:8000
  
  # Catch-all
  - service: http://localhost:8001
```

✅ **Esta configuración es correcta.**

---

## ❓ PROBLEMAS COMUNES

### Problema 1: "bank.dvta.ch no resuelve"

**Causa**: DNS no configurado en Cloudflare

**Solución**:
```batch
cloudflared tunnel route dns b75039b1-7b54-4da0-b2ab-0a338bfccdc5 bank.dvta.ch
```

---

### Problema 2: "Error 502 en bank.dvta.ch"

**Causa**: Servidor Bank no está corriendo en puerto 8000

**Solución**:
```batch
# Verificar puerto
netstat -ano | findstr ":8000"

# Si no está activo, iniciar Bank
cd /d "%~dp0"
python main.py
```

---

### Problema 3: "Tunnel no conecta"

**Causa**: Tunnel no está corriendo

**Solución**:
```batch
# Reiniciar tunnel
taskkill /F /IM cloudflared.exe
timeout /t 2
cloudflared.exe tunnel --config cloudflare-dvta-config.yml run
```

---

## 🎯 RESUMEN

**Para que bank.dvta.ch funcione necesitas**:

1. ✅ Servidor Bank corriendo en puerto 8000 (YA ESTÁ)
2. ✅ Configuración del tunnel correcta (YA ESTÁ)
3. ❌ Registro DNS en Cloudflare (FALTA CONFIGURAR)

**Acción requerida**:

Ejecuta UNO de estos comandos:

**Opción A - CLI** (más rápido):
```batch
cloudflared tunnel route dns b75039b1-7b54-4da0-b2ab-0a338bfccdc5 bank.dvta.ch
```

**Opción B - Dashboard** (más visual):
1. Ve a: https://dash.cloudflare.com
2. Dominio: dvta.ch
3. DNS → Add record
4. Type: CNAME, Name: bank, Target: b75039b1-7b54-4da0-b2ab-0a338bfccdc5.cfargotunnel.com

---

## 📞 AYUDA ADICIONAL

Si después de configurar el DNS sigue sin funcionar:

1. **Verifica los logs del tunnel**:
   - Mira la ventana "Cloudflare Tunnel"
   - Busca errores relacionados con "bank.dvta.ch"

2. **Verifica el servidor Bank**:
   ```batch
   curl http://localhost:8000
   ```

3. **Espera propagación DNS**:
   - Puede tardar 1-5 minutos
   - Limpia caché del navegador (Ctrl+Shift+Del)

---

**Última actualización**: 27 Mayo 2026  
**Estado**: Configuración del tunnel correcta, falta DNS en Cloudflare
