"""
DVDcoin Platform - Main Router
Enruta peticiones a los diferentes módulos según el dominio/path
"""
import os
import sys
import subprocess
import time
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("router")

# Configuración de módulos
MODULES = {
    "bank": {
        "port": 8000,
        "script": "main.py",
        "cwd": ".",
        "domains": ["dvdbank.com", "localhost:8000"],
        "enabled": True
    },
    "exams": {
        "port": 8001,
        "script": "modules/exams/app_exams.py",
        "cwd": "modules/exams",
        "domains": ["dvta.ch", "localhost:8001"],
        "enabled": True
    },
    "games": {
        "port": 8002,
        "script": "modules/games/app_games.py",
        "cwd": "modules/games",
        "domains": ["games.dvdbank.com", "localhost:8002"],
        "enabled": False  # Pendiente de implementar
    }
}

class ModuleManager:
    """Gestor de módulos de la plataforma"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
    
    def start_module(self, name: str, config: dict) -> bool:
        """Inicia un módulo"""
        if not config.get("enabled", False):
            logger.info(f"Module {name} is disabled, skipping")
            return False
        
        script_path = os.path.join(self.base_dir, config["script"])
        if not os.path.exists(script_path):
            logger.error(f"Script not found: {script_path}")
            return False
        
        cwd = os.path.join(self.base_dir, config["cwd"])
        
        try:
            logger.info(f"Starting {name} on port {config['port']}...")
            
            # Iniciar proceso
            process = subprocess.Popen(
                [sys.executable, script_path],
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            self.processes[name] = process
            
            # Esperar un poco para verificar que inició
            time.sleep(2)
            
            if process.poll() is None:
                logger.info(f"✅ {name.upper()} started successfully on port {config['port']}")
                logger.info(f"   Domains: {', '.join(config['domains'])}")
                return True
            else:
                logger.error(f"❌ {name.upper()} failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Error starting {name}: {e}")
            return False
    
    def stop_module(self, name: str):
        """Detiene un módulo"""
        if name in self.processes:
            process = self.processes[name]
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            del self.processes[name]
            logger.info(f"Stopped {name}")
    
    def stop_all(self):
        """Detiene todos los módulos"""
        for name in list(self.processes.keys()):
            self.stop_module(name)
    
    def start_all(self):
        """Inicia todos los módulos habilitados"""
        logger.info("=" * 80)
        logger.info("DVDcoin Platform - Starting all modules")
        logger.info("=" * 80)
        
        success_count = 0
        for name, config in MODULES.items():
            if self.start_module(name, config):
                success_count += 1
        
        logger.info("=" * 80)
        logger.info(f"Started {success_count}/{len([m for m in MODULES.values() if m['enabled']])} modules")
        logger.info("=" * 80)
        
        return success_count > 0
    
    def status(self):
        """Muestra el estado de todos los módulos"""
        logger.info("\nModule Status:")
        logger.info("-" * 80)
        for name, config in MODULES.items():
            if not config.get("enabled", False):
                status = "DISABLED"
            elif name in self.processes and self.processes[name].poll() is None:
                status = f"RUNNING (port {config['port']})"
            else:
                status = "STOPPED"
            logger.info(f"  {name.upper():10} - {status}")
        logger.info("-" * 80)


def main():
    """Función principal"""
    manager = ModuleManager()
    
    try:
        # Iniciar todos los módulos
        if not manager.start_all():
            logger.error("Failed to start any modules")
            return 1
        
        # Mostrar estado
        manager.status()
        
        # Mantener el script corriendo
        logger.info("\nPress Ctrl+C to stop all modules")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        manager.stop_all()
        logger.info("All modules stopped")
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        manager.stop_all()
        return 1


if __name__ == "__main__":
    sys.exit(main())
