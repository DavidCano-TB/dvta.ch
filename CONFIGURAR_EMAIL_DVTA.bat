@echo off
chcp 65001 >nul

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  📧 CONFIGURAR EMAIL: info@dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este asistente te guiará para configurar info@dvta.ch
echo.
echo SOLUCIÓN: Cloudflare Email Routing (GRATIS)
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PASO 1: ACTIVAR EMAIL ROUTING EN CLOUDFLARE
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Abriendo Cloudflare Dashboard...
echo.
echo EN EL NAVEGADOR:
echo.
echo 1. Selecciona el dominio: dvta.ch
echo 2. En el menú lateral, haz clic en: "Email" → "Email Routing"
echo 3. Haz clic en: "Get started" o "Enable Email Routing"
echo 4. Cloudflare configurará los registros DNS automáticamente
echo 5. Espera a que se complete (1-2 minutos)
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

start https://dash.cloudflare.com/

echo.
echo ¿Has activado Email Routing? (S/N)
set /p ACTIVADO=

if /i not "%ACTIVADO%"=="S" (
    echo.
    echo Activa Email Routing y vuelve a ejecutar este script.
    pause
    exit /b
)

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PASO 2: AGREGAR DIRECCIÓN DE DESTINO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo EN EL NAVEGADOR (Cloudflare Dashboard):
echo.
echo 1. En "Destination addresses", haz clic en "Add destination address"
echo 2. Ingresa: Davidcano.ch@gmail.com
echo 3. Haz clic en "Send verification email"
echo 4. Ve a tu Gmail y haz clic en el enlace de verificación
echo 5. Vuelve a Cloudflare
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

echo.
echo Abriendo Gmail...
start https://mail.google.com/

echo.
echo ¿Has verificado Davidcano.ch@gmail.com en Cloudflare? (S/N)
set /p VERIFICADO=

if /i not "%VERIFICADO%"=="S" (
    echo.
    echo Verifica el email y vuelve a ejecutar este script.
    pause
    exit /b
)

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PASO 3: CREAR REGLA DE ENRUTAMIENTO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo EN EL NAVEGADOR (Cloudflare Dashboard):
echo.
echo 1. En "Routing rules", haz clic en "Create address"
echo 2. Configura:
echo    - Custom address: info
echo    - Action: Send to an email
echo    - Destination: Davidcano.ch@gmail.com
echo 3. Haz clic en "Save"
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

echo.
echo ¿Has creado la regla para info@dvta.ch? (S/N)
set /p REGLA=

if /i not "%REGLA%"=="S" (
    echo.
    echo Crea la regla y vuelve a ejecutar este script.
    pause
    exit /b
)

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PASO 4: CONFIGURAR GMAIL PARA ENVIAR COMO info@dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Abriendo configuración de Gmail...
echo.
start https://mail.google.com/mail/u/0/#settings/accounts

echo.
echo EN GMAIL:
echo.
echo 1. En "Enviar correo como", haz clic en "Añadir otra dirección de correo"
echo 2. Ingresa:
echo    - Nombre: DVDBank Info
echo    - Dirección: info@dvta.ch
echo    - Desmarca "Tratarlo como un alias"
echo 3. Haz clic en "Siguiente paso"
echo 4. Configura SMTP:
echo    - Servidor: smtp.gmail.com
echo    - Puerto: 587
echo    - Usuario: Davidcano.ch@gmail.com
echo    - Contraseña: [Contraseña de aplicación]
echo    - TLS activado
echo 5. Añadir cuenta
echo 6. Verifica con el código que llegará a tu Gmail
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PASO 5: CREAR CONTRASEÑA DE APLICACIÓN
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Abriendo Google Account...
echo.
start https://myaccount.google.com/apppasswords

echo.
echo EN GOOGLE ACCOUNT:
echo.
echo 1. Si no tienes verificación en 2 pasos, actívala primero
echo 2. En "Contraseñas de aplicaciones":
echo    - App: Correo
echo    - Dispositivo: Otro (DVDBank SMTP)
echo 3. Haz clic en "Generar"
echo 4. Copia la contraseña de 16 caracteres
echo 5. Úsala en Gmail (paso 4.4)
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Email configurado: info@dvta.ch
echo.
echo RECIBIR CORREOS:
echo   → Los correos a info@dvta.ch llegarán a Davidcano.ch@gmail.com
echo.
echo ENVIAR CORREOS:
echo   → Desde Gmail, selecciona "De: info@dvta.ch"
echo.
echo CREDENCIALES SMTP:
echo   → Servidor: smtp.gmail.com
echo   → Puerto: 587 (TLS)
echo   → Usuario: Davidcano.ch@gmail.com
echo   → Contraseña: [Contraseña de aplicación de Gmail]
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Para más información, lee: CONFIGURACION_EMAIL_DVTA_CH.txt
echo.
pause
