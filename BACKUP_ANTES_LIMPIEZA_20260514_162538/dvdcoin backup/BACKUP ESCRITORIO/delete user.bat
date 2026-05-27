import sqlite3
import os
import sys
import logging

# Configuración del archivo de LOG en la misma carpeta
log_path = os.path.join(os.path.dirname(__file__), "db_admin.log")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def eliminar_usuario():
    # 1. Validar si se pasó el nombre de usuario
    if len(sys.argv) < 2:
        print("\n❌ Error: Debes proporcionar un nombre de usuario.")
        print("Uso: python borrar_usuario.py [username]\n")
        return

    username = sys.argv[1]
    db_path = os.path.join("data", "database.db") # Asegúrate de que esta es la ruta a tu archivo .db

    if not os.path.exists(db_path):
        msg = f"Base de datos no encontrada en: {db_path}"
        print(f"❌ {msg}")
        logging.error(msg)
        return

    conn = None
    try:
        # 2. Conexión y ejecución
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar si el usuario existe antes de intentar borrar
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            msg = f"El usuario '{username}' no existe."
            print(f"⚠️ {msg}")
            logging.warning(msg)
            return

        # Proceder con el borrado
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        
        exito_msg = f"Usuario '{username}' eliminado correctamente de la base de datos."
        print(f"✅ {exito_msg}")
        logging.info(exito_msg)

    except sqlite3.OperationalError as e:
        err = f"Error: La base de datos está bloqueada (posiblemente el servidor esté activo). {e}"
        print(f"❌ {err}")
        logging.error(err)
    except Exception as e:
        err = f"Error inesperado: {e}"
        print(f"❌ {err}")
        logging.error(err)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    eliminar_usuario()