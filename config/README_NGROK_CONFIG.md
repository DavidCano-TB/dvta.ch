# 🔧 Configuración de ngrok - DVDcoin Bank

## 📄 Archivo de Configuración: `ngrok_config.txt`

Este archivo centraliza la configuración de ngrok para facilitar cambios futuros.

### 📍 Ubicación
```
config/ngrok_config.txt
```

### 📝 Formato del Archivo

```ini
# Configuración de ngrok para DVDcoin Bank
# Este archivo contiene el token y dominio reservado de ngrok
# Formato: VARIABLE=valor (sin espacios alrededor del =)

NGROK_TOKEN=tu_token_aqui
NGROK_DOMAIN=tu-dominio.ngrok-free.dev
```

### ⚙️ Variables Disponibles

#### `NGROK_TOKEN` (Requerido)
- **Descripción**: Token de autenticación de ngrok
- **Dónde obtenerlo**: https://dashboard.ngrok.com/get-started/your-authtoken
- **Ejemplo**: `NGROK_TOKEN=3AqlNjjWKOeqmIGjN1Gu4Dnqm5d_28Hfykvwy45AXCe8gUHGz`

#### `NGROK_DOMAIN` (Opcional)
- **Descripción**: Dominio reservado de ngrok (si tienes uno)
- **Dónde obtenerlo**: https://dashboard.ngrok.com/cloud-edge/domains
- **Ejemplo**: `NGROK_DOMAIN=premium-size-unreached.ngrok-free.dev`
- **Nota**: Si no se especifica, ngrok usará una URL aleatoria

---

## 🔄 Cómo Cambiar la Configuración

### Método 1: Editar el archivo directamente

1. Abre `config/ngrok_config.txt` con un editor de texto
2. Modifica las variables que necesites:
   ```ini
   NGROK_TOKEN=nuevo_token_aqui
   NGROK_DOMAIN=nuevo-dominio.ngrok-free.dev
   ```
3. Guarda el archivo
4. Reinicia el servidor:
   - Detén el proceso actual (Ctrl+C si está en ventana visible)
   - Ejecuta `ARRANCAR.bat` o reinicia Windows

### Método 2: Reemplazar el archivo completo

1. Crea un nuevo archivo con el formato correcto
2. Reemplaza `config/ngrok_config.txt`
3. Reinicia el servidor

---

## 🔒 Seguridad

### ⚠️ IMPORTANTE: Este archivo contiene información sensible

- ✅ El archivo está en `.gitignore` (no se sube a Git)
- ✅ Mantén tu token privado
- ✅ No compartas este archivo públicamente
- ✅ No lo incluyas en capturas de pantalla

### 🔐 Archivos Protegidos

Los siguientes archivos están excluidos de Git:
```
config/ngrok_config.txt
config/.ngrok_token
config/jwt_secret.txt
config/master.txt
```

---

## 🏗️ Arquitectura del Sistema

### Orden de Prioridad para Cargar Configuración

El sistema busca la configuración en este orden:

1. **`config/ngrok_config.txt`** ⭐ (Recomendado)
   - Archivo centralizado con token y dominio
   - Fácil de editar y mantener

2. **`config/.ngrok_token`** (Fallback)
   - Solo contiene el token
   - Usado si ngrok_config.txt no existe o está vacío

3. **`config/deploy.env`** (Fallback)
   - Archivo de variables de entorno
   - Busca línea `NGROK_TOKEN=...`

4. **Variable de entorno `NGROK_TOKEN`** (Fallback)
   - Variable del sistema operativo
   - Última opción

### 📂 Estructura de Archivos

```
dvdcoin/
├── config/
│   ├── ngrok_config.txt          ← Configuración principal ⭐
│   ├── .ngrok_token              ← Fallback (legacy)
│   ├── jwt_secret.txt            ← Secret para JWT
│   ├── master.txt                ← Password de emergencia
│   └── README_NGROK_CONFIG.md    ← Esta documentación
├── src/
│   └── start.py                  ← Lee ngrok_config.txt
└── .gitignore                    ← Protege archivos sensibles
```

---

## 🧪 Verificación

### Comprobar que la configuración se carga correctamente

1. Ejecuta `ARRANCAR.bat`
2. Busca en la salida:
   ```
   ✓  ngrok encontrado
      Usando dominio reservado: tu-dominio.ngrok-free.dev
      Intentando conectar con dominio reservado...
   ```
3. Si ves tu dominio, ¡la configuración se cargó correctamente!

### Probar sin dominio reservado

1. Comenta o elimina la línea `NGROK_DOMAIN=...` en `ngrok_config.txt`:
   ```ini
   NGROK_TOKEN=tu_token_aqui
   # NGROK_DOMAIN=tu-dominio.ngrok-free.dev
   ```
2. Reinicia el servidor
3. Verás:
   ```
   Sin dominio reservado, usando URL aleatoria...
   ```

---

## 🐛 Solución de Problemas

### Error: "Sin token ngrok — solo acceso local"

**Causa**: El archivo `ngrok_config.txt` no existe o está vacío

**Solución**:
1. Verifica que existe: `config/ngrok_config.txt`
2. Verifica que contiene: `NGROK_TOKEN=tu_token_aqui`
3. Verifica que no hay espacios extra alrededor del `=`

### Error: "Dominio reservado no disponible"

**Causa**: El dominio especificado no es válido o no está asociado a tu cuenta

**Solución**:
1. Verifica el dominio en: https://dashboard.ngrok.com/cloud-edge/domains
2. Copia el dominio exacto (sin `https://`)
3. Actualiza `NGROK_DOMAIN=` en `ngrok_config.txt`
4. O comenta la línea para usar URL aleatoria

### El sistema usa URL aleatoria en lugar del dominio

**Causa**: El dominio no se pudo conectar (puede estar en uso o ser inválido)

**Comportamiento**: El sistema automáticamente hace fallback a URL aleatoria

**Solución**: Esto es normal y el sistema seguirá funcionando. Si quieres usar el dominio reservado:
1. Verifica que el dominio es correcto
2. Asegúrate de que no hay otra instancia de ngrok usando ese dominio
3. Reinicia el servidor

---

## 📚 Ejemplos

### Ejemplo 1: Configuración Completa (con dominio reservado)

```ini
# Configuración de ngrok para DVDcoin Bank
NGROK_TOKEN=3AqlNjjWKOeqmIGjN1Gu4Dnqm5d_28Hfykvwy45AXCe8gUHGz
NGROK_DOMAIN=premium-size-unreached.ngrok-free.dev
```

**Resultado**: Usará el dominio reservado

### Ejemplo 2: Solo Token (sin dominio reservado)

```ini
# Configuración de ngrok para DVDcoin Bank
NGROK_TOKEN=3AqlNjjWKOeqmIGjN1Gu4Dnqm5d_28Hfykvwy45AXCe8gUHGz
```

**Resultado**: Usará una URL aleatoria de ngrok

### Ejemplo 3: Con Comentarios

```ini
# Configuración de ngrok para DVDcoin Bank
# Token obtenido de: https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_TOKEN=3AqlNjjWKOeqmIGjN1Gu4Dnqm5d_28Hfykvwy45AXCe8gUHGz

# Dominio reservado (plan gratuito permite 1 dominio)
# Obtenido de: https://dashboard.ngrok.com/cloud-edge/domains
NGROK_DOMAIN=premium-size-unreached.ngrok-free.dev

# Nota: Las líneas que empiezan con # son comentarios y se ignoran
```

---

## ✅ Ventajas de esta Arquitectura

1. **✅ Centralizado**: Toda la configuración en un solo archivo
2. **✅ Fácil de cambiar**: Edita un archivo y reinicia
3. **✅ Seguro**: Archivo protegido en `.gitignore`
4. **✅ Flexible**: Soporta múltiples métodos de configuración (fallbacks)
5. **✅ Sin código duro**: No hay valores hardcodeados en el código
6. **✅ Documentado**: Comentarios en el archivo explican cada variable

---

## 🔄 Migración desde Versión Anterior

Si tenías el token en `config/.ngrok_token`:

1. El sistema seguirá funcionando (fallback automático)
2. Para migrar a la nueva arquitectura:
   - Crea `config/ngrok_config.txt`
   - Copia el token de `.ngrok_token`
   - Agrega el dominio si lo tienes
   - Opcionalmente, elimina `.ngrok_token`

---

**Última actualización**: 2026-05-07  
**Versión**: 2.0 (Arquitectura centralizada)
