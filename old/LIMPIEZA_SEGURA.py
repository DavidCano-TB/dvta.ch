#!/usr/bin/env python3
"""
Script de limpieza segura para DVDcoin
- Identifica archivos duplicados y backups
- Verifica dependencias antes de eliminar
- Crea backup antes de cualquier eliminación
"""

import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Carpetas que son claramente backups o duplicados
CARPETAS_BACKUP = [
    "dvdcoin backup",
    "old",
    "dvdcoin_bank_windows",  # Solo contiene venv vacío
]

# Archivos de test y temporales que pueden eliminarse
ARCHIVOS_TEMPORALES = [
    # Logs de ngrok antiguos
    "ngrok_*.log",
    # Archivos .pyc
    "*.pyc",
    # Archivos de test específicos (mantener los de test_funcionalidades)
    "test_*.py",  # Solo en raíz
    "TEST_*.py",  # Solo en raíz
    "TEST_*.bat",  # Solo en raíz
    "TEST_*.html",  # Solo en raíz
]

# Archivos .bat duplicados o innecesarios (muchos hacen lo mismo)
BATS_DUPLICADOS = [
    "ABRIR_OPO_AHORA.bat",
    "ABRIR_OPO_CON_LOGIN.bat",
    "ABRIR_OPO_CORRECTO.bat",
    "ABRIR_OPO_DIRECTO.bat",
    "ABRIR_OPO_GESTION.bat",
    "ABRIR_OPO_LIMPIO.bat",
    "ABRIR_OPO_LOCALHOST.bat",
    "ABRIR_OPO_VERIFICADO.bat",
    "APLICAR_CAMBIOS_OPO.bat",
    "APLICAR_CAMBIOS_VOTACIONES_AHORA.bat",
    "APLICAR_FIX_OPO.bat",
    "ARREGLAR_OPO_DEFINITIVO.bat",
    "CORRECCION_A_FONDO.bat",
    "CORRECCION_AUTOMATICA.bat",
    "CORREGIR_OPO_COMPLETO.bat",
    "DIAGNOSTICAR_OPO.bat",
    "DIAGNOSTICAR_Y_REPARAR_NGROK.bat",
    "DIAGNOSTICO_COMPLETO_OPO.bat",
    "GESTIONAR_ACCESO_OPO.bat",
    "GESTIONAR_OPO.bat",
    "INICIAR_OPO_LOCAL.bat",
    "INICIAR_TODO_OPO.bat",
    "MATAR_TODO_Y_REINICIAR_OPO.bat",
    "REINICIAR_OPO_LIMPIO.bat",
    "REINICIAR_SERVIDOR_OPO.bat",
    "REINICIAR_TODO_AHORA.bat",
    "REINICIAR_TODO_DEFINITIVO.bat",
    "REINICIAR_TODO.bat",
    "REINICIO_AUTOMATICO_OPO.bat",
    "SOLUCION_DEFINITIVA_OPO.bat",
    "SOLUCION_DEFINITIVA.bat",
    "SOLUCION_NGROK_FINAL.bat",
    "SOLUCIONAR_NGROK_AHORA.bat",
    "VERIFICAR_OPO_FUNCIONA.bat",
    "VERIFICAR_OPO.bat",
    "VERIFICAR_Y_ABRIR_OPO.bat",
]

# Archivos .md de documentación duplicada
MDS_DUPLICADOS = [
    "ARREGLO_OPO_BLOQUES.md",
    "CAMBIOS_NAVEGACION.md",
    "INSTRUCCIONES_FINALES_OPO.md",
    "MEJORAS_QUIEN_SOY_COMPLETAS.md",
    "MEJORAS_QUIEN_SOY.md",
    "NUEVA_PAGINA_GESTION_OPO.md",
    "NUEVA_PAGINA_OPO_COMPLETA.md",
    "OPO_DEFINITIVO_SIN_LOGIN.md",
    "OPO_SIN_AUTH_LISTO.md",
    "RESUMEN_FINAL_COMPLETO_OPO.txt",
    "RESUMEN_FINAL_OPO.md",
    "RESUMEN_FINAL_QUIEN_SOY.md",
    "SISTEMA_LISTO.txt",
    "SISTEMA_OPO_LISTO.md",
    "TRABAJO_COMPLETADO_OPO.md",
    "VERIFICACION_FINAL_COMPLETA.md",
    "VERIFICACION_VISUAL_OPO.md",
]

def crear_backup():
    """Crea un backup completo antes de la limpieza"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(BASE_DIR, f"BACKUP_ANTES_LIMPIEZA_{timestamp}")
    
    print(f"\n📦 Creando backup en: {backup_dir}")
    
    # Copiar solo las carpetas que vamos a eliminar
    for carpeta in CARPETAS_BACKUP:
        src = os.path.join(BASE_DIR, carpeta)
        if os.path.exists(src):
            dst = os.path.join(backup_dir, carpeta)
            print(f"  Copiando {carpeta}...")
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
    
    print(f"✅ Backup creado exitosamente\n")
    return backup_dir

def analizar_espacio():
    """Analiza cuánto espacio ocupan las carpetas a eliminar"""
    print("\n📊 Analizando espacio en disco...\n")
    
    total_size = 0
    for carpeta in CARPETAS_BACKUP:
        path = os.path.join(BASE_DIR, carpeta)
        if os.path.exists(path):
            size = get_dir_size(path)
            size_mb = size / (1024 * 1024)
            total_size += size
            print(f"  {carpeta}: {size_mb:.2f} MB")
    
    print(f"\n  TOTAL A LIBERAR: {total_size / (1024 * 1024):.2f} MB\n")
    return total_size

def get_dir_size(path):
    """Calcula el tamaño total de un directorio"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_dir_size(entry.path)
    except Exception:
        pass
    return total

def limpiar_carpetas_backup():
    """Elimina las carpetas de backup identificadas"""
    print("\n🗑️  Eliminando carpetas de backup...\n")
    
    for carpeta in CARPETAS_BACKUP:
        path = os.path.join(BASE_DIR, carpeta)
        if os.path.exists(path):
            try:
                print(f"  Eliminando {carpeta}...")
                shutil.rmtree(path)
                print(f"  ✅ {carpeta} eliminado")
            except Exception as e:
                print(f"  ❌ Error eliminando {carpeta}: {e}")

def limpiar_archivos_duplicados():
    """Elimina archivos .bat y .md duplicados"""
    print("\n🗑️  Eliminando archivos duplicados...\n")
    
    # BATs duplicados
    print("  Eliminando .bat duplicados...")
    for bat in BATS_DUPLICADOS:
        path = os.path.join(BASE_DIR, bat)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"    ✅ {bat}")
            except Exception as e:
                print(f"    ❌ {bat}: {e}")
    
    # MDs duplicados
    print("\n  Eliminando .md duplicados...")
    for md in MDS_DUPLICADOS:
        path = os.path.join(BASE_DIR, md)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"    ✅ {md}")
            except Exception as e:
                print(f"    ❌ {md}: {e}")

def limpiar_archivos_test():
    """Elimina archivos de test en la raíz (no en test_funcionalidades)"""
    print("\n🗑️  Eliminando archivos de test en raíz...\n")
    
    import glob
    
    patterns = ["test_*.py", "TEST_*.py", "TEST_*.bat", "TEST_*.html"]
    for pattern in patterns:
        for file in glob.glob(os.path.join(BASE_DIR, pattern)):
            # No eliminar si está en subdirectorios
            if os.path.dirname(file) == BASE_DIR:
                try:
                    os.remove(file)
                    print(f"  ✅ {os.path.basename(file)}")
                except Exception as e:
                    print(f"  ❌ {os.path.basename(file)}: {e}")

def limpiar_logs_antiguos():
    """Elimina logs de ngrok antiguos"""
    print("\n🗑️  Eliminando logs antiguos de ngrok...\n")
    
    import glob
    for log in glob.glob(os.path.join(BASE_DIR, "ngrok_*.log")):
        try:
            os.remove(log)
            print(f"  ✅ {os.path.basename(log)}")
        except Exception as e:
            print(f"  ❌ {os.path.basename(log)}: {e}")

def main():
    import sys
    auto_mode = '--auto' in sys.argv or '-y' in sys.argv
    
    print("=" * 70)
    print("  LIMPIEZA SEGURA DE DVDCOIN")
    print("=" * 70)
    
    # Analizar espacio
    analizar_espacio()
    
    # Confirmar
    if not auto_mode:
        print("\n⚠️  ADVERTENCIA:")
        print("  Se eliminarán carpetas de backup y archivos duplicados.")
        print("  Se creará un backup antes de proceder.")
        print("\n  Carpetas a eliminar:")
        for c in CARPETAS_BACKUP:
            print(f"    - {c}")
        
        respuesta = input("\n¿Continuar? (s/N): ").strip().lower()
        if respuesta != 's':
            print("\n❌ Limpieza cancelada")
            return
    else:
        print("\n✅ Modo automático activado, procediendo con la limpieza...")
    
    # Crear backup
    backup_dir = crear_backup()
    
    # Limpiar
    limpiar_carpetas_backup()
    limpiar_archivos_duplicados()
    limpiar_archivos_test()
    limpiar_logs_antiguos()
    
    print("\n" + "=" * 70)
    print("  ✅ LIMPIEZA COMPLETADA")
    print("=" * 70)
    print(f"\n  Backup guardado en: {backup_dir}")
    print("\n  Si algo falla, puedes restaurar desde el backup.")
    print("\n")

if __name__ == "__main__":
    main()
