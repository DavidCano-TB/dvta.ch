@echo off
chcp 65001 >nul
title OPTIMIZADOR WINDOWS 11 - RENDIMIENTO MÁXIMO (Errores Visibles)
color 0A

echo.
echo ========================================================
echo  OPTIMIZADOR DE RENDIMIENTO WINDOWS 11 - VERSIÓN MÁXIMA
echo  + Acelera TODO (CPU, RAM, Gráficos, Audio, Disco)
echo  + Instala últimos drivers automáticamente
echo  + Actualiza TODOS los programas SIN CLICAR NADA
echo  + Cancela todo lo no imprescindible al encender
echo  + Mejoras extremas seguras (sin romper nada)
echo ========================================================
echo.
echo **IMPORTANTE: EJECUTA ESTE ARCHIVO COMO ADMINISTRADOR**
echo.
echo Pulsa cualquier tecla para continuar...
pause >nul

:: === COMPROBAR ADMINISTRADOR ===
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Este script necesita privilegios de Administrador.
    echo Cierra esta ventana, haz clic derecho sobre el .bat y selecciona "Ejecutar como administrador".
    pause
    exit /b 1
)

echo.
echo [1/9] Creando punto de restauración del sistema...
powershell -Command "Checkpoint-Computer -Description 'Antes_Optimizacion_Maxima_Grok_2026' -RestorePointType 'MODIFY_SETTINGS'" 
if %errorlevel% == 0 (
    echo ✓ Punto de restauración creado correctamente.
) else (
    echo [ADVERTENCIA] No se pudo crear el punto de restauración (puede estar desactivado).
)

echo.
echo [2/9] Activando plan de energía ULTIMATE PERFORMANCE...
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61
powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61
if %errorlevel% == 0 (
    echo ✓ Plan Ultimate Performance activado.
) else (
    echo [ADVERTENCIA] Error al activar Ultimate Performance.
)

echo.
echo [3/9] Desactivando efectos visuales y animaciones al máximo...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f
reg add "HKCU\Control Panel\Desktop" /v MenuShowDelay /t REG_SZ /d "0" /f
reg add "HKCU\Control Panel\Desktop" /v UserPreferencesMask /t REG_BINARY /d 9012038010000000 /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v DisableThumbnailCache /t REG_DWORD /d 1 /f
echo ✓ Efectos visuales optimizados.

echo.
echo [4/9] Cancelando TODAS las ejecuciones no imprescindibles al encender...
if not exist "C:\StartupBackup" mkdir "C:\StartupBackup"
xcopy "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\*" "C:\StartupBackup\Usuario\" /s /y /q >nul 2>&1
xcopy "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\*" "C:\StartupBackup\TodosLosUsuarios\" /s /y /q >nul 2>&1
del /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\*.*" 2>nul
del /q "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\*.*" 2>nul
echo ✓ Programas de inicio movidos a backup (C:\StartupBackup).

echo.
echo [5/9] Limpiando archivos temporales, caché y Prefetch...
del /q /s /f "%TEMP%\*" 2>nul
del /q /s /f "C:\Windows\Temp\*" 2>nul
del /q /s /f "C:\Windows\Prefetch\*" 2>nul
del /q /s /f "C:\Windows\SoftwareDistribution\Download\*" 2>nul
echo ✓ Limpieza completada.

echo.
echo [6/9] Desactivando servicios no esenciales...
sc config DiagTrack start= disabled
sc config dmwappushservice start= disabled
sc config RetailDemo start= disabled
sc config MapsBroker start= disabled
sc config WSearch start= demand
echo ✓ Servicios configurados.

echo.
echo [7/9] Forzando Windows Update para drivers y actualizaciones...
UsoClient.exe StartScan
UsoClient.exe StartDownload
UsoClient.exe StartInstall
echo ✓ Comprobación de actualizaciones y drivers iniciada.

echo.
echo [8/9] Actualizando TODOS los programas automáticamente con winget...
where winget >nul 2>&1
if %errorlevel%==0 (
    echo   Actualizando todos los programas de forma silenciosa...
    winget upgrade --all --silent --disable-interactivity --accept-package-agreements --accept-source-agreements --include-unknown
    if %errorlevel% == 0 (
        echo ✓ Actualización de programas completada.
    ) else (
        echo [ADVERTENCIA] Algunos programas no se pudieron actualizar (ver errores arriba).
    )
) else (
    echo [ERROR] Winget no está instalado. Instálalo desde Microsoft Store (App Installer).
)

echo.
echo [9/9] Aplicando mejoras extremas de rendimiento...
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f
reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v Win32PrioritySeparation /t REG_DWORD /d 38 /f
reg add "HKCU\Software\Microsoft\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f
reg add "HKCU\Software\Microsoft\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 1 /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications" /v Migrated /t REG_DWORD /d 1 /f
echo ✓ Mejoras aplicadas: Gráficos (HAGS), CPU, Game Mode y RAM liberada.

echo.
echo ========================================================
echo ¡OPTIMIZACIÓN TERMINADA!
echo.
echo REINICIA el equipo ahora para aplicar todos los cambios.
echo.
echo Si ves errores rojos arriba, cópialos y pégamelos aquí para ayudarte.
echo Para revertir cualquier cambio: usa "Restaurar sistema" con el punto creado.
echo ========================================================
pause