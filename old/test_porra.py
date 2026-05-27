import sqlite3
import json

# Conectar a la base de datos
db_bets = sqlite3.connect('data/apuestas.db')
db_bets.row_factory = sqlite3.Row

# Ver porras abiertas
print('=== PORRAS ABIERTAS ===')
porras = db_bets.execute('SELECT id, titulo, estado FROM porras WHERE estado = "abierta" ORDER BY id DESC LIMIT 3').fetchall()
for p in porras:
    print(f'ID: {p["id"]}, Título: {p["titulo"]}, Estado: {p["estado"]}')
    
    # Ver apuestas de esta porra
    apuestas = db_bets.execute('SELECT username, opcion, cantidad FROM apuestas_usuarios WHERE porra_id = ?', (p['id'],)).fetchall()
    if apuestas:
        print(f'  Apuestas:')
        for a in apuestas:
            print(f'    - {a["username"]}: {a["cantidad"]} DVDc en "{a["opcion"]}"')
        
        # Ver opciones disponibles
        opciones_json = db_bets.execute('SELECT opciones_json FROM porras WHERE id = ?', (p['id'],)).fetchone()
        if opciones_json and opciones_json[0]:
            opciones = json.loads(opciones_json[0])
            print(f'  Opciones disponibles:')
            for i, o in enumerate(opciones, 1):
                print(f'    {i}. {o["nombre"]} (valor: {o["valor"]})')
    else:
        print(f'  Sin apuestas')
    print()

db_bets.close()
