#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DVDcoin Watchdog Monitor - Versión Definitiva
Monitorea el servidor cada 15 minutos con tests reales
Reinicia automáticamente si hay problemas
"""

import time
import requests
import subprocess
import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════
CHECK_INTERVAL = 900  # 15 minutos
MAX_FAILURES = 2      # Fallos antes de reiniciar
BASE_URL = "http://127.0.0.1:8000"
NGROK_API = "http://localhost:4040/api/tunnels"
BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "logs" / "watchdog.log"
RESTART_SCRIPT = BASE_DIR / "KILL_ALL_AND_RESTART.bat"

# Crear directorio de logs
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
        self.total_restarts = 0
        self.last_success = None
        self.last_restart = None
        self.start_time = datetime.now()
        self.last_ngrok_url = None
        
    def check_port(self, port, timeout=3):
        """Verifica si un puerto está escuchando"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.warning(f"Error verificando puerto {port}: {e}")
            return False
    
    def check_process(self, process_name):
        """Verifica si un proceso está corriendo"""
        try:
            if sys.platform == 'win32':
                result = subprocess.run(
                    ['tasklist', '/FI', f'IMAGENAME eq {process_name}'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return process_name.lower() in result.stdout.lower()
            else:
                result = subprocess.run(
                    ['pgrep', '-f', process_name.replace('.exe', '')],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
        except Exception as e:
            logger.warning(f"Error verificando proceso {process_name}: {e}")
            return False
    
    def get_ngrok_url(self):
        """Obtiene la URL pública de ngrok"""
        try:
            response = requests.get(NGROK_API, timeout=5)
            if response.status_code != 200:
                return None
            
            data = response.json()
            tunnels = data.get("tunnels", [])
            
            if not tunnels:
                return None
            
            # Preferir HTTPS
            for tunnel in tunnels:
                url = tunnel.get("public_url", "")
                if url.startswith("https:"):
                    return url
            
            # Fallback a cualquier URL
            return tunnels[0].get("public_url") if tunnels else None
            
        except Exception as e:
            logger.warning(f"Error obteniendo URL de ngrok: {e}")
            return None
    
    def test_endpoint(self, endpoint, timeout=10):
        """Test un endpoint específico"""
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except Exception:
            return False
    
    def test_ngrok_url(self, url):
        """Test que la URL de ngrok responda"""
        try:
            response = requests.get(url, timeout=15, allow_redirects=True)
            return response.status_code in [200, 302, 307]
        except Exception:
            return False
    
    def comprehensive_check(self):
        """Verificación completa del sistema"""
        logger.info("=" * 70)
        logger.info(f"🔍 VERIFICACIÓN COMPLETA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)
        
        results = {}
        critical_failed = False
        
        # CHECK 1: Puerto 8000
        logger.info("Verificando puerto 8000...")
        results["Puerto 8000"] = self.check_port(8000)
        if not results["Puerto 8000"]:
            logger.error("  ❌ Puerto 8000 no responde")
            critical_failed = True
        else:
            logger.info("  ✅ Puerto 8000 OK")
        
        # CHECK 2: Proceso Python
        logger.info("Verificando proceso Python...")
        results["Proceso Python"] = self.check_process("python.exe")
        if not results["Proceso Python"]:
            logger.error("  ❌ Proceso Python no encontrado")
            critical_failed = True
        else:
            logger.info("  ✅ Proceso Python OK")
        
        # CHECK 3: Proceso ngrok
        logger.info("Verificando proceso ngrok...")
        results["Proceso ngrok"] = self.check_process("ngrok.exe")
        if not results["Proceso ngrok"]:
            logger.warning("  ⚠️  Proceso ngrok no encontrado")
        else:
            logger.info("  ✅ Proceso ngrok OK")
        
        # CHECK 4: Endpoints de API
        logger.info("Verificando endpoints de API...")
        api_tests = {
            "/api/health": self.test_endpoint("/api/health"),
            "/api/ice-servers": self.test_endpoint("/api/ice-servers"),
            "/api/rooms/list": self.test_endpoint("/api/rooms/list"),
        }
        
        api_passed = sum(1 for v in api_tests.values() if v)
        api_total = len(api_tests)
        
        for endpoint, passed in api_tests.items():
            if passed:
                logger.info(f"  ✅ {endpoint} OK")
            else:
                logger.error(f"  ❌ {endpoint} FALLO")
        
        results["API Endpoints"] = api_passed >= (api_total * 0.7)  # 70% deben pasar
        
        # CHECK 5: URL de ngrok
        logger.info("Verificando URL de ngrok...")
        ngrok_url = self.get_ngrok_url()
        
        if ngrok_url:
            logger.info(f"  URL encontrada: {ngrok_url}")
            self.last_ngrok_url = ngrok_url
            
            # Guardar URL
            url_file = LOG_FILE.parent / "current_url.txt"
            try:
                with open(url_file, 'w', encoding='utf-8') as f:
                    f.write(ngrok_url)
            except Exception:
                pass
            
            # Test que la URL responda
            if self.test_ngrok_url(ngrok_url):
                logger.info("  ✅ URL de ngrok responde OK")
                results["URL ngrok"] = True
            else:
                logger.error("  ❌ URL de ngrok no responde")
                results["URL ngrok"] = False
        else:
            logger.error("  ❌ No se pudo obtener URL de ngrok")
            results["URL ngrok"] = False
        
        # RESUMEN
        logger.info("-" * 70)
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        logger.info(f"RESULTADO: {passed}/{total} checks pasados ({success_rate:.1f}%)")
        
        self.total_checks += 1
        
        # Consideramos exitoso si:
        # - No hay fallos críticos (puerto 8000 y proceso Python)
        # - Al menos 60% de los checks pasan
        success = not critical_failed and success_rate >= 60
        
        if success:
            logger.info("✅ VERIFICACIÓN EXITOSA")
            self.consecutive_failures = 0
            self.last_success = datetime.now()
        else:
            self.consecutive_failures += 1
            self.total_failures += 1
            logger.error(f"❌ VERIFICACIÓN FALLIDA (Fallos consecutivos: {self.consecutive_failures}/{MAX_FAILURES})")
        
        logger.info("=" * 70)
        return success
    
    def restart_server(self):
        """Reinicia el servidor usando el script"""
        logger.critical("=" * 70)
        logger.critical("🔄 REINICIANDO SERVIDOR")
        logger.critical("=" * 70)
        logger.critical(f"Estadísticas: {self.total_checks} checks, {self.total_failures} fallos, {self.total_restarts} reinicios")
        
        if not RESTART_SCRIPT.exists():
            logger.critical(f"❌ ERROR: Script no encontrado: {RESTART_SCRIPT}")
            logger.critical("ACCIÓN MANUAL REQUERIDA")
            return False
        
        try:
            self.total_restarts += 1
            self.last_restart = datetime.now()
            
            logger.info(f"Ejecutando: {RESTART_SCRIPT}")
            
            # Ejecutar como administrador
            if sys.platform == 'win32':
                # Usar PowerShell para ejecutar como admin
                ps_cmd = f'Start-Process -FilePath "{RESTART_SCRIPT}" -Verb RunAs -Wait'
                result = subprocess.run(
                    ['powershell', '-Command', ps_cmd],
                    timeout=180,
                    capture_output=True,
                    text=True
                )
                
                logger.info("Script ejecutado")
                logger.info("Esperando 40 segundos para que el servidor inicie...")
                time.sleep(40)
                
                # Verificar si funcionó
                logger.info("Verificando si el servidor se reinició...")
                if self.comprehensive_check():
                    logger.info("✅ SERVIDOR REINICIADO EXITOSAMENTE")
                    return True
                else:
                    logger.error("❌ El servidor no se reinició correctamente")
                    return False
            else:
                subprocess.run([str(RESTART_SCRIPT)], timeout=180)
                time.sleep(40)
                return self.comprehensive_check()
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout al ejecutar script")
            return False
        except Exception as e:
            logger.critical(f"❌ ERROR: {e}")
            logger.critical("ACCIÓN MANUAL REQUERIDA")
            return False
    
    def run(self):
        """Bucle principal"""
        logger.info("=" * 70)
        logger.info("🐕 DVDCOIN WATCHDOG MONITOR - VERSIÓN DEFINITIVA")
        logger.info("=" * 70)
        logger.info(f"Intervalo: {CHECK_INTERVAL//60} minutos")
        logger.info(f"Fallos antes de reiniciar: {MAX_FAILURES}")
        logger.info(f"Script de reinicio: {RESTART_SCRIPT}")
        logger.info(f"Log: {LOG_FILE}")
        logger.info("=" * 70)
        
        # Primera verificación después de 10 segundos
        logger.info("Esperando 10 segundos antes de la primera verificación...")
        time.sleep(10)
        self.comprehensive_check()
        
        while True:
            try:
                # Esperar intervalo
                next_check = datetime.now().timestamp() + CHECK_INTERVAL
                next_time = datetime.fromtimestamp(next_check).strftime('%H:%M:%S')
                logger.info(f"💤 Próxima verificación a las {next_time}")
                time.sleep(CHECK_INTERVAL)
                
                # Verificar
                success = self.comprehensive_check()
                
                if not success:
                    if self.consecutive_failures >= MAX_FAILURES:
                        logger.critical(f"🔴 ALERTA: {MAX_FAILURES} fallos consecutivos")
                        logger.critical("Procediendo a reiniciar...")
                        
                        if self.restart_server():
                            logger.info("✅ Servidor recuperado. Continuando monitoreo.")
                        else:
                            logger.critical("❌ No se pudo recuperar el servidor")
                            logger.critical("Esperando 10 minutos antes de reintentar...")
                            time.sleep(600)
                    else:
                        logger.warning(f"⚠️  Fallo detectado. Esperando próxima verificación...")
                else:
                    # Estadísticas cada 4 checks (1 hora)
                    if self.total_checks % 4 == 0:
                        uptime = datetime.now() - self.start_time
                        hours = int(uptime.total_seconds() // 3600)
                        minutes = int((uptime.total_seconds() % 3600) // 60)
                        logger.info(f"📊 Stats: {self.total_checks} checks, {self.total_failures} fallos, {self.total_restarts} reinicios, Uptime: {hours}h {minutes}m")
                        if self.last_ngrok_url:
                            logger.info(f"URL actual: {self.last_ngrok_url}")
                
            except KeyboardInterrupt:
                logger.info("Watchdog detenido por usuario (Ctrl+C)")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Error en bucle principal: {e}")
                logger.error("Continuando...")
                time.sleep(60)


if __name__ == "__main__":
    monitor = ServerMonitor()
    monitor.run()
