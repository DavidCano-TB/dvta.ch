================================================================================
                    ⚠️  ADVERTENCIA IMPORTANTE ⚠️
================================================================================

ARCHIVO PROTEGIDO: .ngrok_token
--------------------------------

Este archivo contiene la configuración de ngrok y SOLO debe ser modificado
manualmente por el administrador del sistema.

CONTENIDO ACTUAL:
-----------------
El archivo debe contener ÚNICAMENTE el token de autenticación de ngrok:

    3AqlNjjWKOeqmIGjN1Gu4Dnqm5d_28Hfykvwy45AXCe8gUHGz

O si usas dominio personalizado, puede tener este formato:

    NGROK_TOKEN=tu_token_aqui
    NGROK_DOMAIN=premium-size-unreached.ngrok-free.dev

REGLAS IMPORTANTES:
-------------------

✅ PERMITIDO:
   - Editar manualmente el archivo con un editor de texto
   - Cambiar el token si obtienes uno nuevo
   - Añadir o cambiar el dominio personalizado

❌ PROHIBIDO:
   - Que los scripts modifiquen este archivo automáticamente
   - Añadir URLs temporales de ngrok
   - Añadir comentarios o líneas adicionales
   - Borrar el archivo

PROTECCIÓN IMPLEMENTADA:
-------------------------

Se ha corregido el archivo INICIAR_COMO_ADMIN.bat para que:
- LEA el token del archivo
- NO ESCRIBA nada en el archivo
- Guarde la URL temporal en ngrok_url.txt (no en .ngrok_token)

VERIFICACIÓN:
-------------

Si sospechas que el archivo fue modificado incorrectamente:

1. Abre el archivo: conf\.ngrok_token
2. Verifica que solo contiene el token (y opcionalmente el dominio)
3. Si hay líneas adicionales (como NGROK_URL=...), bórralas
4. Guarda el archivo

FORMATO CORRECTO:
-----------------

Opción 1 - Solo token (una línea):
    3AqlNjjWKOeqmIGjN1Gu4Dnqm5d_28Hfykvwy45AXCe8gUHGz

Opción 2 - Token y dominio (dos líneas):
    NGROK_TOKEN=3AqlNjjWKOeqmIGjN1Gu4Dnqm5d_28Hfykvwy45AXCe8gUHGz
    NGROK_DOMAIN=premium-size-unreached.ngrok-free.dev

FORMATO INCORRECTO (NO USAR):
------------------------------

❌ Con URLs temporales:
    NGROK_TOKEN=...
    NGROK_DOMAIN=...
    NGROK_URL=https://xxxx.ngrok.io  ← ESTO NO DEBE ESTAR AQUÍ

❌ Con comentarios:
    # Token de ngrok  ← NO AÑADIR COMENTARIOS
    NGROK_TOKEN=...

UBICACIÓN DE OTROS ARCHIVOS:
-----------------------------

- Token de ngrok:     conf\.ngrok_token  (PROTEGIDO - solo edición manual)
- URL temporal:       ngrok_url.txt      (generado automáticamente)
- Logs de ngrok:      ngrok.log          (generado automáticamente)
- API de ngrok:       ngrok_tunnels.json (generado automáticamente)

CAMBIOS REALIZADOS:
-------------------

Fecha: 14 de mayo de 2026
Archivo corregido: INICIAR_COMO_ADMIN.bat
Línea eliminada: echo NGROK_URL=%NGROK_URL%>>conf\.ngrok_token
Razón: Evitar que se añadan URLs temporales al archivo de configuración

RESPONSABILIDAD:
----------------

Solo el administrador del sistema debe modificar el archivo .ngrok_token.
Los scripts solo deben LEER este archivo, nunca ESCRIBIR en él.

================================================================================
                    MANTÉN ESTE ARCHIVO PROTEGIDO
================================================================================

Si tienes dudas sobre cómo configurar ngrok, consulta:
- NGROK_CONFIG_README.md
- INSTRUCCIONES_ARRANQUE.txt
- O contacta al administrador del sistema

================================================================================
