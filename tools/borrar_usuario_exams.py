"""
Borrar usuario de la base de datos de Exams.
Uso: python borrar_usuario_exams.py
Te pedirá el email o username del usuario a borrar.
"""
import sqlite3, os, sys

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "modules", "exams", "data", "users_exams.db")

if not os.path.exists(DB_PATH):
    print(f"ERROR: No se encuentra la BD: {DB_PATH}")
    input("Pulsa Enter para salir...")
    sys.exit(1)

print("=" * 50)
print("  BORRAR USUARIO DE EXAMS")
print("=" * 50)
print(f"\nBD: {DB_PATH}\n")

# Listar usuarios
c = sqlite3.connect(DB_PATH)
c.row_factory = sqlite3.Row
users = c.execute("SELECT id, username, email, verified, role FROM users ORDER BY username").fetchall()
print(f"Usuarios registrados ({len(users)}):")
print("-" * 50)
for u in users:
    v = "✅" if u["verified"] else "❌"
    print(f"  {u['id']:3d} | {u['username']:20s} | {u['email']:30s} | {v} | {u['role']}")
print("-" * 50)

# Pedir usuario a borrar
query = input("\nEmail o username a borrar (o 'q' para salir): ").strip()
if not query or query.lower() == 'q':
    c.close()
    sys.exit(0)

# Buscar
row = c.execute("SELECT * FROM users WHERE email=? OR username=?", (query, query)).fetchone()
if not row:
    print(f"\n❌ No se encontró usuario con '{query}'")
    c.close()
    input("Pulsa Enter para salir...")
    sys.exit(1)

print(f"\n¿Borrar a @{row['username']} ({row['email']})? (s/n): ", end="")
confirm = input().strip().lower()
if confirm != 's':
    print("Cancelado.")
    c.close()
    sys.exit(0)

c.execute("DELETE FROM users WHERE id=?", (row['id'],))
c.commit()
c.close()
print(f"\n✅ Usuario @{row['username']} ({row['email']}) BORRADO")
input("\nPulsa Enter para salir...")
