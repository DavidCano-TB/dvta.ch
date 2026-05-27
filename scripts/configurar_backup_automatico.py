"""
Configura una tarea programada en Windows para ejecutar el backup diariamente
"""
import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SCRIPT_PATH = BASE_DIR / "scripts" / "backup_databases.py"
PYTHON_PATH = sys.executable

# Configuración de la tarea
TASK_NAME = "DVDCoin_Backup_Diario"
TASK_TIME = "03:00"  # 3:00 AM

def crear_tarea_programada():
    """Crea una tarea programada en Windows"""
    
    # Comando para crear la tarea
    comando = [
        "schtasks",
        "/Create",
        "/TN", TASK_NAME,
        "/TR", f'"{PYTHON_PATH}" "{SCRIPT_PATH}"',
        "/SC", "DAILY",
        "/ST", TASK_TIME,
        "/F",  # Forzar creación (sobrescribe si existe)
        "/RL", "HIGHEST"  # Ejecutar con privilegios más altos
    ]
    
    try:
        print(f"Creando tarea programada: {TASK_NAME}")
        print(f"Hora de ejecución: {TASK_TIME} (todos los días)")
        print(f"Script: {SCRIPT_PATH}")
        print(f"Python: {PYTHON_PATH}")
        print()
        
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if resultado.returncode == 0:
            print("✓ Tarea programada creada exitosamente")
            print()
            print("Para verificar la tarea, ejecuta:")
            print(f'  schtasks /Query /TN "{TASK_NAME}" /V /FO LIST')
            print()
            print("Para ejecutar la tarea manualmente:")
            print(f'  schtasks /Run /TN "{TASK_NAME}"')
            print()
            print("Para eliminar la tarea:")
            print(f'  schtasks /Delete /TN "{TASK_NAME}" /F')
            return True
        else:
            print("✗ Error creando la tarea programada")
            print(f"Código de error: {resultado.returncode}")
            if resultado.stderr:
                print(f"Error: {resultado.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def verificar_tarea():
    """Verifica si la tarea ya existe"""
    try:
        resultado = subprocess.run(
            ["schtasks", "/Query", "/TN", TASK_NAME],
            capture_output=True,
            text=True
        )
        return resultado.returncode == 0
    except:
        return False

def main():
    print("=" * 60)
    print("CONFIGURACIÓN DE BACKUP AUTOMÁTICO")
    print("=" * 60)
    print()
    
    if verificar_tarea():
        print(f"⚠ La tarea '{TASK_NAME}' ya existe")
        respuesta = input("¿Deseas reconfigurarla? (s/n): ").strip().lower()
        if respuesta != 's':
            print("Operación cancelada")
            return 0
        print()
    
    if crear_tarea_programada():
        print()
        print("=" * 60)
        print("✓ CONFIGURACIÓN COMPLETADA")
        print("=" * 60)
        print()
        print("El backup se ejecutará automáticamente todos los días a las 3:00 AM")
        print("Los backups se guardarán en: backup/")
        print("Se mantendrán los últimos 7 días de backups")
        return 0
    else:
        print()
        print("=" * 60)
        print("✗ ERROR EN LA CONFIGURACIÓN")
        print("=" * 60)
        print()
        print("Asegúrate de ejecutar este script como Administrador")
        return 1

if __name__ == "__main__":
    exit(main())
