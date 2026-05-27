@echo off
chcp 65001 >nul
title Commit Arquitectura Modular
color 0E

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   📦 COMMIT - Arquitectura Modular Completa
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [1/4] Verificando Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo      ❌ Git no encontrado
    pause
    exit /b 1
)
echo      ✅ Git instalado
echo.

echo [2/4] Añadiendo archivos...
git add .
git add modules/
git add config/
git add .github/
git add .gitignore
echo      ✅ Archivos añadidos
echo.

echo [3/4] Creando commit...
git commit -m "feat: Arquitectura modular completa con módulo Exams

- ✅ Estructura modular completa (shared, exams, bank, games, social)
- ✅ Módulo Exams funcional (puerto 8001, dvta.ch)
- ✅ Sistema de autenticación con JWT
- ✅ Verificación por email
- ✅ Bases de datos separadas
- ✅ Interfaz HTML con estilo azulado
- ✅ Scripts de arranque robustos
- ✅ GitHub Actions actualizado
- ✅ Cloudflare Tunnel configurado
- ✅ Documentación completa
- ✅ Sistema de verificación

Módulos:
- shared: Utilidades reutilizables (email, DB, JWT, utils)
- exams: Sistema completo de exámenes (puerto 8001)
- bank: Preparado para migración
- games: Preparado para juegos
- social: Preparado para futuro

Scripts:
- ARRANCAR_TODO.bat: Inicia todos los módulos
- ARRANCAR_DVTA_COMPLETO.bat: Inicia Exams + Tunnel
- ARREGLAR_DVTA_AHORA.bat: Solución Error 1033
- DIAGNOSTICO_COMPLETO.bat: Verificación completa
- VERIFICAR_SISTEMA_COMPLETO.bat: Verificación general

Configuración:
- cloudflare-dvta-config.yml: dvta.ch → puerto 8001
- GitHub Actions: Valida todos los módulos
- .gitignore: Excluye archivos sensibles

Documentación:
- RESUMEN_FINAL_SISTEMA.md
- GUIA_RAPIDA_ARRANQUE.md
- README_DVTA_CH.md
- TODO_LISTO.txt
- CHANGELOG_ARQUITECTURA_MODULAR.md

Fixes:
- Error 1033 dvta.ch solucionado
- Servidor Exams con start_exams.py robusto
- Manejo de errores mejorado
- Verificación de dependencias automática"

if %errorlevel% neq 0 (
    echo      ⚠️  No hay cambios para commit o error
) else (
    echo      ✅ Commit creado
)
echo.

echo [4/4] Haciendo push a GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo      ⚠️  Intentando con master...
    git push origin master
    if %errorlevel% neq 0 (
        echo      ❌ Error en push
        echo.
        echo      Verifica:
        echo        • Conexión a internet
        echo        • Credenciales de GitHub
        echo        • Rama correcta
        pause
        exit /b 1
    )
)
echo      ✅ Push completado
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ COMMIT Y PUSH EXITOSOS
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo GitHub Actions se ejecutará automáticamente y:
echo   • Verificará sintaxis de todos los módulos
echo   • Instalará dependencias
echo   • Ejecutará tests
echo   • Enviará email de confirmación
echo.
echo Ver en: https://github.com/davidcano-tb/dvta.ch/actions
echo.
pause
