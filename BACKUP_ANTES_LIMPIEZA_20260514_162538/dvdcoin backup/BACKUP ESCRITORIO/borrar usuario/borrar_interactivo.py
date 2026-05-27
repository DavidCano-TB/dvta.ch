import sqlite3
import os
import logging
import tkinter as tk
from tkinter import simpledialog, messagebox

# 1. Configuración de Logs
log_path = os.path.join(os.path.dirname(__file__), "db_admin.log")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def borrar_usuario_ventana():
    # Crear una ventana oculta de Tkinter para los diálogos
    root = tk.Tk()
    root.withdraw()

    # 2. Preguntar el nombre de usuario en una ventana
    username = simpledialog.askstring("DVDcoin Admin", "Introduce el nombre de usuario a BORRAR:")

    if not username:
        return # Usuario canceló o dejó vacío

    db_path = os.path.join("data", "database.db")

    if not os.path.exists(db_path):
        messagebox.showerror("Error", f"No se encontró la DB en:\n{db_path}")
        return

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 3. Verificar si el usuario existe
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            messagebox.showwarning("No encontrado", f"El usuario '{username}' no existe.")
            return

        # 4. Confirmación final
        confirmar = messagebox.askyesno("Confirmar", f"¿Estás seguro de borrar permanentemente a '{username}'?")
        
        if confirmar:
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            
            msg = f"Usuario '{username}' eliminado con éxito."
            logging.info(msg)
            messagebox.showinfo("Éxito", msg)
        else:
            logging.info(f"Borrado de '{username}' cancelado por el admin.")

    except sqlite3.OperationalError:
        err = "Error: La base de datos está bloqueada.\nCierra el servidor antes de borrar."
        logging.error(err)
        messagebox.showerror("DB Bloqueada", err)
    except Exception as e:
        err = f"Error inesperado: {e}"
        logging.error(err)
        messagebox.showerror("Error", err)
    finally:
        if conn:
            conn.close()
        root.destroy()

if __name__ == "__main__":
    borrar_usuario_ventana()