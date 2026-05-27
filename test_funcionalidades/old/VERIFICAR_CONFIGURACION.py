#!/usr/bin/env python3
"""
🔍 VERIFICAR CONFIGURACIÓN
Script para verificar que todo está listo para ejecutar los tests
"""
import sys
import json
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def print_section(text):
    print("\n" + "-" * 80)
    print(f"  {text}")
    print("-" * 80)

def check_python_version():
    """Verificar versión de Python"""
    print_section("1. Verificando versión de Python")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Versión de Python correcta (>= 3.8)")
        return True
    else:
        print("❌ Se requiere Python 3.8 o superior")
        return False

def check_dependencies():
    """Verificar dependencias instaladas"""
    print_section("2. Verificando dependencias")
    
    dependencies = {
        'requests': 'HTTP/REST API',
        'websocket': 'WebSockets',
        'PIL': 'Imágenes (Pillow)'
    }
    
    all_ok = True
    
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module:15} - {description}")
        except ImportError:
            print(f"❌ {module:15} - {description} (NO INSTALADO)")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Instala las dependencias faltantes con:")
        print("   pip install requests websocket-client pillow")
        print("   o ejecuta: INSTALAR_DEPENDENCIAS.bat")
    
    return all_ok

def check_config_file():
    """Verificar archivo de configuración"""
    print_section("3. Verificando archivo de configuración")
    
    config_path = Path(__file__).parent / "config.json"
    
    if not config_path.exists():
        print("❌ Archivo config.json NO encontrado")
        return False
    
    print("✅ Archivo config.json encontrado")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Verificar estructura
        required_keys = ['server', 'credentials']
        missing = [k for k in required_keys if k not in config]
        
        if missing:
            print(f"❌ Faltan claves en config.json: {', '.join(missing)}")
            return False
        
        print("✅ Estructura de config.json correcta")
        
        # Mostrar configuración
        print(f"\n📋 Configuración actual:")
        print(f"   Servidor: {config['server']['base_url']}")
        print(f"   WebSocket: {config['server']['ws_url']}")
        print(f"   Admin: {config['credentials']['admin']['username']}")
        print(f"   Usuario 1: {config['credentials']['test_user']['username']}")
        print(f"   Usuario 2: {config['credentials']['test_user2']['username']}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Error al leer config.json: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_server_connection():
    """Verificar conexión con el servidor"""
    print_section("4. Verificando conexión con el servidor")
    
    try:
        import requests
        
        config_path = Path(__file__).parent / "config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        base_url = config['server']['base_url']
        
        print(f"Conectando a {base_url}...")
        
        response = requests.get(f"{base_url}/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servidor respondiendo correctamente")
            print(f"   Estado: {data.get('status')}")
            print(f"   Timestamp: {data.get('time')}")
            return True
        else:
            print(f"❌ Servidor respondió con código {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout al conectar con el servidor")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_test_files():
    """Verificar que existan los archivos de test"""
    print_section("5. Verificando archivos de test")
    
    base_dir = Path(__file__).parent
    
    test_dirs = [
        "01_transferencias",
        "02_opo",
        "03_millonario",
        "04_video",
        "05_cifras_letras",
        "06_pasapalabra",
        "07_hundir_flota",
        "08_mensajes",
        "09_apuestas",
        "10_votaciones",
        "11_cuentos",
        "12_quien_soy",
        "13_admin",
        "14_galeria",
        "15_autenticacion"
    ]
    
    all_ok = True
    found = 0
    
    for test_dir in test_dirs:
        test_path = base_dir / test_dir
        if test_path.exists():
            found += 1
        else:
            print(f"❌ Carpeta {test_dir} NO encontrada")
            all_ok = False
    
    if all_ok:
        print(f"✅ Todos los {found} módulos de test encontrados")
    else:
        print(f"⚠️  Solo {found}/{len(test_dirs)} módulos encontrados")
    
    return all_ok

def main():
    """Función principal"""
    print_header("🔍 VERIFICACIÓN DE CONFIGURACIÓN - Tests DVDcoin Bank")
    
    results = {
        "Python": check_python_version(),
        "Dependencias": check_dependencies(),
        "Config": check_config_file(),
        "Servidor": check_server_connection(),
        "Tests": check_test_files()
    }
    
    print_header("📊 RESUMEN")
    
    for check, result in results.items():
        status = "✅ OK" if result else "❌ FALLO"
        print(f"  {status:10} {check}")
    
    all_ok = all(results.values())
    
    print("\n" + "=" * 80)
    
    if all_ok:
        print("  ✅ TODO LISTO PARA EJECUTAR LOS TESTS")
        print("\n  Ejecuta: EJECUTAR_TODOS_LOS_TESTS.bat")
    else:
        print("  ⚠️  ALGUNOS CHECKS FALLARON")
        print("\n  Revisa los errores arriba y corrígelos antes de ejecutar los tests")
    
    print("=" * 80 + "\n")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
