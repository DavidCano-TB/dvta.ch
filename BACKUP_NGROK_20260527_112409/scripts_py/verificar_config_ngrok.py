#!/usr/bin/env python3
"""
Script de verificación de configuración de ngrok
Verifica que el archivo conf/.ngrok_token esté correctamente configurado
"""
from pathlib import Path

# Colores para la consola
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def main():
    print(f"\n{CYAN}{BOLD}═══════════════════════════════════════════════════════{RESET}")
    print(f"{CYAN}{BOLD}  Verificación de Configuración de ngrok{RESET}")
    print(f"{CYAN}{BOLD}═══════════════════════════════════════════════════════{RESET}\n")
    
    BASE = Path(__file__).parent
    config_file = BASE / "conf" / ".ngrok_token"
    
    # Verificar que el archivo existe
    if not config_file.exists():
        print(f"{RED}✗ ERROR: El archivo de configuración no existe{RESET}")
        print(f"  Ubicación esperada: {config_file}")
        print(f"\n{YELLOW}Solución:{RESET}")
        print(f"  1. Crea el archivo: {config_file}")
        print(f"  2. Agrega las siguientes líneas:")
        print(f"     NGROK_TOKEN=tu_token_aqui")
        print(f"     NGROK_DOMAIN=tu_dominio.ngrok-free.dev")
        return False
    
    print(f"{GREEN}✓ Archivo de configuración encontrado{RESET}")
    print(f"  Ubicación: {config_file}\n")
    
    # Leer y verificar el contenido
    try:
        content = config_file.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        
        token = None
        domain = None
        
        for line in lines:
            if line.startswith("NGROK_TOKEN="):
                token = line.split("=", 1)[1].strip()
            elif line.startswith("NGROK_DOMAIN="):
                domain = line.split("=", 1)[1].strip()
        
        # Verificar token
        if not token:
            print(f"{RED}✗ ERROR: NGROK_TOKEN no encontrado{RESET}")
            print(f"  Agrega la línea: NGROK_TOKEN=tu_token_aqui")
            return False
        elif len(token) < 20:
            print(f"{YELLOW}⚠ ADVERTENCIA: El token parece muy corto{RESET}")
            print(f"  Token actual: {token[:10]}...")
        else:
            print(f"{GREEN}✓ NGROK_TOKEN configurado{RESET}")
            print(f"  Token: {token[:10]}...{token[-10:]}")
        
        # Verificar dominio
        if not domain:
            print(f"{RED}✗ ERROR: NGROK_DOMAIN no encontrado{RESET}")
            print(f"  Agrega la línea: NGROK_DOMAIN=tu_dominio.ngrok-free.dev")
            return False
        elif not domain.endswith(".ngrok-free.dev") and not domain.endswith(".ngrok.io"):
            print(f"{YELLOW}⚠ ADVERTENCIA: El dominio no parece ser de ngrok{RESET}")
            print(f"  Dominio actual: {domain}")
        else:
            print(f"{GREEN}✓ NGROK_DOMAIN configurado{RESET}")
            print(f"  Dominio: {domain}")
        
        # Mostrar URL completa
        if token and domain:
            print(f"\n{CYAN}{BOLD}URL pública que se usará:{RESET}")
            print(f"  https://{domain}")
            print(f"\n{GREEN}✓ Configuración válida{RESET}")
            print(f"\n{CYAN}Para iniciar el servidor, ejecuta:{RESET}")
            print(f"  python start.py")
            print(f"  o")
            print(f"  ARRANCAR.bat")
            return True
        
    except Exception as e:
        print(f"{RED}✗ ERROR al leer el archivo: {e}{RESET}")
        return False
    
    print(f"\n{CYAN}{BOLD}═══════════════════════════════════════════════════════{RESET}\n")
    return False

if __name__ == "__main__":
    success = main()
    if not success:
        print(f"\n{RED}La configuración tiene errores. Por favor corrígelos antes de continuar.{RESET}\n")
        exit(1)
    else:
        print()
        exit(0)
