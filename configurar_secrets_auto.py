#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import base64
import sys
from nacl import encoding, public

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a secret using the repository's public key."""
    public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def configure_github_secrets(token, repo_owner, repo_name, smtp_username, smtp_password):
    """Configure GitHub secrets for the repository."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    
    # Get repository public key
    print("Obteniendo clave pública del repositorio...")
    response = requests.get(f"{base_url}/actions/secrets/public-key", headers=headers)
    
    if response.status_code != 200:
        print(f"Error obteniendo clave pública: {response.status_code}")
        print(response.text)
        return False
    
    public_key_data = response.json()
    public_key = public_key_data["key"]
    key_id = public_key_data["key_id"]
    
    # Encrypt and set SMTP_USERNAME
    print("Configurando SMTP_USERNAME...")
    encrypted_username = encrypt_secret(public_key, smtp_username)
    
    response = requests.put(
        f"{base_url}/actions/secrets/SMTP_USERNAME",
        headers=headers,
        json={
            "encrypted_value": encrypted_username,
            "key_id": key_id
        }
    )
    
    if response.status_code not in [201, 204]:
        print(f"Error configurando SMTP_USERNAME: {response.status_code}")
        print(response.text)
        return False
    
    print("✅ SMTP_USERNAME configurado")
    
    # Encrypt and set SMTP_PASSWORD
    print("Configurando SMTP_PASSWORD...")
    encrypted_password = encrypt_secret(public_key, smtp_password)
    
    response = requests.put(
        f"{base_url}/actions/secrets/SMTP_PASSWORD",
        headers=headers,
        json={
            "encrypted_value": encrypted_password,
            "key_id": key_id
        }
    )
    
    if response.status_code not in [201, 204]:
        print(f"Error configurando SMTP_PASSWORD: {response.status_code}")
        print(response.text)
        return False
    
    print("✅ SMTP_PASSWORD configurado")
    
    return True

if __name__ == "__main__":
    # Check if arguments provided
    if len(sys.argv) == 3:
        token = sys.argv[1]
        smtp_password = sys.argv[2]
    else:
        print("═══════════════════════════════════════════════════════════════")
        print(" CONFIGURACIÓN AUTOMÁTICA DE SECRETS DE GITHUB")
        print("═══════════════════════════════════════════════════════════════")
        print()
        
        # Get GitHub token
        print("Necesito un token de GitHub con permisos 'repo' y 'workflow'")
        print("Créalo en: https://github.com/settings/tokens/new")
        print()
        token = input("Token de GitHub: ").strip()
        
        if not token:
            print("❌ Token vacío")
            sys.exit(1)
        
        # Get Gmail app password
        print()
        print("Necesito la contraseña de aplicación de Gmail")
        print("Créala en: https://myaccount.google.com/apppasswords")
        print()
        smtp_password = input("Contraseña de aplicación de Gmail (16 caracteres): ").strip()
        
        if not smtp_password:
            print("❌ Contraseña vacía")
            sys.exit(1)
    
    # Configure secrets
    print()
    print("Configurando secrets...")
    print()
    
    smtp_username = "Davidcano.ch@gmail.com"
    repo_owner = "davidcano-tb"
    repo_name = "dvta.ch"
    
    success = configure_github_secrets(token, repo_owner, repo_name, smtp_username, smtp_password)
    
    if success:
        print()
        print("═══════════════════════════════════════════════════════════════")
        print(" ✅ SECRETS CONFIGURADOS CORRECTAMENTE")
        print("═══════════════════════════════════════════════════════════════")
        print()
    else:
        print()
        print("❌ Error configurando secrets")
        sys.exit(1)
