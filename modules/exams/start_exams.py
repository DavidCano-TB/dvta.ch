"""
Script robusto para iniciar el servidor Exams
Maneja errores y verifica dependencias
"""
import os
import sys
import subprocess
import time

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    required = ['fastapi', 'uvicorn', 'pydantic', 'bcrypt', 'jose']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Dependencias faltantes: {', '.join(missing)}")
        print("Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return False
    
    return True

def check_port(port=8001):
    """Verifica si el puerto está disponible"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0  # True si está libre

def main():
    print("=" * 80)
    print("DVDcoin Exams - Starting Server")
    print("=" * 80)
    print()
    
    # Cambiar al directorio correcto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Verificar dependencias
    print("[1/3] Checking dependencies...")
    if not check_dependencies():
        print("✅ Dependencies installed")
        # Reintentar importar
        try:
            import fastapi
        except ImportError:
            print("❌ Failed to install dependencies")
            return 1
    else:
        print("✅ All dependencies OK")
    print()
    
    # Verificar puerto
    print("[2/3] Checking port 8001...")
    if not check_port(8001):
        print("⚠️  Port 8001 is already in use")
        print("Attempting to free it...")
        if os.name == 'nt':  # Windows
            subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            if not check_port(8001):
                print("❌ Could not free port 8001")
                return 1
    print("✅ Port 8001 is available")
    print()
    
    # Iniciar servidor
    print("[3/3] Starting server...")
    print()
    print("=" * 80)
    print("Server starting on:")
    print("  • Local:    http://localhost:8001")
    print("  • External: https://dvta.ch")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    try:
        import uvicorn
        from app_exams import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
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
