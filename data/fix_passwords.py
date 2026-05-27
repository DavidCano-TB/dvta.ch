#!/usr/bin/env python3
"""
DVDcoin Bank — reset de contraseñas de admins
Ejecutar en el servidor: python3 fix_passwords.py
"""
import os, sqlite3, bcrypt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "data", "users.db")

# ── Contraseñas temporales para cada admin ────────────────────────────────────
# Cámbialas después del primer login
ADMIN_PASSWORDS = {
    "dvd":      "dvd2024",
    "nebulosa": "nebulosa2024",
    "nina":     "nina2024",
    "victor":   "victor2024",
    "yu":       "yu2024",
    "roy":      "roy2024",
    "aitor":    "aitor2024",
}
# El usuario ghost "admin" usa su contraseña especial — no se toca

# ─────────────────────────────────────────────────────────────────────────────

def hash_pwd(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ No se encuentra la base de datos en: {DB_PATH}")
        print(f"   Asegúrate de ejecutar este script desde la carpeta de la app.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    print(f"✅ DB encontrada: {DB_PATH}")
    print()

    updated = []
    created = []

    for username, password in ADMIN_PASSWORDS.items():
        row = conn.execute(
            "SELECT username, password_hash FROM users WHERE username=?", (username,)
        ).fetchone()

        new_hash = hash_pwd(password)

        if row:
            conn.execute(
                "UPDATE users SET password_hash=?, failed_attempts=0, locked_until=NULL, is_blocked=0 WHERE username=?",
                (new_hash, username)
            )
            updated.append(username)
        else:
            # Admin no existe en la DB — crearle una entrada
            conn.execute(
                "INSERT INTO users(username, password_hash, balance) VALUES(?,?,0.0)",
                (username, new_hash)
            )
            created.append(username)

    conn.commit()

    # Verificar que las contraseñas funcionan
    print("Verificando contraseñas reseteadas:")
    all_ok = True
    for username, password in ADMIN_PASSWORDS.items():
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username=?", (username,)
        ).fetchone()
        if row:
            ok = bcrypt.checkpw(password.encode(), row["password_hash"].encode())
            status = "✅" if ok else "❌"
            if not ok: all_ok = False
            print(f"  {status} {username:12} → contraseña: {password}")
        else:
            print(f"  ❌ {username} NO encontrado en DB")
            all_ok = False

    conn.close()

    print()
    if updated: print(f"Actualizados: {', '.join(updated)}")
    if created: print(f"Creados:      {', '.join(created)}")
    print()

    if all_ok:
        print("✅ Todo correcto. Reinicia el servidor y prueba a hacer login.")
    else:
        print("⚠️  Algunos hashes no verificaron correctamente. Revisa los errores arriba.")

    print()
    print("Contraseñas temporales:")
    print("-" * 35)
    for u, p in ADMIN_PASSWORDS.items():
        print(f"  {u:15} → {p}")
    print("-" * 35)
    print("¡Cámbialas después del primer login!")

if __name__ == "__main__":
    main()
