@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo   🧪 EJECUTAR TODOS LOS TESTS FUNCIONALES
echo ================================================================================
echo.

cd /d "%~dp0"

python RUN_ALL_TESTS.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE
    echo.
) else (
    echo.
    echo ❌ ALGUNOS TESTS FALLARON
    echo.
)

pause
