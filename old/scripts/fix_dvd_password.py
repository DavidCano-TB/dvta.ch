#!/usr/bin/env python3
import sqlite3
import bcrypt

# Verificar y corregir la contraseña de dvd
conn = sqlite3.connect('data/users.db')
cursor = conn.cursor()

print("=" * 70)
print("VERIFICANDO Y CORRIGIENDO CONTRASEÑA DE 'dvd'")
print("=" * 70)

# Ver el hash actual
cursor.execute("SELECT username, password_hash FROM users WHERE username='dvd'")
row = cursor.fetchone()

if row:
    username, current_hash = row
    print(f"\nUsuario: {username}")
    print(f"Hash actual: {current_hash[:60]}...")
    
    # Probar contraseñas
    passwords_to_test = ["3666", "dvd", "password", "admin"]
    
    print("\nProbando contraseñas:")
    for pwd in passwords_to_test:
        try:
            if bcrypt.checkpw(pwd.encode('utf-8'), current_hash.encode('utf-8')):
                print(f"  ✓ '{pwd}' - FUNCIONA")
            else:
                print(f"  ✗ '{pwd}' - No funciona")
        except Exception as e:
            print(f"  ✗ '{pwd}' - Error: {e}")
    
    # Generar nuevo hash para 3666
    print("\n" + "=" * 70)
    print("GENERANDO NUEVO HASH PARA '3666'")
    print("=" * 70)
    
    new_password = "3666"
    new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    print(f"\nNuevo hash generado: {new_hash[:60]}...")
    
    # Actualizar en la base de datos
    cursor.execute("UPDATE users SET password_hash=? WHERE username='dvd'", (new_hash,))
    conn.commit()
    
    print("\n✅ Contraseña actualizada en la base de datos")
    
    # Verificar que funciona
    cursor.execute("SELECT password_hash FROM users WHERE username='dvd'")
    updated_hash = cursor.fetchone()[0]
    
    if bcrypt.checkpw(new_password.encode('utf-8'), updated_hash.encode('utf-8')):
        print("✅ Verificación exitosa: La contraseña '3666' ahora funciona")
    else:
        print("❌ ERROR: La verificación falló")
else:
    print("\n❌ Usuario 'dvd' no encontrado")

conn.close()

print("\n" + "=" * 70)
print("REINICIA EL SERVIDOR PARA APLICAR LOS CAMBIOS")
print("=" * 70)
