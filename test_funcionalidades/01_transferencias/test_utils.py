"""
Utilidades comunes para todos los tests
"""
import os
import json
import logging
import requests
import websocket
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

class TestLogger:
    """Logger personalizado para tests"""
    
    def __init__(self, test_name: str, log_dir: Optional[str] = None):
        self.test_name = test_name
        
        # Si no se especifica log_dir, usar la carpeta del script que llama
        if log_dir is None:
            import inspect
            caller_frame = inspect.stack()[1]
            caller_file = caller_frame.filename
            log_dir = Path(caller_file).parent
        else:
            log_dir = Path(log_dir)
        
        self.log_dir = log_dir
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = self.log_dir / f"test_{test_name}_{timestamp}.log"
        
        # Configurar logger
        self.logger = logging.getLogger(test_name)
        self.logger.setLevel(logging.DEBUG)
        
        # Handler para archivo
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        
        # Handler para consola
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_warnings = 0
        
        self.logger.info("=" * 80)
        self.logger.info(f"🧪 INICIANDO TEST: {test_name.upper()}")
        self.logger.info("=" * 80)
    
    def success(self, message: str):
        """Log de test exitoso"""
        self.tests_passed += 1
        self.logger.info(f"✅ {message}")
    
    def fail(self, message: str, error: Optional[Exception] = None):
        """Log de test fallido"""
        self.tests_failed += 1
        self.logger.error(f"❌ {message}")
        if error:
            self.logger.error(f"   Error: {str(error)}")
    
    def warning(self, message: str):
        """Log de advertencia"""
        self.tests_warnings += 1
        self.logger.warning(f"⚠️  {message}")
    
    def info(self, message: str):
        """Log informativo"""
        self.logger.info(f"ℹ️  {message}")
    
    def debug(self, message: str):
        """Log de debug"""
        self.logger.debug(f"🔍 {message}")
    
    def section(self, title: str):
        """Separador de sección"""
        self.logger.info("")
        self.logger.info("-" * 80)
        self.logger.info(f"📋 {title}")
        self.logger.info("-" * 80)
    
    def summary(self):
        """Resumen final del test"""
        total = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total * 100) if total > 0 else 0
        
        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("📊 RESUMEN DEL TEST")
        self.logger.info("=" * 80)
        self.logger.info(f"✅ Tests exitosos:  {self.tests_passed}")
        self.logger.info(f"❌ Tests fallidos:  {self.tests_failed}")
        self.logger.info(f"⚠️  Advertencias:    {self.tests_warnings}")
        self.logger.info(f"📈 Tasa de éxito:   {success_rate:.1f}%")
        self.logger.info("=" * 80)
        
        return self.tests_failed == 0


class TestClient:
    """Cliente HTTP para tests"""
    
    def __init__(self, base_url: str, logger: TestLogger):
        self.base_url = base_url.rstrip('/')
        self.logger = logger
        self.token: Optional[str] = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': '1'
        })
    
    def login(self, username: str, password: str) -> bool:
        """Login y obtener token"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                self.logger.success(f"Login exitoso como {username}")
                return True
            else:
                self.logger.fail(f"Login fallido: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.logger.fail(f"Error en login", e)
            return False
    
    def get(self, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """GET request"""
        try:
            url = f"{self.base_url}{endpoint}"
            self.logger.debug(f"GET {url}")
            response = self.session.get(url, **kwargs)
            self.logger.debug(f"Response: {response.status_code}")
            return response
        except Exception as e:
            self.logger.fail(f"Error en GET {endpoint}", e)
            return None
    
    def post(self, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """POST request"""
        try:
            url = f"{self.base_url}{endpoint}"
            self.logger.debug(f"POST {url}")
            response = self.session.post(url, **kwargs)
            self.logger.debug(f"Response: {response.status_code}")
            return response
        except Exception as e:
            self.logger.fail(f"Error en POST {endpoint}", e)
            return None
    
    def put(self, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """PUT request"""
        try:
            url = f"{self.base_url}{endpoint}"
            self.logger.debug(f"PUT {url}")
            response = self.session.put(url, **kwargs)
            self.logger.debug(f"Response: {response.status_code}")
            return response
        except Exception as e:
            self.logger.fail(f"Error en PUT {endpoint}", e)
            return None
    
    def delete(self, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """DELETE request"""
        try:
            url = f"{self.base_url}{endpoint}"
            self.logger.debug(f"DELETE {url}")
            response = self.session.delete(url, **kwargs)
            self.logger.debug(f"Response: {response.status_code}")
            return response
        except Exception as e:
            self.logger.fail(f"Error en DELETE {endpoint}", e)
            return None


def load_config() -> Dict[str, Any]:
    """Cargar configuración de tests"""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def verify_response(response: Optional[requests.Response], 
                   expected_status: int,
                   logger: TestLogger,
                   test_name: str) -> bool:
    """Verificar respuesta HTTP"""
    if response is None:
        logger.fail(f"{test_name}: No se obtuvo respuesta")
        return False
    
    if response.status_code != expected_status:
        logger.fail(f"{test_name}: Status {response.status_code}, esperado {expected_status}")
        logger.debug(f"Response: {response.text[:500]}")
        return False
    
    logger.success(f"{test_name}: Status {response.status_code} ✓")
    return True


def verify_json_fields(data: Dict[str, Any],
                      required_fields: List[str],
                      logger: TestLogger,
                      test_name: str) -> bool:
    """Verificar que existan campos requeridos en JSON"""
    missing = [f for f in required_fields if f not in data]
    
    if missing:
        logger.fail(f"{test_name}: Faltan campos: {', '.join(missing)}")
        return False
    
    logger.success(f"{test_name}: Todos los campos presentes ✓")
    return True
