#!/usr/bin/env python3
"""
👥 CREAR USUARIOS DE PRUEBA
Crea automáticamente los usuarios necesarios para los tests
"""
import requests
import json
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def crear_usuario(base_url, username, password):
    """Intenta crear un usuario"""
    try:
        response = requests.post(
            f"{base_url}/api/register",
            json={"username": username, "password": password},
            headers={'ngrok-skip-browser-warning': '1'},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Usuario '{username}' creado exitosamente")
            return True
        elif response.status_code == 400 and "already exists" in response.text.lower():
            print(f"ℹ️  Usuario '{username}' ya existe")
            return True
        else:
            print(f"❌ Error creando '{username}': {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ No se pudo conectar al servidor en {base_url}")
        print(f"   Asegúrate de que el servidor esté ejecutándose (ARRANCAR.bat)")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def verificar_login(base_url, username, password):
    """Verifica que el usuario pueda hacer login"""
    try:
        response = requests.post(
            f"{base_url}/api/login",
            json={"username": username, "password": password},
            headers={'ngrok-skip-browser-warning': '1'},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Login verificado para '{username}'")
            return True
        else:
            print(f"⚠️  Login falló para '{username}': {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verificando login: {e}")
        return False

def main():
    print_header("👥 CREAR USUARIOS DE PRUEBA")
    
    # Cargar configuración
    config_path = Path(__file__).parent / "config.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró config.json")
        print("   Ejecuta primero: python PREPARAR_TESTS.py")
        return False
    
    base_url = config['server']['base_url']
    
    print(f"Servidor: {base_url}")
    print()
    
    # Verificar conexión al servidor
    print("🔍 Verificando conexión al servidor...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print("✅ Servidor accesible")
    except:
        print("❌ No se pudo conectar al servidor")
        print()
        print("⚠️  IMPORTANTE: Debes iniciar el servidor primero")
        print("   Ejecuta en otra ventana: ARRANCAR.bat")
        print()
        input("Presiona Enter cuando el servidor esté ejecutándose...")
        print()
    
    # Crear usuarios de prueba
    print("👥 Creando usuarios de prueba...")
    print()
    
    usuarios = [
        (config['credentials']['test_user']['username'], 
         config['credentials']['test_user']['password']),
        (config['credentials']['test_user2']['username'], 
         config['credentials']['test_user2']['password'])
    ]
    
    exitos = 0
    
    for username, password in usuarios:
        if crear_usuario(base_url, username, password):
            exitos += 1
    
    print()
    
    # Verificar logins
    if exitos > 0:
        print("🔐 Verificando logins...")
        print()
        
        for username, password in usuarios:
            verificar_login(base_url, username, password)
    
    print()
    print_header("📊 RESUMEN")
    
    print(f"Usuarios procesados: {len(usuarios)}")
    print(f"✅ Exitosos: {exitos}")
    print(f"❌ Fallidos: {len(usuarios) - exitos}")
    
    if exitos == len(usuarios):
        print()
        print("🎉 ¡Todos los usuarios están listos!")
        print()
        print("Ahora puedes ejecutar los tests:")
        print("  EJECUTAR_TODOS_LOS_TESTS.bat")
        print()
        return True
    else:
        print()
        print("⚠️  Algunos usuarios no se pudieron crear")
        print("   Verifica que el servidor esté ejecutándose")
        print()
        return False

if __name__ == "__main__":
    import sys
    success = main()
    input("\nPresiona Enter para continuar...")
    sys.exit(0 if success else 1)
