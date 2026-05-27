"""
Script to generate comprehensive translations for all HTML files
Extracts text content and generates translation keys
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# Base translations that already exist
EXISTING_KEYS = set()

# Common game translations to add
GAME_TRANSLATIONS = {
    # Common UI
    "loading": {"es": "Cargando...", "en": "Loading...", "fr": "Chargement...", "ca": "Carregant...", "eu": "Kargatzen...", "de": "Laden...", "it": "Caricamento..."},
    "error": {"es": "Error", "en": "Error", "fr": "Erreur", "ca": "Error", "eu": "Errorea", "de": "Fehler", "it": "Errore"},
    "success": {"es": "Éxito", "en": "Success", "fr": "Succès", "ca": "Èxit", "eu": "Arrakasta", "de": "Erfolg", "it": "Successo"},
    "close": {"es": "Cerrar", "en": "Close", "fr": "Fermer", "ca": "Tancar", "eu": "Itxi", "de": "Schließen", "it": "Chiudi"},
    "save": {"es": "Guardar", "en": "Save", "fr": "Enregistrer", "ca": "Desar", "eu": "Gorde", "de": "Speichern", "it": "Salva"},
    "cancel": {"es": "Cancelar", "en": "Cancel", "fr": "Annuler", "ca": "Cancel·lar", "eu": "Ezeztatu", "de": "Abbrechen", "it": "Annulla"},
    "confirm": {"es": "Confirmar", "en": "Confirm", "fr": "Confirmer", "ca": "Confirmar", "eu": "Berretsi", "de": "Bestätigen", "it": "Conferma"},
    "yes": {"es": "Sí", "en": "Yes", "fr": "Oui", "ca": "Sí", "eu": "Bai", "de": "Ja", "it": "Sì"},
    "no": {"es": "No", "en": "No", "fr": "Non", "ca": "No", "eu": "Ez", "de": "Nein", "it": "No"},
    "ok": {"es": "OK", "en": "OK", "fr": "OK", "ca": "D'acord", "eu": "Ados", "de": "OK", "it": "OK"},
    
    # Game specific - Hundir la Flota
    "hundirTitle": {"es": "Hundir la Flota", "en": "Battleship", "fr": "Bataille Navale", "ca": "Enfonsar la Flota", "eu": "Flota Hondoratu", "de": "Schiffe Versenken", "it": "Battaglia Navale"},
    "hundirPlaceShips": {"es": "Coloca tus barcos", "en": "Place your ships", "fr": "Placez vos navires", "ca": "Col·loca els teus vaixells", "eu": "Jarri zure itsasontziak", "de": "Platziere deine Schiffe", "it": "Posiziona le tue navi"},
    "hundirValidate": {"es": "Validar posición", "en": "Validate position", "fr": "Valider la position", "ca": "Validar posició", "eu": "Posizioa baliozkotu", "de": "Position bestätigen", "it": "Convalida posizione"},
    "hundirWaiting": {"es": "Esperando jugadores...", "en": "Waiting for players...", "fr": "En attente de joueurs...", "ca": "Esperant jugadors...", "eu": "Jokalariak itxaroten...", "de": "Warte auf Spieler...", "it": "In attesa di giocatori..."},
    "hundirYourTurn": {"es": "¡Tu turno!", "en": "Your turn!", "fr": "Votre tour !", "ca": "El teu torn!", "eu": "Zure txanda!", "de": "Du bist dran!", "it": "Il tuo turno!"},
    "hundirOpponentTurn": {"es": "Turno del oponente", "en": "Opponent's turn", "fr": "Tour de l'adversaire", "ca": "Torn de l'oponent", "eu": "Aurkariarentzanda", "de": "Gegner ist dran", "it": "Turno dell'avversario"},
    "hundirHit": {"es": "¡Tocado!", "en": "Hit!", "fr": "Touché !", "ca": "Tocat!", "eu": "Jo!", "de": "Treffer!", "it": "Colpito!"},
    "hundirMiss": {"es": "¡Agua!", "en": "Miss!", "fr": "À l'eau !", "ca": "Aigua!", "eu": "Ura!", "de": "Daneben!", "it": "Mancato!"},
    "hundirSunk": {"es": "¡Hundido!", "en": "Sunk!", "fr": "Coulé !", "ca": "Enfonsat!", "eu": "Hondoratua!", "de": "Versenkt!", "it": "Affondato!"},
    "hundirVictory": {"es": "¡Victoria!", "en": "Victory!", "fr": "Victoire !", "ca": "Victòria!", "eu": "Garaipena!", "de": "Sieg!", "it": "Vittoria!"},
    "hundirDefeat": {"es": "Derrota", "en": "Defeat", "fr": "Défaite", "ca": "Derrota", "eu": "Porrot", "de": "Niederlage", "it": "Sconfitta"},
    
    # Ships
    "shipCarrier": {"es": "Portaaviones", "en": "Aircraft Carrier", "fr": "Porte-avions", "ca": "Portaavions", "eu": "Hegazkin-ontzia", "de": "Flugzeugträger", "it": "Portaerei"},
    "shipBattleship": {"es": "Acorazado", "en": "Battleship", "fr": "Cuirassé", "ca": "Cuirassat", "eu": "Gudarontzia", "de": "Schlachtschiff", "it": "Corazzata"},
    "shipSubmarine": {"es": "Submarino", "en": "Submarine", "fr": "Sous-marin", "ca": "Submarí", "eu": "Itsaspekoa", "de": "U-Boot", "it": "Sottomarino"},
    "shipDestroyer": {"es": "Destructor", "en": "Destroyer", "fr": "Destroyer", "ca": "Destructor", "eu": "Suntsitzailea", "de": "Zerstörer", "it": "Cacciatorpediniere"},
    "shipPatrol": {"es": "Patrullera", "en": "Patrol Boat", "fr": "Patrouilleur", "ca": "Patrullera", "eu": "Patroila-ontzia", "de": "Patrouillenboot", "it": "Pattugliatore"},
    
    # Quien Soy
    "quienSoyTitle": {"es": "¿Quién soy?", "en": "Who am I?", "fr": "Qui suis-je ?", "ca": "Qui sóc?", "eu": "Nor naiz?", "de": "Wer bin ich?", "it": "Chi sono?"},
    "quienSoyAsk": {"es": "Hacer pregunta", "en": "Ask question", "fr": "Poser une question", "ca": "Fer pregunta", "eu": "Galdera egin", "de": "Frage stellen", "it": "Fai una domanda"},
    "quienSoyGuess": {"es": "Adivinar", "en": "Guess", "fr": "Deviner", "ca": "Endevinar", "eu": "Asmatu", "de": "Raten", "it": "Indovina"},
    "quienSoyYes": {"es": "Sí", "en": "Yes", "fr": "Oui", "ca": "Sí", "eu": "Bai", "de": "Ja", "it": "Sì"},
    "quienSoyNo": {"es": "No", "en": "No", "fr": "Non", "ca": "No", "eu": "Ez", "de": "Nein", "it": "No"},
    "quienSoyCorrect": {"es": "¡Correcto!", "en": "Correct!", "fr": "Correct !", "ca": "Correcte!", "eu": "Zuzena!", "de": "Richtig!", "it": "Corretto!"},
    "quienSoyWrong": {"es": "Incorrecto", "en": "Wrong", "fr": "Incorrect", "ca": "Incorrecte", "eu": "Okerra", "de": "Falsch", "it": "Sbagliato"},
    
    # Millonario
    "millonarioTitle": {"es": "¿Quiere ser millonario?", "en": "Who Wants to Be a Millionaire?", "fr": "Qui veut gagner des millions ?", "ca": "Vol ser milionari?", "eu": "Milionario izan nahi duzu?", "de": "Wer wird Millionär?", "it": "Chi vuol essere milionario?"},
    "millonarioAnswer": {"es": "Responder", "en": "Answer", "fr": "Répondre", "ca": "Respondre", "eu": "Erantzun", "de": "Antworten", "it": "Rispondi"},
    "millonarioFiftyFifty": {"es": "50:50", "en": "50:50", "fr": "50:50", "ca": "50:50", "eu": "50:50", "de": "50:50", "it": "50:50"},
    "millonarioAudience": {"es": "Público", "en": "Audience", "fr": "Public", "ca": "Públic", "eu": "Publikoa", "de": "Publikum", "it": "Pubblico"},
    "millonarioCall": {"es": "Llamada", "en": "Phone a Friend", "fr": "Appel", "ca": "Trucada", "eu": "Deia", "de": "Telefonjoker", "it": "Chiamata"},
    
    # Pasapalabra
    "pasapalabraTitle": {"es": "Pasapalabra", "en": "Pasapalabra", "fr": "Pasapalabra", "ca": "Pasapalabra", "eu": "Pasapalabra", "de": "Pasapalabra", "it": "Pasapalabra"},
    "pasapalabraPass": {"es": "Pasapalabra", "en": "Pass", "fr": "Passer", "ca": "Passa", "eu": "Pasa", "de": "Passen", "it": "Passa"},
    "pasapalabraAnswer": {"es": "Responder", "en": "Answer", "fr": "Répondre", "ca": "Respondre", "eu": "Erantzun", "de": "Antworten", "it": "Rispondi"},
    "pasapalabraTime": {"es": "Tiempo", "en": "Time", "fr": "Temps", "ca": "Temps", "eu": "Denbora", "de": "Zeit", "it": "Tempo"},
    
    # Cifras y Letras
    "cifrasLetrasTitle": {"es": "Cifras y Letras", "en": "Numbers & Letters", "fr": "Des Chiffres et des Lettres", "ca": "Xifres i Lletres", "eu": "Zenbakiak eta Hizkiak", "de": "Zahlen und Buchstaben", "it": "Numeri e Lettere"},
    "cifrasNumbers": {"es": "Cifras", "en": "Numbers", "fr": "Chiffres", "ca": "Xifres", "eu": "Zenbakiak", "de": "Zahlen", "it": "Numeri"},
    "cifrasLetters": {"es": "Letras", "en": "Letters", "fr": "Lettres", "ca": "Lletres", "eu": "Hizkiak", "de": "Buchstaben", "it": "Lettere"},
    "cifrasTarget": {"es": "Objetivo", "en": "Target", "fr": "Objectif", "ca": "Objectiu", "eu": "Helburua", "de": "Ziel", "it": "Obiettivo"},
    "cifrasSolution": {"es": "Solución", "en": "Solution", "fr": "Solution", "ca": "Solució", "eu": "Emaitza", "de": "Lösung", "it": "Soluzione"},
    
    # Admin
    "adminTitle": {"es": "Administración", "en": "Administration", "fr": "Administration", "ca": "Administració", "eu": "Administrazioa", "de": "Verwaltung", "it": "Amministrazione"},
    "adminStatus": {"es": "Estado del juego", "en": "Game status", "fr": "État du jeu", "ca": "Estat del joc", "eu": "Jokoaren egoera", "de": "Spielstatus", "it": "Stato del gioco"},
    "adminActive": {"es": "Activo", "en": "Active", "fr": "Actif", "ca": "Actiu", "eu": "Aktibo", "de": "Aktiv", "it": "Attivo"},
    "adminInactive": {"es": "Desactivado", "en": "Inactive", "fr": "Désactivé", "ca": "Desactivat", "eu": "Desaktibatua", "de": "Inaktiv", "it": "Disattivo"},
    "adminActivate": {"es": "Activar", "en": "Activate", "fr": "Activer", "ca": "Activar", "eu": "Aktibatu", "de": "Aktivieren", "it": "Attiva"},
    "adminDeactivate": {"es": "Desactivar", "en": "Deactivate", "fr": "Désactiver", "ca": "Desactivar", "eu": "Desaktibatu", "de": "Deaktivieren", "it": "Disattiva"},
    "adminReset": {"es": "Reiniciar", "en": "Reset", "fr": "Réinitialiser", "ca": "Reiniciar", "eu": "Berrabiarazi", "de": "Zurücksetzen", "it": "Ripristina"},
    "adminStart": {"es": "Iniciar partida", "en": "Start game", "fr": "Démarrer la partie", "ca": "Iniciar partida", "eu": "Partida hasi", "de": "Spiel starten", "it": "Inizia partita"},
    "adminPlayers": {"es": "Jugadores", "en": "Players", "fr": "Joueurs", "ca": "Jugadors", "eu": "Jokalariak", "de": "Spieler", "it": "Giocatori"},
    "adminAddPlayer": {"es": "Añadir jugador", "en": "Add player", "fr": "Ajouter un joueur", "ca": "Afegir jugador", "eu": "Jokalaria gehitu", "de": "Spieler hinzufügen", "it": "Aggiungi giocatore"},
    "adminOpenGame": {"es": "Abrir juego", "en": "Open game", "fr": "Ouvrir le jeu", "ca": "Obrir joc", "eu": "Jokoa ireki", "de": "Spiel öffnen", "it": "Apri gioco"},
    
    # Votaciones
    "votacionesTitle": {"es": "Votaciones", "en": "Voting", "fr": "Votes", "ca": "Votacions", "eu": "Botoak", "de": "Abstimmungen", "it": "Votazioni"},
    "votacionesCreate": {"es": "Crear votación", "en": "Create poll", "fr": "Créer un vote", "ca": "Crear votació", "eu": "Botoa sortu", "de": "Abstimmung erstellen", "it": "Crea votazione"},
    "votacionesVote": {"es": "Votar", "en": "Vote", "fr": "Voter", "ca": "Votar", "eu": "Botoa eman", "de": "Abstimmen", "it": "Vota"},
    "votacionesResults": {"es": "Resultados", "en": "Results", "fr": "Résultats", "ca": "Resultats", "eu": "Emaitzak", "de": "Ergebnisse", "it": "Risultati"},
    "votacionesOpen": {"es": "Abierta", "en": "Open", "fr": "Ouverte", "ca": "Oberta", "eu": "Irekia", "de": "Offen", "it": "Aperta"},
    "votacionesClosed": {"es": "Cerrada", "en": "Closed", "fr": "Fermée", "ca": "Tancada", "eu": "Itxia", "de": "Geschlossen", "it": "Chiusa"},
}

def main():
    """Generate comprehensive translation files"""
    i18n_dir = Path("static/i18n")
    
    # Load existing translations
    existing = {}
    for lang in ["es", "en", "fr", "ca", "eu", "de", "it"]:
        file_path = i18n_dir / f"{lang}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                existing[lang] = json.load(f)
        else:
            existing[lang] = {}
    
    # Merge with new game translations
    for key, translations in GAME_TRANSLATIONS.items():
        for lang, text in translations.items():
            if key not in existing[lang]:
                existing[lang][key] = text
    
    # Save updated translations
    for lang, data in existing.items():
        file_path = i18n_dir / f"{lang}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ Updated {lang}.json with {len(data)} keys")

if __name__ == "__main__":
    main()
