#!/usr/bin/env python3
"""
Script de limpieza del proyecto DVDcoin
Mueve archivos innecesarios a la carpeta 'old'
"""
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent
OLD_DIR = BASE_DIR / "old"

# Crear carpeta old si no existe
OLD_DIR.mkdir(exist_ok=True)

# Archivos Python innecesarios (scripts de prueba/diagnóstico/utilidades)
python_files_to_move = [
    "restore_porra_7_complete.py",
    "sincronizar_y_limpiar_main.py",
    "test_ai_simple.py",
    "_do_restart.py",
    "_setup_autostart.py",
    "cleanup_project.py",  # Este mismo script después de ejecutarse
]

# Archivos .md innecesarios (mantener solo README.md)
md_files_to_move = [
    "ACCION_REQUERIDA.md",
    "CAMBIOS_PANEL_TRANSACCIONES.md",
    "CONFIRMACION_FINAL.md",
    "CONFIRMACION_PANEL_TRANSACCIONES.md",
    "FIX_HISTORIAL_Y_REINICIO.md",
    "FIX_OPO_ACCESO.md",
    "FIX_OPO_PANTALLA_VACIA.md",
    "FIX_TRANSACCIONES_PRIVACIDAD.md",
    "GRAPHIFY_INTEGRATION.md",
    "GUIA_CONFIGURAR_CLAUDE_API.md",
    "GUIA_CONFIGURAR_GEMINI_API.md",
    "HUNDIR_LA_FLOTA_ADMIN_MEJORADO.md",
    "HUNDIR_LA_FLOTA_VICTORIA_CORREGIDA.md",
    "INSTRUCCIONES_BACKUP.md",
    "INSTRUCCIONES_GEMINI_AI.md",
    "INSTRUCCIONES_QUIEN_SOY_MEJORADO.md",
    "INSTRUCCIONES_SUGERENCIAS_QUIEN_SOY.md",
    "MEJORAS_QUIEN_SOY.md",
    "MEJORAS_QUIEN_SOY_FINAL.md",
    "MEJORAS_QUIEN_SOY_IA.md",
    "MEJORAS_QUIEN_SOY_SUGERENCIAS.md",
    "MIGRACION_CLAUDE_A_GEMINI.md",
    "PERMISOS_AUDIO_VIDEO_OPTIMIZADOS.md",
    "PROBLEMA_REAL_ENCONTRADO.md",
    "QUE_DEBERIA_VER_EN_OPO.md",
    "README_IA_CLAUDE.md",
    "README_IA_GEMINI.md",
    "RESUMEN_CONFIGURAR_IA.md",
    "RESUMEN_FINAL_COMPLETO.md",
    "RESUMEN_FINAL_EXHAUSTIVO.md",
    "RESUMEN_FIX_OPO.md",
    "RESUMEN_MEJORAS_QUIEN_SOY.md",
    "RESUMEN_MEJORAS_SUGERENCIAS.md",
    "RESUMEN_QUIEN_SOY_100_IA.md",
    "RESUMEN_SOLUCION_OPO.md",
    "SERVIDOR_FUNCIONANDO.md",
    "SERVIDOR_OPO_LISTO.md",
    "SISTEMA_COMPLETO_FUNCIONANDO.md",
    "SISTEMA_LISTO_QUIEN_SOY.md",
    "SOLUCION_FINAL_GEMINI.md",
    "SOLUCION_FINAL_OPO.md",
    "SOLUCION_FINAL_OPO_DEFINITIVA.md",
    "SOLUCION_NGROK_DEFINITIVA.md",
    "SOLUCION_RAPIDA_OPO.md",
    "TRADUCCIONES_COMPLETAS.md",
    "VERIFICACION_COMPLETA_SISTEMA.md",
    "VERIFICACION_FINAL.md",
    "VERIFICACION_MIGRACION_COMPLETADA.md",
    "VERIFICACION_OPO_COMPLETA.md",
]

# Archivos .txt innecesarios
txt_files_to_move = [
    "COMO_USAR_OPO_AHORA.txt",
    "FIX_OPO_APLICADO.txt",
    "FIX_OPO_RESTAURADO.txt",
    "INICIO_RAPIDO_IA.txt",
    "INSTRUCCIONES_APLICAR_FIX_OPO.txt",
    "INSTRUCCIONES_ARRANQUE_AUTOMATICO.txt",
    "INSTRUCCIONES_FINALES_OPO.txt",
    "INSTRUCCIONES_URGENTES_OPO.txt",
    "INSTRUCCION_FINAL_SIMPLE.txt",
    "LEEME_NGROK.txt",
    "LEEME_OPO.txt",
    "LEEME_PRIMERO.txt",
    "LEEME_PRIMERO_OPO.txt",
    "LEE_ESTO_AHORA.txt",
    "LEE_ESTO_AHORA_OPO.txt",
    "LEE_ESTO_PRIMERO_OPO.txt",
    "NGROK_FUNCIONANDO.txt",
    "ngrok_url.txt",
    "OPO_LISTO.txt",
    "RESUMEN_EJECUTIVO.txt",
    "RESUMEN_FINAL_COMPLETO.txt",
    "RESUMEN_FINAL_OPO.txt",
    "RESUMEN_SOLUCION_QUIEN_SOY.txt",
    "RESUMEN_VERIFICACION_OPO.txt",
    "SERVIDOR_FUNCIONANDO.txt",
    "SERVIDOR_REINICIADO.txt",
    "SOLUCION_FINAL_OPO.txt",
    "TODO_FUNCIONANDO_CONFIRMADO.txt",
    "TODO_LISTO.txt",
    "URGENTE_LEE_ESTO.txt",
    "USA_LOCALHOST_NO_NGROK.txt",
    "VOTING_ARCHITECTURE.txt",
]

# Combinar todas las listas
all_files_to_move = python_files_to_move + md_files_to_move + txt_files_to_move

moved_count = 0
not_found_count = 0

print("=" * 70)
print("LIMPIEZA DEL PROYECTO DVDCOIN")
print("=" * 70)
print()

for filename in all_files_to_move:
    source = BASE_DIR / filename
    if source.exists():
        destination = OLD_DIR / filename
        try:
            shutil.move(str(source), str(destination))
            print(f"✓ Movido: {filename}")
            moved_count += 1
        except Exception as e:
            print(f"✗ Error moviendo {filename}: {e}")
    else:
        not_found_count += 1

print()
print("=" * 70)
print(f"RESUMEN:")
print(f"  Archivos movidos: {moved_count}")
print(f"  Archivos no encontrados: {not_found_count}")
print(f"  Total procesados: {len(all_files_to_move)}")
print("=" * 70)
print()
print("Archivos esenciales mantenidos:")
print("  - main.py (servidor principal)")
print("  - groq_helper.py (helper IA)")
print("  - ai_helper.py (helper IA alternativo)")
print("  - start.py (launcher)")
print("  - restart_server.py (reinicio)")
print("  - service_launcher.py (servicio)")
print("  - requirements.txt (dependencias)")
print("  - README.md (documentación principal)")
print()
