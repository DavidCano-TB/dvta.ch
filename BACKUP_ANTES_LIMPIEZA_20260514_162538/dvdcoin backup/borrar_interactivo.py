import sqlite3
import os
import logging
import tkinter as tk
from tkinter import simpledialog, messagebox

# Configuración de Logs
log_path = r"C:\DvDcoin\db_admin.log"
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def borrar_con_verificacion():
    root = tk.Tk()
    root.withdraw()

    db_path = r"C:\DvDcoin\data\dvdcoin.db"
    
    if not os.path.exists(db_path):
        messagebox.showerror("Error", f"No se encontró la DB en:\n{db_path}")
        return

    # 1. Pedir nombre
    username_raw = simpledialog.askstring("DVDcoin Admin", "Usuario a borrar (Confirmación doble):")
    if not username_raw: return
    username = username_raw.strip()

    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=15) # Aumentamos el tiempo de espera
        cursor = conn.cursor()

        # 2. Buscar si existe originalmente
        cursor.execute("SELECT username FROM users WHERE username = ? COLLATE NOCASE", (username,))
        res = cursor.fetchone()
        
        if not res:
            messagebox.showwarning("Error", f"El usuario '{username}' no existe en la base de datos.")
            return

        nombre_real = res[0]

        # 3. Confirmar acción
        if not messagebox.askyesno("⚠️ CUIDADO", f"¿Eliminar a '{nombre_real}'?\nEsta acción es irreversible."):
            return

        # 4. EJECUTAR BORRADO
        cursor.execute("DELETE FROM users WHERE username = ? COLLATE NOCASE", (username,))
        
        # FORZAR EL GUARDADO (COMMIT)
        conn.commit()

        # 5. COMPROBACIÓN POST-BORRADO (Crucial)
        cursor.execute("SELECT username FROM users WHERE username = ? COLLATE NOCASE", (username,))
        verificacion = cursor.fetchone()

        if verificacion:
            # Si aún existe después del DELETE y COMMIT
            msg_fail = f"FALLO CRÍTICO: El usuario '{nombre_real}' sigue en la DB a pesar del borrado."
            logging.error(msg_fail)
            messagebox.showerror("Error de Persistencia", msg_fail)
        else:
            # Si ya no se encuentra
            msg_success = f"ÉXITO: '{nombre_real}' ha sido borrado y verificado."
            logging.info(msg_success)
            messagebox.showinfo("Confirmado", msg_success)

    except sqlite3.OperationalError as e:
        err = f"Base de datos bloqueada.\nCierra uvicorn/servidor e inténtalo de nuevo.\n\nDetalle: {e}"
        logging.error(err)
        messagebox.showerror("Bloqueo de Archivo", err)
    except Exception as e:
        messagebox.showerror("Error Inesperado", f"Ocurrió un fallo: {e}")
    finally:
        if conn:
            conn.close()
        root.destroy()

if __name__ == "__main__":
    borrar_con_verificacion()