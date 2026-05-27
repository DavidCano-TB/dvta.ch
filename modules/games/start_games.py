"""
Script robusto para iniciar el servidor Games
Maneja errores y verifica dependencias
"""
import os
import sys
import subprocess
import time

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    required = ['fastapi', 'uvicorn', 'pydantic']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Dependencias faltantes: {', '.join(missing)}")
        print("Instalando...")
        for pkg in missing:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg])
        return False
    
    return True

def check_port(port=8002):
    """Verifica si el puerto está disponible"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0  # True si está libre

def main():
    print("=" * 80)
    print("DVDcoin Games - Starting Server")
    print("=" * 80)
    print()
    
    # Cambiar al directorio correcto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Verificar dependencias
    print("[1/3] Checking dependencies...")
    if not check_dependencies():
        print("✅ Dependencies installed")
    else:
        print("✅ All dependencies OK")
    print()
    
    # Verificar puerto
    print("[2/3] Checking port 8002...")
    if not check_port(8002):
        print("⚠️  Port 8002 is already in use")
        print("Server may already be running")
    else:
        print("✅ Port 8002 is available")
    print()
    
    # Iniciar servidor
    print("[3/3] Starting server...")
    print()
    print("=" * 80)
    print("Server starting on:")
    print("  • Local:    http://localhost:8002")
    print("  • External: https://games.dvta.ch")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    try:
        import uvicorn
        from app_games import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8002,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
