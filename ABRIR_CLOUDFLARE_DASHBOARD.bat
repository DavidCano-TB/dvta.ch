@echo off
chcp 65001 >nul

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  CONFIGURAR dvta.ch EN CLOUDFLARE DASHBOARD
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script abrirá el dashboard de Cloudflare para configurar el túnel.
echo.
echo PASOS A SEGUIR:
echo.
echo 1. Se abrirá el navegador en Cloudflare Zero Trust
echo 2. Inicia sesión si es necesario
echo 3. Ve a: Networks ^> Tunnels
echo 4. Haz clic en "Create a tunnel"
echo 5. Selecciona "Cloudflared"
echo 6. Nombre: dvta-tunnel
echo 7. En la página siguiente, COPIA el token que aparece
echo 8. Vuelve a esta ventana y pégalo cuando se te pida
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

echo.
echo Abriendo Cloudflare Dashboard...
start https://one.dash.cloudflare.com/

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  INSTRUCCIONES DETALLADAS
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo EN EL NAVEGADOR:
echo.
echo 1. Selecciona tu cuenta de Cloudflare
echo.
echo 2. En el menú lateral, busca "Zero Trust" o "Access"
echo.
echo 3. Ve a: Networks ^> Tunnels
echo.
echo 4. Haz clic en "Create a tunnel"
echo.
echo 5. Selecciona "Cloudflared" como conector
echo.
echo 6. Nombre del túnel: dvta-tunnel
echo.
echo 7. Haz clic en "Save tunnel"
echo.
echo 8. En la siguiente pantalla verás un comando como:
echo    cloudflared.exe service install eyJh...
echo.
echo 9. COPIA TODO el token (la parte después de "install ")
echo.
echo 10. Vuelve aquí y pégalo
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo ¿Ya tienes el token? (S/N)
set /p TIENE_TOKEN=

if /i "%TIENE_TOKEN%"=="S" (
    echo.
    echo Pega el token aquí y presiona Enter:
    set /p TUNNEL_TOKEN=
    
    if defined TUNNEL_TOKEN (
        echo.
        echo Instalando túnel...
        cloudflared.exe service install !TUNNEL_TOKEN!
        
        if errorlevel 1 (
            echo.
            echo ❌ Error al instalar el túnel
            echo.
            echo Intenta ejecutar manualmente:
            echo cloudflared.exe service install !TUNNEL_TOKEN!
            echo.
        ) else (
            echo.
            echo ✅ Túnel instalado correctamente
            echo.
            echo Ahora configura las rutas públicas en el dashboard:
            echo.
            echo 1. En la página del túnel, ve a "Public Hostname"
            echo 2. Haz clic en "Add a public hostname"
            echo 3. Configura:
            echo    - Subdomain: (dejar vacío)
            echo    - Domain: dvta.ch
            echo    - Service Type: HTTP
            echo    - URL: localhost:8000
            echo 4. Guarda
            echo 5. Repite para www.dvta.ch
            echo.
            echo Cuando termines, ejecuta: INICIAR_DVDBANK_DVTA.bat
            echo.
        )
    )
) else (
    echo.
    echo Sigue los pasos en el navegador y vuelve cuando tengas el token.
    echo Luego ejecuta este script de nuevo.
    echo.
)

pause
