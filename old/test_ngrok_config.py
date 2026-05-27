#!/usr/bin/env python3
"""
test_ngrok_config.py - Script de prueba para verificar la configuración de ngrok
"""
import sys
from pathlib import Path

# Importar la función de start.py
sys.path.insert(0, str(Path(__file__).parent))

# Colores
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

def test_config():
    """Prueba la función get_ngrok_config de start.py"""
    print(f"\n{BOLD}=== Test de configuración de ngrok ==={RESET}\n")
    
    # Importar la función
    try:
        from start import get_ngrok_config
        print(f"{GREEN}✓ Función get_ngrok_config importada correctamente{RESET}")
    except Exception as e:
        print(f"{RED}✗ Error al importar: {e}{RESET}")
        return False
    
    # Obtener configuración
    try:
        config = get_ngrok_config()
        print(f"{GREEN}✓ Configuración obtenida correctamente{RESET}\n")
    except Exception as e:
        print(f"{RED}✗ Error al obtener configuración: {e}{RESET}")
        return False
    
    # Mostrar configuración
    print(f"{BOLD}Configuración leída:{RESET}")
    
    if config["token"]:
        token_display = config["token"][:10] + "..." + config["token"][-10:] if len(config["token"]) > 20 else config["token"]
        print(f"  Token: {GREEN}{token_display}{RESET}")
    else:
        print(f"  Token: {RED}No configurado{RESET}")
    
    if config["domain"]:
        print(f"  Dominio: {GREEN}{config['domain']}{RESET}")
    else:
        print(f"  Dominio: {YELLOW}No configurado (se usará por defecto){RESET}")
    
    print()
    
    # Verificar que los valores son correctos
    if not config["token"]:
        print(f"{RED}✗ FALLO: Token no configurado{RESET}")
        return False
    
    print(f"{GREEN}✓ Test completado exitosamente{RESET}")
    print(f"\n{CYAN}El sistema está listo para usar ngrok con la configuración de conf/.ngrok_token{RESET}\n")
    return True


if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)
