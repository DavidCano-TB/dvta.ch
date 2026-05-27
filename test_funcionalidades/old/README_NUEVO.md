# 🧪 Suite de Tests Funcionales - DVDcoin Bank

Esta carpeta contiene scripts de prueba exhaustivos para cada funcionalidad de la aplicación.

## 🚀 INICIO RÁPIDO

### Primera vez (Setup completo):
```bash
SETUP_COMPLETO.bat
```

O manualmente:
```bash
1. PREPARAR_TESTS.bat          # Copiar archivos necesarios
2. INSTALAR_DEPENDENCIAS.bat   # Instalar Python packages
3. Editar config.json           # Configurar credenciales
4. EJECUTAR_TODOS_LOS_TESTS.bat # Ejecutar tests
```

### Ejecuciones posteriores:
```bash
EJECUTAR_TODOS_LOS_TESTS.bat
```

## 📁 Estructura

Cada carpeta contiene:
- `test_[funcionalidad].py` - Script de prueba principal
- `test_utils.py` - Utilidades (copiado automáticamente)
- `config.json` - Configuración (copiado automáticamente)
- `EJECUTAR_TEST.bat` - Ejecutor individual
- `test_[funcionalidad]_[timestamp].log` - Logs generados

## 📊 Logs

Los logs se generan automáticamente en la misma carpeta del test:
- Formato: `test_[funcionalidad]_YYYY-MM-DD_HH-MM-SS.log`
- Incluyen: timestamps, éxitos ✅, fallos ❌, advertencias ⚠️, resumen 📊

## 🔧 Configuración

Edita `config.json` (se copia automáticamente a cada carpeta):

```json
{
  "server": {
    "base_url": "http://localhost:8000",
    "ws_url": "ws://localhost:8000",
    "timeout": 30
  },
  "credentials": {
    "admin": {
      "username": "dvd",
      "password": "tu_password_admin"
    },
    "test_user": {
      "username": "test_user",
      "password": "test123"
    },
    "test_user2": {
      "username": "test_user2",
      "password": "test123"
    }
  }
}
```

## 📋 Funcionalidades Testeadas (15 módulos)

1. **Autenticación y Sesiones** - Login, tokens JWT, refresh, cambio de contraseña
2. **Transferencias** - Sistema de transacciones DVDcoin
3. **OPO** - Sistema de oposiciones
4. **Millonario** - Juego ¿Quién quiere ser millonario?
5. **Video** - Sistema de videollamadas WebRTC
6. **Cifras y Letras** - Juego Cifras y Letras
7. **Pasapalabra** - Juego Pasapalabra
8. **Hundir la Flota** - Juego naval
9. **Mensajes** - Sistema de mensajería
10. **Apuestas** - Sistema de apuestas y porras
11. **Votaciones** - Sistema de votaciones
12. **Cuentos** - Gestión de historias
13. **¿Quién Soy?** - Juego de adivinanzas con IA
14. **Administración** - Panel de administración completo
15. **Galería** - Sistema de imágenes

## 🎯 Cobertura

Cada test verifica:
- ✅ Endpoints de API (GET, POST, PUT, DELETE)
- ✅ WebSockets y comunicación en tiempo real
- ✅ Autenticación y autorización
- ✅ Validación de datos
- ✅ Manejo de errores
- ✅ Flujos completos de usuario
- ✅ Integración frontend-backend

## 📚 Documentación

- `INICIO_RAPIDO.md` - Guía de inicio rápido
- `INSTRUCCIONES.md` - Instrucciones detalladas
- `RESUMEN_COMPLETO.md` - Documentación exhaustiva
- `README_NUEVO.md` - Este archivo

## 🔍 Scripts Útiles

- `SETUP_COMPLETO.bat` - Setup automático completo
- `PREPARAR_TESTS.bat` - Copiar archivos necesarios
- `INSTALAR_DEPENDENCIAS.bat` - Instalar packages Python
- `VERIFICAR_CONFIGURACION.bat` - Verificar que todo está listo
- `EJECUTAR_TODOS_LOS_TESTS.bat` - Ejecutar todos los tests

## ⚠️ IMPORTANTE

**Antes de ejecutar los tests por primera vez:**
1. Ejecuta `PREPARAR_TESTS.bat` para copiar archivos necesarios
2. Edita `config.json` con tus credenciales
3. Asegúrate de que el servidor esté corriendo

## 🐛 Solución de Problemas

### Error: "No module named 'test_utils'"
**Solución:** Ejecuta `PREPARAR_TESTS.bat`

### Error: "No se pudo conectar al servidor"
**Solución:** Inicia el servidor con `ARRANCAR.bat`

### Error: "Login fallido"
**Solución:** Verifica las credenciales en `config.json`

### Error: "ModuleNotFoundError"
**Solución:** Ejecuta `INSTALAR_DEPENDENCIAS.bat`

## 📞 Soporte

Si encuentras problemas:
1. Ejecuta `VERIFICAR_CONFIGURACION.bat`
2. Revisa los logs en cada carpeta de test
3. Consulta `INSTRUCCIONES.md` para más detalles

---

**✅ TODO CORREGIDO Y FUNCIONANDO**

Los archivos necesarios se copian automáticamente a cada carpeta con `PREPARAR_TESTS.bat`.
