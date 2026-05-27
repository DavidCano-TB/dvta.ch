#!/usr/bin/env python3
"""
ngrok_config_manager.py - Gestor de configuración de ngrok
Lee desde config/ngrok_config.txt y escribe en conf/.ngrok_token
"""
import sys
from pathlib import Path

BASE = Path(__file__).parent
CONFIG_FILE = BASE / "config" / "ngrok_config.txt"
TOKEN_FILE = BASE / "conf" / ".ngrok_token"

# Colores para terminal
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def read_config():
    """Lee la configuración actual de ngrok desde config/ngrok_config.txt"""
    config = {"token": "", "domain": ""}
    
    if not CONFIG_FILE.exists():
        return config
    
    for line in CONFIG_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            if line.startswith("NGROK_TOKEN="):
                config["token"] = line.split("=", 1)[1].strip()
            elif line.startswith("NGROK_DOMAIN="):
                config["domain"] = line.split("=", 1)[1].strip()
    
    return config


def write_config(token, domain):
    """Escribe la configuración de ngrok en config/ngrok_config.txt y conf/.ngrok_token"""
    # Crear directorios si no existen
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Escribir en config/ngrok_config.txt (archivo principal)
    content = f"""# Configuración de ngrok para DVDcoin Bank
# Este archivo contiene el token y dominio reservado de ngrok
# Formato: VARIABLE=valor (sin espacios alrededor del =)

NGROK_TOKEN={token}
NGROK_DOMAIN={domain}
"""
    CONFIG_FILE.write_text(content, encoding="utf-8")
    print(f"{GREEN}✓ Configuración guardada en: {CONFIG_FILE}{RESET}")
    
    # Escribir en conf/.ngrok_token (para compatibilidad)
    token_content = f"NGROK_TOKEN={token}\nNGROK_DOMAIN={domain}\n"
    TOKEN_FILE.write_text(token_content, encoding="utf-8")
    print(f"{GREEN}✓ Token sincronizado en: {TOKEN_FILE}{RESET}")


def show_config():
    """Muestra la configuración actual"""
    config = read_config()
    
    print(f"\n{BOLD}Configuración actual de ngrok:{RESET}")
    print(f"  Archivo principal: {CYAN}{CONFIG_FILE}{RESET}")
    print(f"  Existe: {GREEN}Sí{RESET}" if CONFIG_FILE.exists() else f"  Existe: {RED}No{RESET}")
    print(f"  Archivo secundario: {CYAN}{TOKEN_FILE}{RESET}")
    print(f"  Existe: {GREEN}Sí{RESET}" if TOKEN_FILE.exists() else f"  Existe: {RED}No{RESET}")
    print()
    
    if config["token"]:
        # Mostrar solo los primeros y últimos caracteres del token por seguridad
        token_display = config["token"][:10] + "..." + config["token"][-10:] if len(config["token"]) > 20 else config["token"]
        print(f"  Token: {GREEN}{token_display}{RESET}")
    else:
        print(f"  Token: {RED}No configurado{RESET}")
    
    domain_value = config["domain"]
    if domain_value:
        print(f"  Dominio: {GREEN}{domain_value}{RESET}")
    else:
        print(f"  Dominio: {RED}No configurado{RESET}")
    
    print()


def update_config():
    """Actualiza la configuración de forma interactiva"""
    print(f"\n{BOLD}Actualizar configuración de ngrok{RESET}\n")
    
    current = read_config()
    
    print(f"Token actual: {current['token'][:10]}...{current['token'][-10:] if current['token'] else 'No configurado'}")
    token = input("Nuevo token (Enter para mantener actual): ").strip()
    if not token:
        token = current["token"]
    
    print(f"\nDominio actual: {current['domain'] or 'No configurado'}")
    domain = input("Nuevo dominio (Enter para mantener actual): ").strip()
    if not domain:
        domain = current["domain"]
    
    if not token:
        print(f"\n{RED}✗ Error: El token es obligatorio{RESET}")
        return
    
    write_config(token, domain)
    print(f"\n{GREEN}✓ Configuración actualizada correctamente{RESET}")


def verify_config():
    """Verifica que la configuración es válida"""
    print(f"\n{BOLD}Verificando configuración...{RESET}\n")
    
    if not CONFIG_FILE.exists():
        print(f"{RED}✗ El archivo de configuración no existe: {CONFIG_FILE}{RESET}")
        print(f"\n{YELLOW}Ejecuta: python ngrok_config_manager.py update{RESET}")
        return False
    
    config = read_config()
    
    valid = True
    
    if not config["token"]:
        print(f"{RED}✗ Token no configurado{RESET}")
        valid = False
    else:
        print(f"{GREEN}✓ Token configurado{RESET}")
    
    if not config["domain"]:
        print(f"{YELLOW}⚠ Dominio no configurado (se usará uno por defecto){RESET}")
    else:
        domain_value = config["domain"]
        print(f"{GREEN}✓ Dominio configurado: {domain_value}{RESET}")
    
    print()
    
    if valid:
        print(f"{GREEN}✓ Configuración válida{RESET}")
    else:
        print(f"{RED}✗ Configuración incompleta{RESET}")
        print(f"\n{YELLOW}Ejecuta: python ngrok_config_manager.py update{RESET}")
    
    return valid


def show_help():
    """Muestra la ayuda"""
    print(f"""
{BOLD}ngrok_config_manager.py - Gestor de configuración de ngrok{RESET}

{BOLD}Uso:{RESET}
  python ngrok_config_manager.py [comando]

{BOLD}Comandos:{RESET}
  show      Muestra la configuración actual (por defecto)
  update    Actualiza la configuración de forma interactiva
  verify    Verifica que la configuración es válida
  help      Muestra esta ayuda

{BOLD}Archivos de configuración:{RESET}
  Principal:  {CYAN}{CONFIG_FILE}{RESET}
  Secundario: {CYAN}{TOKEN_FILE}{RESET} (generado automáticamente)

{BOLD}Formato del archivo:{RESET}
  NGROK_TOKEN=tu_token_aqui
  NGROK_DOMAIN=tu_dominio.ngrok-free.dev

{BOLD}Ejemplos:{RESET}
  python ngrok_config_manager.py show
  python ngrok_config_manager.py update
  python ngrok_config_manager.py verify
""")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "show"
    
    if command == "show":
        show_config()
    elif command == "update":
        update_config()
    elif command == "verify":
        verify_config()
    elif command == "help":
        show_help()
    else:
        print(f"{RED}Comando desconocido: {command}{RESET}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
