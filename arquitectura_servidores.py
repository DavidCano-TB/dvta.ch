#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquitectura de Gestión de Servidores - DVDBank
Gestiona múltiples servidores con balanceo de carga y alta disponibilidad
"""

import json
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class ServerStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"

@dataclass
class ServerConfig:
    """Configuración de un servidor"""
    name: str
    port: int
    module: str  # 'bank', 'exams', 'games', 'social'
    command: str
    health_check_url: str
    auto_restart: bool = True
    max_retries: int = 3
    status: ServerStatus = ServerStatus.STOPPED
    pid: Optional[int] = None
    
class ServerManager:
    """Gestor centralizado de servidores"""
    
    def __init__(self, config_file: str = "servers_config.json"):
        self.config_file = Path(config_file)
        self.servers: Dict[str, ServerConfig] = {}
        self.load_config()
        
    def load_config(self):
        """Carga la configuración de servidores"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for server_data in data.get('servers', []):
                    server = ServerConfig(**server_data)
                    self.servers[server.name] = server
        else:
            # Configuración por defecto
            self.create_default_config()
            
    def create_default_config(self):
        """Crea configuración por defecto"""
        default_servers = [
            ServerConfig(
                name="bank",
                port=8000,
                module="bank",
                command="python main.py",
                health_check_url="http://localhost:8000/health",
                auto_restart=True
            ),
            ServerConfig(
                name="exams",
                port=8001,
                module="exams",
                command="python modules/exams/start_exams.py",
                health_check_url="http://localhost:8001/health",
                auto_restart=True
            ),
            ServerConfig(
                name="games",
                port=8002,
                module="games",
                command="python modules/games/start_games.py",
                health_check_url="http://localhost:8002/health",
                auto_restart=True
            ),
            ServerConfig(
                name="social",
                port=8003,
                module="social",
                command="python modules/social/start_social.py",
                health_check_url="http://localhost:8003/health",
                auto_restart=True
            )
        ]
        
        for server in default_servers:
            self.servers[server.name] = server
            
        self.save_config()
        
    def save_config(self):
        """Guarda la configuración"""
        data = {
            'servers': [asdict(s) for s in self.servers.values()]
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
            
    def start_server(self, name: str) -> bool:
        """Inicia un servidor"""
        if name not in self.servers:
            print(f"❌ Servidor '{name}' no encontrado")
            return False
            
        server = self.servers[name]
        
        if server.status == ServerStatus.RUNNING:
            print(f"⚠ Servidor '{name}' ya está corriendo")
            return True
            
        print(f"🚀 Iniciando servidor '{name}' en puerto {server.port}...")
        
        try:
            # Iniciar proceso
            process = subprocess.Popen(
                server.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0
            )
            
            server.pid = process.pid
            server.status = ServerStatus.STARTING
            
            # Esperar a que el servidor esté listo
            for i in range(30):  # 30 segundos máximo
                time.sleep(1)
                if self.check_health(server):
                    server.status = ServerStatus.RUNNING
                    self.save_config()
                    print(f"✅ Servidor '{name}' iniciado correctamente (PID: {server.pid})")
                    return True
                    
            server.status = ServerStatus.ERROR
            print(f"❌ Servidor '{name}' no respondió a tiempo")
            return False
            
        except Exception as e:
            server.status = ServerStatus.ERROR
            print(f"❌ Error iniciando servidor '{name}': {e}")
            return False
            
    def stop_server(self, name: str) -> bool:
        """Detiene un servidor"""
        if name not in self.servers:
            print(f"❌ Servidor '{name}' no encontrado")
            return False
            
        server = self.servers[name]
        
        if server.status == ServerStatus.STOPPED:
            print(f"⚠ Servidor '{name}' ya está detenido")
            return True
            
        print(f"🛑 Deteniendo servidor '{name}'...")
        
        try:
            if server.pid:
                # Matar proceso
                subprocess.run(f"taskkill /F /PID {server.pid}", shell=True, capture_output=True)
                
            server.status = ServerStatus.STOPPED
            server.pid = None
            self.save_config()
            print(f"✅ Servidor '{name}' detenido")
            return True
            
        except Exception as e:
            print(f"❌ Error deteniendo servidor '{name}': {e}")
            return False
            
    def restart_server(self, name: str) -> bool:
        """Reinicia un servidor"""
        print(f"🔄 Reiniciando servidor '{name}'...")
        self.stop_server(name)
        time.sleep(2)
        return self.start_server(name)
        
    def check_health(self, server: ServerConfig) -> bool:
        """Verifica el estado de salud de un servidor"""
        try:
            response = requests.get(server.health_check_url, timeout=2)
            return response.status_code == 200
        except:
            return False
            
    def get_status(self) -> Dict:
        """Obtiene el estado de todos los servidores"""
        status = {}
        for name, server in self.servers.items():
            is_healthy = self.check_health(server) if server.status == ServerStatus.RUNNING else False
            status[name] = {
                'name': name,
                'port': server.port,
                'module': server.module,
                'status': server.status.value,
                'pid': server.pid,
                'healthy': is_healthy
            }
        return status
        
    def start_all(self):
        """Inicia todos los servidores"""
        print("🚀 Iniciando todos los servidores...")
        for name in self.servers:
            self.start_server(name)
            time.sleep(2)  # Esperar entre servidores
            
    def stop_all(self):
        """Detiene todos los servidores"""
        print("🛑 Deteniendo todos los servidores...")
        for name in self.servers:
            self.stop_server(name)
            
    def monitor(self, interval: int = 30):
        """Monitorea y reinicia servidores caídos"""
        print(f"👁 Monitoreando servidores cada {interval} segundos...")
        print("Presiona Ctrl+C para detener")
        
        try:
            while True:
                for name, server in self.servers.items():
                    if server.status == ServerStatus.RUNNING:
                        if not self.check_health(server):
                            print(f"⚠ Servidor '{name}' no responde")
                            if server.auto_restart:
                                print(f"🔄 Reiniciando servidor '{name}'...")
                                self.restart_server(name)
                                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n👋 Monitor detenido")

def main():
    """Función principal"""
    import sys
    
    manager = ServerManager()
    
    if len(sys.argv) < 2:
        print("Uso: python arquitectura_servidores.py [comando] [servidor]")
        print("\nComandos:")
        print("  start [servidor]    - Inicia un servidor")
        print("  stop [servidor]     - Detiene un servidor")
        print("  restart [servidor]  - Reinicia un servidor")
        print("  start-all           - Inicia todos los servidores")
        print("  stop-all            - Detiene todos los servidores")
        print("  status              - Muestra el estado de todos")
        print("  monitor             - Monitorea y reinicia automáticamente")
        return
        
    command = sys.argv[1]
    
    if command == "start" and len(sys.argv) > 2:
        manager.start_server(sys.argv[2])
    elif command == "stop" and len(sys.argv) > 2:
        manager.stop_server(sys.argv[2])
    elif command == "restart" and len(sys.argv) > 2:
        manager.restart_server(sys.argv[2])
    elif command == "start-all":
        manager.start_all()
    elif command == "stop-all":
        manager.stop_all()
    elif command == "status":
        status = manager.get_status()
        print("\n═══════════════════════════════════════════════════════════════")
        print(" ESTADO DE SERVIDORES")
        print("═══════════════════════════════════════════════════════════════")
        for name, info in status.items():
            health_icon = "✅" if info['healthy'] else "❌"
            print(f"\n{name.upper()}:")
            print(f"  Puerto: {info['port']}")
            print(f"  Estado: {info['status']}")
            print(f"  PID: {info['pid']}")
            print(f"  Salud: {health_icon}")
    elif command == "monitor":
        manager.monitor()
    else:
        print(f"❌ Comando desconocido: {command}")

if __name__ == "__main__":
    main()
