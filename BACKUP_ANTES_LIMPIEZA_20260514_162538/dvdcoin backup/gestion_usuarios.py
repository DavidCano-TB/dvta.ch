import sqlite3
import os
import bcrypt as _bcrypt
import tkinter as tk
from tkinter import simpledialog, messagebox

# Función idéntica a la de tu main.py v3.2
def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")[:72]
    return _bcrypt.hashpw(pwd_bytes, _bcrypt.gensalt(rounds=12)).decode("utf-8")

def gestionar():
    root = tk.Tk()
    root.withdraw()

    # Ruta exacta de tu v3.2
    db_path = r"C:\DvDcoin\data\dvdcoin.db"
    
    if not os.path.exists(db_path):
        messagebox.showerror("Error", f"No se encontró la DB en:\n{db_path}")
        return

    user = simpledialog.askstring("DVDcoin Admin", "Nombre de usuario:")
    if not user: return
    user = user.strip().lower()

    pwd = simpledialog.askstring("DVDcoin Admin", f"Nueva contraseña para {user}:", show='*')
    if not pwd: return

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        new_hash = hash_password(pwd)

        # Verificar si existe
        cursor.execute("SELECT username FROM users WHERE username = ?", (user,))
        if cursor.fetchone():
            if messagebox.askyesno("Confirmar", f"¿Cambiar contraseña de '{user}'?"):
                cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, user))
                conn.commit()
                messagebox.showinfo("Éxito", "Contraseña actualizada.")
        else:
            if messagebox.askyesno("Nuevo", f"¿Crear usuario '{user}' con saldo 0?"):
                # Insertamos con los valores por defecto de tu v3.2
                cursor.execute("INSERT INTO users (username, password_hash, balance) VALUES (?, ?, 0.0)", (user, new_hash))
                conn.commit()
                messagebox.showinfo("Éxito", f"Usuario {user} creado.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        conn.close()
        root.destroy()

if __name__ == "__main__":
    gestionar()