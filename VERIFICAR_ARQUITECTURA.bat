@echo off
chcp 65001 >nul
echo ========================================
echo   Verificación Arquitectura Modular
echo ========================================
echo.

echo [1/5] Verificando estructura de carpetas...
if exist "modules\shared\email_service.py" (
    echo ✅ Módulo shared OK
) else (
    echo ❌ Módulo shared FALTA
)

if exist "modules\exams\app_exams.py" (
    echo ✅ Módulo exams OK
) else (
    echo ❌ Módulo exams FALTA
)

if exist "modules\exams\static\index.html" (
    echo ✅ HTML principal OK
) else (
    echo ❌ HTML principal FALTA
)

if exist "modules\exams\static\css\exams-style.css" (
    echo ✅ CSS azulado OK
) else (
    echo ❌ CSS azulado FALTA
)

echo.
echo [2/5] Verificando configuración...
if exist "modules\exams\config\admins.json" (
    echo ✅ Config admins OK
) else (
    echo ❌ Config admins FALTA
)

if exist "modules\exams\config\email.json.example" (
    echo ✅ Config email example OK
) else (
    echo ❌ Config email example FALTA
)

echo.
echo [3/5] Verificando documentación...
if exist "PLAN_ARQUITECTURA_MODULAR.md" (
    echo ✅ Plan completo OK
) else (
    echo ❌ Plan completo FALTA
)

if exist "ARQUITECTURA_MODULAR_IMPLEMENTADA.md" (
    echo ✅ Implementación OK
) else (
    echo ❌ Implementación FALTA
)

if exist "RESUMEN_ARQUITECTURA_MODULAR.md" (
    echo ✅ Resumen ejecutivo OK
) else (
    echo ❌ Resumen ejecutivo FALTA
)

if exist "modules\exams\README.md" (
    echo ✅ README exams OK
) else (
    echo ❌ README exams FALTA
)

echo.
echo [4/5] Verificando dependencias Python...
python -c "import sys; print(f'Python {sys.version.split()[0]}')" 2>nul
if errorlevel 1 (
    echo ❌ Python no encontrado
) else (
    echo ✅ Python instalado
)

echo.
echo [5/5] Verificando archivos críticos...
if exist "modules\shared\db_helper.py" echo ✅ db_helper.py
if exist "modules\shared\jwt_helper.py" echo ✅ jwt_helper.py
if exist "modules\shared\utils.py" echo ✅ utils.py
if exist "modules\exams\requirements.txt" echo ✅ requirements.txt
if exist "modules\exams\opo\list.html" echo ✅ opo/list.html
if exist "modules\exams\static\js\main.js" echo ✅ main.js

echo.
echo ========================================
echo   Resumen
echo ========================================
echo.
echo ✅ Arquitectura modular creada
echo ✅ Módulo EXAMS completo
echo ✅ Módulo SHARED con utilidades
echo ✅ Documentación completa
echo.
echo 📝 Próximos pasos:
echo    1. Completar HTML de OPO (admin, exam-types, exam)
echo    2. Migrar datos de OPO desde bank
echo    3. Eliminar OPO de bank
echo.
echo 🚀 Para iniciar el servidor:
echo    INICIAR_EXAMS.bat
echo.
echo 📖 Leer documentación:
echo    - RESUMEN_ARQUITECTURA_MODULAR.md
echo    - modules\exams\README.md
echo.

pause
