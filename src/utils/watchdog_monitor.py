#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DVDcoin Watchdog Monitor
Monitorea el servidor cada 5 minutos y reinicia el PC si falla 2 veces consecutivas
"""

import time
import requests
import subprocess
import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Configuración
CHECK_INTERVAL = 300  # 5 minutos en segundos
MAX_FAILURES = 2      # Número de fallos consecutivos antes de reiniciar
BASE_URL = "http://127.0.0.1:8000"
LOG_FILE = Path(__file__).parent / "logs" / "watchdog.log"

# Crear directorio de logs si no existe
LOG_FILE.parent.mkdir(exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ServerMonitor:
    def __init__(self):
        self.consecutive_failures = 0
        self.total_checks = 0
        self.total_failures = 0
        self.last_success = None
        self.start_time = datetime.now()
        
    def check_endpoint(self, endpoint, timeout=5):
        """Verifica un endpoint específico"""
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Error al verificar {endpoint}: {e}")
            return False
    
    def check_websocket_port(self):
        """Verifica que el puerto del WebSocket esté escuchando"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()
            return result == 0
        except Exception as e:
            logger.warning(f"Error al verificar puerto WebSocket: {e}")
            return False
    
    def check_python_processes(self):
        """Verifica que haya procesos de Python corriendo"""
        try:
            if sys.platform == 'win32':
                result = subprocess.run(
                    ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return 'python.exe' in result.stdout.lower()
            else:
                result = subprocess.run(
                    ['pgrep', '-f', 'python'],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
        except Exception as e:
            logger.warning(f"Error al verificar procesos Python: {e}")
            return False
    
    def check_ngrok_url(self):
        """Verifica que la URL de ngrok esté disponible"""
        try:
            url_file = Path(__file__).parent / "logs" / "current_url.txt"
            if not url_file.exists():
                logger.warning("Archivo current_url.txt no existe")
                return False
            
            with open(url_file, 'r', encoding='utf-8') as f:
                url = f.read().strip()
            
            if not url:
                logger.warning("URL de ngrok vacía")
                return False
            
            # Verificar que la URL responda
            response = requests.get(url, timeout=10, allow_redirects=True)
            return response.status_code in [200, 302, 307]
        except Exception as e:
            logger.warning(f"Error al verificar URL de ngrok: {e}")
            return False
    
    def comprehensive_check(self):
        """Realiza una verificación completa del sistema"""
        logger.info("=" * 70)
        logger.info("Iniciando verificación completa del sistema...")
        
        checks = {
            "Puerto 8000": self.check_websocket_port(),
            "Procesos Python": self.check_python_processes(),
            "Endpoint /api/health": self.check_endpoint("/api/health"),
            "Endpoint /api/ice-servers": self.check_endpoint("/api/ice-servers"),
            "Endpoint /api/rooms/list": self.check_endpoint("/api/rooms/list"),
            "URL Ngrok": self.check_ngrok_url(),
        }
        
        # Mostrar resultados
        all_passed = True
        for check_name, result in checks.items():
            status = "✅ OK" if result else "❌ FALLO"
            logger.info(f"  {check_name}: {status}")
            if not result:
                all_passed = False
        
        self.total_checks += 1
        
        if all_passed:
            logger.info("✅ Todas las verificaciones pasaron correctamente")
            self.consecutive_failures = 0
            self.last_success = datetime.now()
            return True
        else:
            self.consecutive_failures += 1
            self.total_failures += 1
            logger.error(f"❌ Verificación FALLIDA (Fallos consecutivos: {self.consecutive_failures}/{MAX_FAILURES})")
            return False
    
    def attempt_restart_service(self):
        """Intenta reiniciar el servicio antes de reiniciar el PC"""
        logger.warning("Intentando reiniciar el servicio...")
        try:
            if sys.platform == 'win32':
                # Intentar reiniciar usando el script existente
                script_path = Path(__file__).parent / "REINICIAR_SERVICIO.bat"
                if script_path.exists():
                    subprocess.run([str(script_path)], timeout=30)
                    time.sleep(10)  # Esperar a que el servicio se reinicie
                    return True
            return False
        except Exception as e:
            logger.error(f"Error al reiniciar servicio: {e}")
            return False
    
    def reboot_system(self):
        """Reinicia el sistema operativo"""
        logger.critical("🔴 REINICIANDO EL SISTEMA...")
        logger.critical(f"Estadísticas: {self.total_checks} verificaciones, {self.total_failures} fallos totales")
        logger.critical(f"Tiempo de ejecución: {datetime.now() - self.start_time}")
        
        try:
            if sys.platform == 'win32':
                # Windows: reinicio con delay de 10 segundos
                subprocess.run(['shutdown', '/r', '/t', '10', '/c', 
                               'DVDcoin Watchdog: Reiniciando por fallos del servidor'], 
                              check=True)
                logger.critical("Comando de reinicio enviado. El sistema se reiniciará en 10 segundos.")
            else:
                # Linux/Mac
                subprocess.run(['sudo', 'reboot'], check=True)
                logger.critical("Comando de reinicio enviado.")
        except Exception as e:
            logger.critical(f"ERROR al intentar reiniciar el sistema: {e}")
            logger.critical("ACCIÓN MANUAL REQUERIDA: Por favor reinicia el sistema manualmente")
    
    def run(self):
        """Bucle principal de monitoreo"""
        logger.info("=" * 70)
        logger.info("🐕 DVDcoin Watchdog Monitor INICIADO")
        logger.info(f"Intervalo de verificación: {CHECK_INTERVAL} segundos ({CHECK_INTERVAL//60} minutos)")
        logger.info(f"Fallos consecutivos antes de reiniciar: {MAX_FAILURES}")
        logger.info(f"Tiempo total antes de reinicio: {CHECK_INTERVAL * MAX_FAILURES // 60} minutos")
        logger.info("=" * 70)
        
        # Primera verificación inmediata
        logger.info("Realizando verificación inicial...")
        self.comprehensive_check()
        
        while True:
            try:
                # Esperar el intervalo
                logger.info(f"Próxima verificación en {CHECK_INTERVAL//60} minutos...")
                time.sleep(CHECK_INTERVAL)
                
                # Realizar verificación
                success = self.comprehensive_check()
                
                if not success:
                    if self.consecutive_failures >= MAX_FAILURES:
                        logger.critical(f"🔴 ALERTA: {MAX_FAILURES} fallos consecutivos detectados!")
                        
                        # Intentar reiniciar el servicio primero
                        logger.warning("Intentando reiniciar el servicio antes de reiniciar el PC...")
                        if self.attempt_restart_service():
                            logger.info("Servicio reiniciado. Verificando en 30 segundos...")
                            time.sleep(30)
                            
                            # Verificar si el reinicio del servicio funcionó
                            if self.comprehensive_check():
                                logger.info("✅ Servicio recuperado exitosamente. Continuando monitoreo.")
                                continue
                        
                        # Si el reinicio del servicio no funcionó, reiniciar el PC
                        logger.critical("El reinicio del servicio no funcionó. Procediendo a reiniciar el PC...")
                        self.reboot_system()
                        
                        # Esperar antes de salir (el sistema se reiniciará)
                        time.sleep(60)
                        sys.exit(1)
                    else:
                        logger.warning(f"⚠️ Fallo detectado. Esperando {CHECK_INTERVAL//60} minutos para la siguiente verificación...")
                else:
                    # Mostrar estadísticas cada hora
                    if self.total_checks % 12 == 0:  # Cada 12 verificaciones (1 hora)
                        uptime = datetime.now() - self.start_time
                        logger.info(f"📊 Estadísticas: {self.total_checks} verificaciones, {self.total_failures} fallos totales, Uptime: {uptime}")
                        if self.last_success:
                            logger.info(f"Último éxito: {self.last_success.strftime('%Y-%m-%d %H:%M:%S')}")
                
            except KeyboardInterrupt:
                logger.info("Watchdog detenido por el usuario (Ctrl+C)")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Error en el bucle principal: {e}")
                logger.error("Continuando monitoreo...")
                time.sleep(60)


if __name__ == "__main__":
    monitor = ServerMonitor()
    monitor.run()
