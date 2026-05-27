# DVDBank - Sistema de Gestión

Sistema web de gestión bancaria con túnel Cloudflare.

## 🚀 Inicio Rápido

```cmd
INICIAR_DVDBANK_DVTA.bat
```

## 🌐 Acceso

- **Público:** https://dvta.ch
- **Público:** https://www.dvta.ch  
- **Local:** http://localhost:8000

## ⚙️ Configuración

**Túnel Cloudflare:**
- Nombre: `dvta-tunnel`
- ID: `b75039b1-7b54-4da0-b2ab-0a338bfccdc5`
- Configuración: `cloudflare-dvta-config.yml`

**Inicio automático con Windows:**
```cmd
CONFIGURAR_INICIO_AUTOMATICO_COMPLETO.bat
```

## 📊 Estado del Sistema

```cmd
ESTADO_RAPIDO.bat
```

## 📖 Documentación

- `RESUMEN_CONFIGURACION_COMPLETADA.txt` - Configuración completa
- `PASOS_SIMPLES_ACTIVAR_DVTA_CH.txt` - Guía de activación
- `GUIA_COMPLETA_DNS_DVTA_CH.txt` - Guía DNS detallada

## 🔧 Comandos Útiles

**Ver logs:**
```cmd
type logs\server.log
type logs\tunnel.log
```

**Detener sistema:**
```cmd
taskkill /F /IM python.exe
taskkill /F /IM cloudflared.exe
```

**Verificar túnel:**
```cmd
cloudflared.exe tunnel list
cloudflared.exe tunnel info dvta-tunnel
```
