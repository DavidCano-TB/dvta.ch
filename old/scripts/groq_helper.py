#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper para integración con Groq API
Versión optimizada para DVDBank - Sistema Quién Soy
"""

import os
import json
import urllib.request
import urllib.error
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class GroqAI:
    """Cliente para Groq API - Rápido y con límites altos"""
    
    def __init__(self):
        self.api_key = self._load_api_key()
        # Modelos disponibles en Groq (ordenados por velocidad/calidad)
        self.model = "llama-3.3-70b-versatile"  # Mejor balance
        # Alternativas:
        # "llama-3.1-70b-versatile" - Muy bueno
        # "mixtral-8x7b-32768" - Rápido
        # "gemma2-9b-it" - Muy rápido
        
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.timeout = 30
        self.max_retries = 3
        
    def _load_api_key(self) -> Optional[str]:
        """Carga la API key desde diferentes ubicaciones"""
        locations = [
            "config/.groq_key",
            ".groq_key",
            os.environ.get("GROQ_API_KEY")
        ]
        
        for loc in locations:
            if not loc:
                continue
            if os.path.exists(str(loc)):
                try:
                    with open(loc, 'r') as f:
                        key = f.read().strip()
                        # Verificar que no sea el placeholder
                        if key and not key.startswith("gsk_YourGroqKeyHere"):
                            logger.info(f"Groq API key loaded from: {loc}")
                            return key
                        else:
                            logger.warning(f"Groq API key in {loc} is a placeholder")
                except Exception as e:
                    logger.warning(f"Error reading {loc}: {e}")
        
        logger.warning("Groq API key not found or is placeholder")
        return None
    
    def ask(self, 
            prompt: str, 
            system: Optional[str] = None,
            max_tokens: int = 500,
            temperature: float = 0.7) -> Optional[str]:
        """Hace una pregunta a Groq y devuelve la respuesta"""
        if not self.api_key:
            logger.warning("No Groq API key available")
            return None
        
        for attempt in range(self.max_retries):
            try:
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})
                
                payload_dict = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": 0.95
                }
                
                payload = json.dumps(payload_dict).encode('utf-8')
                
                req = urllib.request.Request(
                    self.api_url,
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    method="POST"
                )
                
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    
                    if result.get("choices"):
                        message = result["choices"][0].get("message", {})
                        content = message.get("content", "").strip()
                        if content:
                            return content
                    
                    return None
                        
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8') if e.fp else ""
                logger.error(f"Groq API HTTP error {e.code}: {e.reason} - {error_body}")
                
                if e.code in [400, 401, 403]:
                    logger.error("Authentication or permission error - check API key")
                    return None
                elif e.code == 429:
                    if attempt < self.max_retries - 1:
                        import time
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limit hit, waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                return None
                    
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                if attempt < self.max_retries - 1:
                    import time
                    time.sleep(1)
                    continue
                return None
        
        return None
    
    def verify_character(self, character: str) -> Dict[str, Any]:
        """Verifica si un personaje existe - 100% IA con Groq"""
        
        system_prompt = """You are a SUPER-INTELLIGENT CHARACTER RECOGNITION EXPERT.
Your PRIMARY goal is to RECOGNIZE ANY character name, even with SEVERE spelling errors.
You have COMPLETE knowledge of ALL famous characters from ANY domain worldwide.
Be EXTREMELY PERMISSIVE and use PHONETIC MATCHING.
Respond ONLY with valid JSON - no markdown, no explanations."""
        
        prompt = f"""INPUT: "{character}"

YOUR MISSION: Identify this character using MAXIMUM intelligence and flexibility.

RECOGNITION STRATEGIES (USE ALL):
1. PHONETIC MATCHING: How does it SOUND? (most important!)
2. VISUAL SIMILARITY: Similar letters/patterns
3. COMMON MISSPELLINGS: Typical errors people make
4. LANGUAGE VARIATIONS: Spanish, English, French, etc.
5. PARTIAL MATCHES: Part of the name is correct
6. CONTEXT CLUES: What could they mean?

ULTRA-FLEXIBLE EXAMPLES:
"scoubidou" → Scooby-Doo ✓ (phonetic)
"miki maus" → Mickey Mouse ✓ (phonetic)
"supermen" → Superman ✓ (plural error)
"spider man" → Spider-Man ✓ (space error)
"hombre araña" → Spider-Man ✓ (Spanish)
"dedpol" → Deadpool ✓ (phonetic)
"pikachu" → Pikachu ✓ (correct)
"mario bross" → Mario Bros ✓ (double s)
"sonic" → Sonic the Hedgehog ✓ (short name)
"pato donald" → Donald Duck ✓ (Spanish)
"bob esponja" → SpongeBob ✓ (Spanish)

CHARACTER DATABASE (RECOGNIZE ALL):
• Cartoons: Scooby-Doo, Mickey Mouse, Bugs Bunny, SpongeBob, Tom & Jerry, Garfield, Tweety, Road Runner, Pink Panther, Popeye, Felix the Cat
• Disney: Donald Duck, Goofy, Pluto, Minnie Mouse, Simba, Nemo, Woody, Buzz Lightyear, Elsa, Anna
• Superheroes: Superman, Batman, Spider-Man, Iron Man, Captain America, Thor, Hulk, Wonder Woman, Flash, Deadpool, Wolverine
• Movies/TV: Harry Potter, Darth Vader, Yoda, Gandalf, Frodo, Sherlock Holmes, James Bond, Rocky
• Video Games: Mario, Luigi, Sonic, Pikachu, Link, Zelda, Pac-Man, Donkey Kong, Lara Croft, Master Chief
• Anime: Goku, Vegeta, Naruto, Luffy, Sailor Moon, Ash Ketchum, Doraemon
• Real People: Einstein, Messi, Ronaldo, Michael Jackson, Elvis, Beatles, Obama
• Historical: Napoleon, Cleopatra, Julius Caesar, Joan of Arc
• Mythological: Zeus, Thor, Hercules, Medusa

RESPONSE FORMAT (EXACT JSON - NO MARKDOWN):
{{
  "exists": true,
  "corrected_name": "Full Correct Name Here",
  "is_real": false,
  "is_fictional": true,
  "is_mythological": false,
  "category": "cartoons",
  "main_known_for": "Brief description (1-2 sentences max)",
  "key_characteristics": ["trait1", "trait2", "trait3", "trait4", "trait5"],
  "confidence": "high",
  "suggestions": ["Character 1", "Character 2", "Character 3", "Character 4", "Character 5"]
}}

CRITICAL INSTRUCTIONS:
- Set "exists": true if you can identify ANY character (be VERY permissive)
- ALWAYS provide a valid "corrected_name" - NEVER null or empty
- "main_known_for": What they're MOST famous for (SHORT)
- "key_characteristics": 5 MAIN traits (physical, personality, abilities, origin, role)
- Set "confidence": "high" if confident, "medium" if unsure, "low" if guessing
- ALWAYS include 5 diverse character suggestions
- Only set "exists": false if COMPLETELY impossible to identify

NOW IDENTIFY: "{character}"

RESPOND WITH ONLY THE JSON (no ```json, no markdown, no explanations):"""
        
        response = self.ask(
            prompt=prompt,
            system=system_prompt,
            max_tokens=1000,
            temperature=0.2
        )
        
        # Lista de sugerencias por defecto
        default_suggestions = [
            "Scooby-Doo", "Mickey Mouse", "Superman", "Batman", "Spider-Man",
            "Harry Potter", "Pikachu", "Mario Bros", "Sonic", "Bugs Bunny",
            "Iron Man", "Wonder Woman", "SpongeBob", "Donald Duck", "Goku",
            "Naruto", "Deadpool", "Hulk", "Thor", "Captain America"
        ]
        
        if not response:
            logger.error("Groq API failed for character verification")
            # Fallback: aceptar el personaje de todos modos
            return {
                "exists": True,
                "corrected_name": character.title() if character else "Personaje Desconocido",
                "is_real": False,
                "is_fictional": True,
                "is_mythological": False,
                "category": "unknown",
                "main_known_for": "Personaje para juego de adivinanzas",
                "key_characteristics": ["Personaje conocido", "Tiene características únicas", "Es reconocible", "Tiene historia", "Es popular"],
                "confidence": "medium",
                "suggestions": default_suggestions[:10],
                "error": "AI_NOT_AVAILABLE_BUT_ACCEPTED"
            }
        
        logger.info(f"Groq response for '{character}': {response[:500]}")
        
        try:
            # Limpiar markdown si existe
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0]
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0]
            
            # Extraer JSON
            start = cleaned_response.find('{')
            end = cleaned_response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = cleaned_response[start:end]
                result = json.loads(json_str)
                
                # Validar y corregir campos obligatorios
                if "exists" not in result:
                    result["exists"] = True
                
                # CRÍTICO: Asegurar que corrected_name SIEMPRE sea válido
                corrected_name = result.get("corrected_name")
                if not corrected_name or str(corrected_name).lower() in ["none", "null", "undefined", ""]:
                    corrected_name = character.title() if character else "Personaje Desconocido"
                result["corrected_name"] = str(corrected_name).strip()
                
                if "main_known_for" not in result or not result.get("main_known_for"):
                    result["main_known_for"] = "Personaje conocido"
                
                if "key_characteristics" not in result or not isinstance(result["key_characteristics"], list) or len(result["key_characteristics"]) == 0:
                    result["key_characteristics"] = ["Personaje conocido", "Tiene características únicas", "Es reconocible", "Tiene historia", "Es popular"]
                
                if "suggestions" not in result or not isinstance(result["suggestions"], list) or len(result["suggestions"]) == 0:
                    result["suggestions"] = default_suggestions[:10]
                
                if "confidence" not in result:
                    result["confidence"] = "high" if result.get("exists") else "low"
                
                if "category" not in result:
                    result["category"] = "general"
                
                result.setdefault("is_real", False)
                result.setdefault("is_fictional", True)
                result.setdefault("is_mythological", False)
                
                logger.info(f"✓ Character verified with Groq: '{result['corrected_name']}' (exists: {result.get('exists')}, confidence: {result.get('confidence')})")
                return result
            else:
                logger.error("No JSON found in Groq response")
                return {
                    "exists": True,
                    "corrected_name": character.title() if character else "Personaje Desconocido",
                    "is_real": False,
                    "is_fictional": True,
                    "is_mythological": False,
                    "category": "unknown",
                    "main_known_for": "Personaje para juego de adivinanzas",
                    "key_characteristics": ["Personaje conocido", "Tiene características únicas", "Es reconocible", "Tiene historia", "Es popular"],
                    "confidence": "medium",
                    "suggestions": default_suggestions[:10],
                    "error": "INVALID_RESPONSE_BUT_ACCEPTED"
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Groq: {e}")
            return {
                "exists": True,
                "corrected_name": character.title() if character else "Personaje Desconocido",
                "is_real": False,
                "is_fictional": True,
                "is_mythological": False,
                "category": "unknown",
                "main_known_for": "Personaje para juego de adivinanzas",
                "key_characteristics": ["Personaje conocido", "Tiene características únicas", "Es reconocible", "Tiene historia", "Es popular"],
                "confidence": "medium",
                "suggestions": default_suggestions[:10],
                "error": "JSON_PARSE_ERROR_BUT_ACCEPTED"
            }
    
    def ask_quien_soy(self, character_info: Dict[str, Any], question: str) -> str:
        """Pregunta específica para el juego Quien Soy - USA CARACTERÍSTICAS DEL PERSONAJE"""
        
        character_name = character_info.get("corrected_name", character_info.get("character", "Unknown"))
        main_known_for = character_info.get("main_known_for", "")
        key_characteristics = character_info.get("key_characteristics", [])
        is_real = character_info.get("is_real", False)
        is_fictional = character_info.get("is_fictional", True)
        is_mythological = character_info.get("is_mythological", False)
        category = character_info.get("category", "unknown")
        
        logger.info(f"ask_quien_soy (Groq): Pregunta sobre '{character_name}': '{question}'")
        
        system_prompt = """You are an EXPERT assistant for the "Quien Soy" (Who Am I?) guessing game.
You MUST answer yes/no questions about characters based on their MAIN characteristics.

CRITICAL RESPONSE RULES:
1. Respond with ONLY: "Sí" or "No"
2. NO "Ni sí ni no" - this option is FORBIDDEN
3. NO explanations, NO punctuation, NO extra words
4. Base answers on the character's MOST KNOWN traits
5. If unsure or ambiguous, answer "No"
6. Be CONSISTENT with the character's main characteristics

RESPONSE LOGIC:
- "Sí" = clearly YES based on main characteristics
- "No" = clearly NO, or ambiguous, or not a main trait"""
        
        character_context = f"""CHARACTER: {character_name}

MAIN KNOWN FOR: {main_known_for}

KEY CHARACTERISTICS:
{chr(10).join(f"- {trait}" for trait in key_characteristics)}

TYPE:
- Real person: {"Yes" if is_real else "No"}
- Fictional: {"Yes" if is_fictional else "No"}
- Mythological: {"Yes" if is_mythological else "No"}
- Category: {category}"""
        
        prompt = f"""{character_context}

PLAYER QUESTION: "{question}"

Think about {character_name}'s MAIN characteristics and answer based on what they are MOST KNOWN FOR.

Respond with ONLY ONE WORD (no punctuation):
- "Sí" (if clearly yes)
- "No" (if clearly no or ambiguous)

YOUR ONE-WORD ANSWER:"""
        
        response = self.ask(
            prompt=prompt,
            system=system_prompt,
            max_tokens=10,
            temperature=0.1
        )
        
        if not response:
            logger.warning("ask_quien_soy: Groq no respondió, usando 'No'")
            return "No"
        
        logger.info(f"ask_quien_soy (Groq): Respuesta cruda = '{response}'")
        
        # Normalización
        import re
        response_clean = response.lower().strip()
        response_clean = re.sub(r'[.,!?¿¡"\'\(\)\[\]\{\}:;]', '', response_clean)
        response_clean = response_clean.strip()
        
        logger.info(f"ask_quien_soy (Groq): Respuesta limpia = '{response_clean}'")
        
        # Detectar respuesta - SOLO "Sí" o "No"
        if any(word in response_clean for word in ['sí', 'si', 'yes', 'oui', 'ja', 'sì', 'sim', 'da']):
            logger.info("✓ Respuesta: Sí")
            return "Sí"
        else:
            # Cualquier otra respuesta (incluyendo "no", "ni sí ni no", ambiguas, etc.) → "No"
            logger.info("✓ Respuesta: No")
            return "No"


# Instancia global
_groq_instance = None

def get_groq() -> GroqAI:
    """Obtiene la instancia global de GroqAI"""
    global _groq_instance
    if _groq_instance is None:
        _groq_instance = GroqAI()
    return _groq_instance

# Funciones de conveniencia
def ask_groq(prompt: str, **kwargs) -> Optional[str]:
    """Atajo para hacer una pregunta a Groq"""
    return get_groq().ask(prompt, **kwargs)

def ask_quien_soy(character_info: Dict[str, Any], question: str) -> str:
    """Atajo para preguntas del juego Quien soy - USA INFO DEL PERSONAJE"""
    return get_groq().ask_quien_soy(character_info, question)
