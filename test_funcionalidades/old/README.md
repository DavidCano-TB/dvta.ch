# 🧪 Suite de Tests Funcionales - DVDcoin Bank

Suite completa de tests automatizados para verificar todas las funcionalidades del sistema DVDcoin Bank.

## 📋 Contenido

Esta suite incluye tests exhaustivos para:

1. **Autenticación y Sesiones** - Login, logout, tokens JWT, sesiones
2. **Transferencias** - Envío de DVDcoins, validaciones, historial
3. **OPO (Oposiciones)** - Sistema de oposiciones completo
4. **Millonario** - Juego del millonario
5. **Video (WebRTC)** - Videollamadas, conexiones, ICE candidates
6. **Cifras y Letras** - Juego de cifras y letras
7. **Pasapalabra** - Juego de pasapalabra
8. **Hundir la Flota** - Juego de hundir la flota
9. **Mensajes** - Sistema de mensajería
10. **Apuestas** - Sistema de apuestas y porras
11. **Votaciones** - Sistema de votaciones
12. **Cuentos** - Generación de cuentos con IA
13. **¿Quién Soy?** - Juego de adivinanzas
14. **Administración** - Panel de administración
15. **Galería** - Gestión de imágenes

## 🚀 Instalación

### 1. Instalar dependencias

```bash
INSTALAR_DEPENDENCIAS.bat
```

O manualmente:
```bash
python -m pip install websocket-client requests
```

### 2. Configurar credenciales

Edita `config.json` si es necesario. Por defecto usa:
- Admin: dvd / (password del archivo config/master.txt)
- Test users: test_user / test123, test_user2 / test123

### 3. Preparar tests

```bash
python PREPARAR_TESTS.py
```

Esto copia `test_utils.py` y `config.json` a cada carpeta de test.

## ▶️ Ejecución

### Ejecutar todos los tests

```bash
EJECUTAR_TODOS_LOS_TESTS.bat
```

O manualmente:
```bash
python RUN_ALL_TESTS.py
```

### Ejecutar un test individual

```bash
cd 01_transferencias
python test_transferencias.py
```

## 📊 Resultados

### Logs individuales

Cada test genera un log en su propia carpeta:
```
01_transferencias/test_transferencias_2026-05-11_17-44-29.log
```

### Resumen general

El script `RUN_ALL_TESTS.py` genera un resumen en:
```
logs/test_summary_2026-05-11_17-44-29.json
```

## 🔧 Estructura

```
test_funcionalidades/
├── config.json                    # Configuración global
├── test_utils.py                  # Utilidades compartidas
├── PREPARAR_TESTS.py             # Script de preparación
├── FIX_ALL_IMPORTS.py            # Script de corrección de imports
├── RUN_ALL_TESTS.py              # Ejecutor principal
├── EJECUTAR_TODOS_LOS_TESTS.bat # Batch para Windows
├── INSTALAR_DEPENDENCIAS.bat    # Instalar dependencias
│
├── 01_transferencias/
│   ├── test_transferencias.py
│   ├── test_utils.py (copia)
│   └── config.json (copia)
│
├── 02_opo/
│   ├── test_opo.py
│   ├── test_utils.py (copia)
│   └── config.json (copia)
│
└── ... (resto de carpetas)
```

## 📝 Características de los Tests

Cada test verifica:

✅ **Backend API**
- Endpoints REST
- Validaciones de datos
- Códigos de respuesta HTTP
- Estructura de JSON

✅ **Frontend**
- Páginas HTML accesibles
- JavaScript funcional
- Elementos DOM presentes

✅ **WebSockets**
- Conexión establecida
- Mensajes enviados/recibidos
- Eventos en tiempo real

✅ **Validaciones**
- Datos inválidos rechazados
- Permisos verificados
- Rate limiting activo

✅ **Flujos Completos**
- Casos de uso end-to-end
- Múltiples usuarios
- Escenarios reales

## 🛠️ Mantenimiento

### Actualizar configuración

Si cambias el servidor o credenciales:

1. Edita `config.json` en la raíz
2. Ejecuta `python PREPARAR_TESTS.py`

### Agregar nuevo test

1. Crea carpeta `XX_nombre/`
2. Crea `test_nombre.py` usando la plantilla
3. Agrega a la lista en `RUN_ALL_TESTS.py`
4. Ejecuta `python PREPARAR_TESTS.py`

### Plantilla de test

```python
#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: NOMBRE DEL TEST
"""
import sys
import os

# Importar desde directorio local primero
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_utils import TestLogger, TestClient, load_config, verify_response

def test_mi_funcionalidad():
    """Test completo de mi funcionalidad"""
    logger = TestLogger("mi_funcionalidad")
    config = load_config()
    
    base_url = config['server']['base_url']
    admin_creds = config['credentials']['admin']
    
    client = TestClient(base_url, logger)
    
    # 1. AUTENTICACIÓN
    logger.section("1. AUTENTICACIÓN")
    if not client.login(admin_creds['username'], admin_creds['password']):
        return logger.summary()
    
    # 2. TUS TESTS AQUÍ
    logger.section("2. PRUEBAS")
    
    # ... tu código ...
    
    # RESUMEN
    return logger.summary()

if __name__ == "__main__":
    success = test_mi_funcionalidad()
    sys.exit(0 if success else 1)
```

## ⚠️ Requisitos

- Python 3.7+
- Servidor DVDcoin Bank ejecutándose en `http://localhost:8000`
- Usuarios de prueba creados (test_user, test_user2)
- Dependencias instaladas (websocket-client, requests)

## 📞 Soporte

Si un test falla:

1. Revisa el log individual del test
2. Verifica que el servidor esté ejecutándose
3. Comprueba las credenciales en `config.json`
4. Asegúrate de que los usuarios de prueba existen
5. Revisa que todas las dependencias estén instaladas

## 🎯 Objetivos

Esta suite garantiza:

- ✅ Todas las funcionalidades operativas
- ✅ APIs respondiendo correctamente
- ✅ Frontend accesible y funcional
- ✅ WebSockets conectando
- ✅ Validaciones activas
- ✅ Flujos completos funcionando
- ✅ Regresiones detectadas temprano
