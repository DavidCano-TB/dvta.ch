@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔒 MANTENIENDO URL ESTABLE
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Tu URL actual es:
type c:\dvdcoin\url_temporal.txt
echo.
echo Esta URL se mantendrá mientras los servicios estén corriendo.
echo.
echo Para que NUNCA cambie, NO ejecutes:
echo   - DETENER_TODO.bat
echo   - Reiniciar el PC
echo.
echo Si necesitas reiniciar, ejecuta después:
echo   - INICIAR_SISTEMA_COMPLETO.bat
echo.
echo Y la URL cambiará. Guarda la nueva URL de: url_temporal.txt
echo.
pause
