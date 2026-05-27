# 🌐 dvta.ch - Guía Completa

## ❌ Error 1033 - Solución

### Causa
El Error 1033 significa que Cloudflare Tunnel está activo pero el servidor local no responde.

### Solución Rápida
```bash
ARREGLAR_DVTA_AHORA.bat
```

Este script:
1. Detiene el tunnel anterior
2. Verifica dependencias
3. Inicia servidor Exams (puerto 8001)
4. Reinicia Cloudflare Tunnel
5. Verifica que todo funcione

---

## 🚀 Arranque Normal

### Opción 1: Script Automático (Recomendado)
```bash
ARRANCAR_DVTA_COMPLETO.bat
```

### Opción 2: Manual
```bash
# 1. Iniciar servidor Exams
cd modules\exams
python app_exams.py

# 2. Iniciar tunnel (en otra ventana)
cloudflared tunnel --config cloudflare-dvta-config.yml run
```

---

## 📊 Verificación

### Verificar que todo funciona
```bash
DIAGNOSTICO_COMPLETO.bat
```

### Verificar manualmente

**1. Servidor local**
```bash
curl http://localhost:8001
```
Debería responder con HTML

**2. Procesos corriendo**
```bash
tasklist | findstr "python.exe"
tasklist | findstr "cloudflared.exe"
```
Ambos deberían aparecer

**3. Puerto 8001**
```bash
netstat -ano | findstr ":8001"
```
Debería mostrar LISTENING

**4. Acceso externo**
Abre https://dvta.ch en el navegador

---

## 🔧 Configuración

### Archivo: `cloudflare-dvta-config.yml`

```yaml
tunnel: b75039b1-7b54-4da0-b2ab-0a338bfccdc5
credentials-file: C:\Users\PC\.cloudflared\b75039b1-7b54-4da0-b2ab-0a338bfccdc5.json

ingress:
  # DVDExams en puerto 8001
  - hostname: dvta.ch
    service: http://localhost:8001
  - hostname: www.dvta.ch
    service: http://localhost:8001
  
  # Bank en puerto 8000 (opcional)
  - hostname: dvta.ch
    path: /bank/*
    service: http://localhost:8000
  
  # Catch-all
  - service: http_status:404
```

### Rutas

- `https://dvta.ch` → Exams (puerto 8001)
- `https://dvta.ch/bank/*` → Bank (puerto 8000)
- `http://localhost:8001` → Exams local
- `http://localhost:8000` → Bank local

---

## 🛑 Detener Servicios

### Opción 1: Cerrar ventanas
Cierra las ventanas de:
- "DVDExams Server"
- "Cloudflare Tunnel - dvta.ch"

### Opción 2: Comando
```bash
taskkill /F /IM python.exe
taskkill /F /IM cloudflared.exe
```

---

## ⚠️ Problemas Comunes

### Error 1033
**Causa**: Servidor Exams no está corriendo
**Solución**: `ARREGLAR_DVTA_AHORA.bat`

### Puerto 8001 ocupado
**Causa**: Otro proceso usando el puerto
**Solución**: 
```bash
netstat -ano | findstr ":8001"
taskkill /F /PID [número_del_proceso]
```

### Dependencias faltantes
**Causa**: FastAPI u otras librerías no instaladas
**Solución**:
```bash
cd modules\exams
pip install -r requirements.txt
```

### Tunnel no conecta
**Causa**: Credenciales inválidas o tunnel no autorizado
**Solución**: Verificar que el archivo de credenciales existe:
```bash
dir C:\Users\PC\.cloudflared\b75039b1-7b54-4da0-b2ab-0a338bfccdc5.json
```

---

## 📦 Dependencias

### Python
- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- bcrypt
- python-jose

### Instalar
```bash
cd modules\exams
pip install -r requirements.txt
```

### Cloudflare
- cloudflared.exe
- Credenciales del tunnel

---

## 🔄 Actualizar

### Después de git pull
```bash
# 1. Detener servicios
taskkill /F /IM python.exe
taskkill /F /IM cloudflared.exe

# 2. Actualizar dependencias (si hay cambios)
cd modules\exams
pip install -r requirements.txt
cd ..\..

# 3. Reiniciar
ARRANCAR_DVTA_COMPLETO.bat
```

---

## 📞 Ayuda

### Scripts Útiles
- `ARREGLAR_DVTA_AHORA.bat` - Solución rápida Error 1033
- `ARRANCAR_DVTA_COMPLETO.bat` - Arranque completo
- `DIAGNOSTICO_COMPLETO.bat` - Diagnóstico completo
- `SOLUCIONAR_TUNNEL_DVTA.bat` - Solución guiada
- `SOLUCION_RAPIDA_DVTA.txt` - Guía de solución

### Documentación
- `modules/exams/README.md` - Documentación del módulo Exams
- `RESUMEN_FINAL_SISTEMA.md` - Resumen del sistema completo
- `GUIA_RAPIDA_ARRANQUE.md` - Guía general de arranque

---

## ✅ Checklist

Antes de que dvta.ch funcione:

- [ ] Python 3.11+ instalado
- [ ] Dependencias instaladas (`pip install -r modules/exams/requirements.txt`)
- [ ] Servidor Exams corriendo en puerto 8001
- [ ] Cloudflare Tunnel corriendo
- [ ] Credenciales de Cloudflare válidas
- [ ] Firewall permite conexiones (si aplica)

---

**Última actualización**: 27 Mayo 2026
**Versión**: 2.0
**Dominio**: dvta.ch
**Puerto**: 8001
**Servicio**: DVDcoin Exams
