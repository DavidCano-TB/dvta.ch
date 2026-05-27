#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper para integración con Groq API
100% IA - SIN FALLBACKS LOCALES
"""

import os
import json
import urllib.request
import urllib.error
import logging
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class GroqAI:
    """Cliente para Groq API - 100% IA sin fallbacks locales"""
    
    def __init__(self):
        self.api_key = self._load_api_key()
        self.model = "llama-3.1-8b-instant"  # Rápido y disponible
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.timeout = 30
        self.max_retries = 5  # Más reintentos para rate limits
        
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
                        if key and not key.startswith("gsk_YourGroqKeyHere"):
                            logger.info(f"Groq API key loaded from: {loc}")
                            return key
                except Exception as e:
                    logger.warning(f"Error reading {loc}: {e}")
        
        logger.error("Groq API key not found!")
        return None
    
    def ask(self, 
            prompt: str, 
            system: Optional[str] = None,
            max_tokens: int = 500,
            temperature: float = 0.7) -> Optional[str]:
        """Hace una pregunta a Groq - ESPERA si hay rate limit"""
        if not self.api_key:
            logger.error("No Groq API key available")
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
                        "Authorization": f"Bearer {self.api_key}",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
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
                
                # Si es rate limit (429), esperar y reintentar
                if e.code == 429:
                    if attempt < self.max_retries - 1:
                        # Extraer tiempo de espera del mensaje de error
                        wait_time = 10  # Por defecto 10 segundos
                        try:
                            error_data = json.loads(error_body)
                            error_msg = error_data.get("error", {}).get("message", "")
                            if "Please try again in" in error_msg:
                                # Extraer el tiempo: "Please try again in 8.77s"
                                import re
                                match = re.search(r'try again in ([\d.]+)', error_msg)
                                if match:
                                    wait_time = float(match.group(1)) + 1  # +1 segundo de margen
                        except:
                            pass
                        
                        logger.warning(f"Rate limit (429), esperando {wait_time}s... (intento {attempt+1}/{self.max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Rate limit después de {self.max_retries} intentos")
                        return None
                
                # Otros errores HTTP
                logger.error(f"Groq API HTTP error {e.code}: {e.reason} - {error_body}")
                if e.code in [400, 401, 403]:
                    return None
                
                # Para otros errores, reintentar
                if attempt < self.max_retries - 1:
                    time.sleep(2)
                    continue
                return None
                    
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
                    continue
                return None
        
        return None
    
    def verify_character(self, character: str) -> Dict[str, Any]:
        """Verifica si un personaje existe - 100% IA SIN FALLBACK LOCAL"""
        
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
"scoubidou" → Scooby-Doo ✓
"miki maus" → Mickey Mouse ✓
"supermen" → Superman ✓
"spider man" → Spider-Man ✓
"hombre araña" → Spider-Man ✓
"dedpol" → Deadpool ✓
"pikachu" → Pikachu ✓
"mario bross" → Mario Bros ✓
"sonic" → Sonic the Hedgehog ✓
"pato donald" → Donald Duck ✓
"bob esponja" → SpongeBob ✓

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
  "suggestions": ["Diverse Character 1", "Diverse Character 2", "Diverse Character 3", "Diverse Character 4", "Diverse Character 5"]
}}

CRITICAL INSTRUCTIONS:
- Set "exists": true if you can identify ANY character (be VERY permissive)
- ALWAYS provide a valid "corrected_name" - NEVER null or empty
- "main_known_for": What they're MOST famous for (SHORT and SPECIFIC)
- "key_characteristics": 5 MAIN traits (physical, personality, abilities, origin, role)
- Set "confidence": "high" if confident, "medium" if unsure, "low" if guessing
- "suggestions": MUST be 5 DIFFERENT and DIVERSE characters (NOT always the same ones!)
- Vary suggestions based on the input character's category
- Only set "exists": false if COMPLETELY impossible to identify

NOW IDENTIFY: "{character}"

RESPOND WITH ONLY THE JSON (no ```json, no markdown, no explanations):"""
        
        logger.info(f"🔍 Verificando personaje con IA: '{character}'")
        
        response = self.ask(
            prompt=prompt,
            system=system_prompt,
            max_tokens=1000,
            temperature=0.3
        )
        
        if not response:
            logger.error(f"❌ IA no respondió para '{character}' - NO HAY FALLBACK")
            return {
                "exists": False,
                "error": "AI_NOT_AVAILABLE",
                "message": "La IA no está disponible. Por favor intenta de nuevo."
            }
        
        logger.info(f"✓ IA respondió: {response[:200]}...")
        
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
            
            if start < 0 or end <= start:
                logger.error(f"❌ No se encontró JSON en respuesta de IA")
                return {
                    "exists": False,
                    "error": "INVALID_AI_RESPONSE",
                    "message": "La IA no devolvió un formato válido. Intenta de nuevo."
                }
            
            json_str = cleaned_response[start:end]
            result = json.loads(json_str)
            
            # Validar campos obligatorios
            if "exists" not in result:
                result["exists"] = True
            
            if not result.get("corrected_name"):
                result["corrected_name"] = character.title()
            
            if not result.get("main_known_for"):
                result["main_known_for"] = "Personaje conocido"
            
            if not result.get("key_characteristics") or not isinstance(result["key_characteristics"], list):
                result["key_characteristics"] = ["Personaje", "Conocido", "Popular", "Reconocible", "Famoso"]
            
            if not result.get("suggestions") or not isinstance(result["suggestions"], list):
                result["suggestions"] = []
            
            if not result.get("confidence"):
                result["confidence"] = "medium"
            
            if not result.get("category"):
                result["category"] = "general"
            
            result.setdefault("is_real", False)
            result.setdefault("is_fictional", True)
            result.setdefault("is_mythological", False)
            
            logger.info(f"✅ Personaje verificado: '{result['corrected_name']}' (confidence: {result['confidence']})")
            logger.info(f"   Conocido por: {result['main_known_for']}")
            logger.info(f"   Sugerencias: {result['suggestions']}")
            
            return result
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parseando JSON de IA: {e}")
            logger.error(f"   Respuesta: {response[:500]}")
            return {
                "exists": False,
                "error": "JSON_PARSE_ERROR",
                "message": "Error procesando respuesta de IA. Intenta de nuevo."
            }
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return {
                "exists": False,
                "error": "UNEXPECTED_ERROR",
                "message": f"Error: {str(e)}"
            }
    
    def ask_quien_soy(self, character_info: Dict[str, Any], question: str) -> str:
        """Pregunta específica para el juego Quien Soy - SOLO RESPONDE SÍ O NO"""
        
        character_name = character_info.get("corrected_name", character_info.get("character", "Unknown"))
        main_known_for = character_info.get("main_known_for", "")
        key_characteristics = character_info.get("key_characteristics", [])
        is_real = character_info.get("is_real", False)
        is_fictional = character_info.get("is_fictional", True)
        is_mythological = character_info.get("is_mythological", False)
        category = character_info.get("category", "unknown")
        
        logger.info(f"❓ Pregunta sobre '{character_name}': '{question}'")
        
        system_prompt = """You are a SUPER-HELPFUL assistant for the "Quien Soy" (Who Am I?) guessing game.
Your goal is to HELP players discover the character through CLEAR and USEFUL answers.

CRITICAL RESPONSE RULES:
1. Respond with ONLY: "Sí" or "No" (NEVER "Ni sí ni no")
2. NO explanations, NO punctuation, NO extra words
3. Be GENEROUS and HELPFUL - focus on MAIN/PREDOMINANT characteristics
4. When asked about physical traits (color, size, etc.), refer to the MAJORITY/PREDOMINANT feature
5. Prioritize answers that GUIDE players toward discovering the character

PREDOMINANT CHARACTERISTIC RULE (SUPER IMPORTANT):
- "¿Es blanco?" → Answer based on PREDOMINANT color, not small details
  Example: Mickey Mouse is mostly BLACK, so "¿Es negro?" = "Sí", "¿Es blanco?" = "No" (even though he has white gloves)
- "¿Es grande?" → Answer based on OVERALL size perception, not technical details
- "¿Es viejo?" → Answer based on how they're GENERALLY perceived
- "¿Es famoso?" → If widely known, always "Sí"

HELPFUL ANSWERING STRATEGY:
- Focus on what the character is MOST KNOWN FOR
- Answer "Sí" to questions that help identify the character
- Answer "No" to questions that clearly don't apply
- When in doubt, choose the answer that is MORE HELPFUL for discovery
- Think: "Will this answer help or confuse the player?"

EXAMPLES OF GOOD ANSWERS:
Character: "Pikachu"
- "¿Es amarillo?" → "Sí" (predominant color)
- "¿Es un animal?" → "Sí" (helpful, even if fictional)
- "¿Es de videojuegos?" → "Sí" (main context)
- "¿Es real?" → "No" (clear and helpful)

Character: "Superman"  
- "¿Puede volar?" → "Sí" (main power)
- "¿Es fuerte?" → "Sí" (main characteristic)
- "¿Usa capa?" → "Sí" (iconic visual)
- "¿Es humano?" → "No" (he's Kryptonian, helpful answer)

Character: "Einstein"
- "¿Es científico?" → "Sí" (main profession)
- "¿Es inteligente?" → "Sí" (main trait)
- "¿Está vivo?" → "No" (clear fact)
- "¿Es alemán?" → "Sí" (origin, helpful)"""
        
        character_context = f"""CHARACTER: {character_name}

MAIN KNOWN FOR: {main_known_for}

KEY CHARACTERISTICS (focus on these):
{chr(10).join(f"- {trait}" for trait in key_characteristics)}

TYPE:
- Real person: {"Yes" if is_real else "No"}
- Fictional: {"Yes" if is_fictional else "No"}
- Mythological: {"Yes" if is_mythological else "No"}
- Category: {category}

REMEMBER: 
- Answer based on PREDOMINANT/MAIN characteristics
- Be HELPFUL and CLEAR
- Guide players toward discovery
- ONLY respond "Sí" or "No" (never ambiguous)"""
        
        prompt = f"""{character_context}

PLAYER QUESTION: "{question}"

ANALYSIS:
1. What is the PREDOMINANT characteristic being asked about?
2. Does this apply to {character_name}'s MAIN/MOST KNOWN traits?
3. Which answer ("Sí" or "No") is MORE HELPFUL for the player to discover the character?

Think about {character_name}'s MOST RECOGNIZABLE features and answer in a way that HELPS discovery.

Respond with ONLY ONE WORD (no punctuation, no explanations):
- "Sí" (if yes, or if it helps identify the character)
- "No" (if no, or if it would mislead)

YOUR ONE-WORD ANSWER:"""
        
        response = self.ask(
            prompt=prompt,
            system=system_prompt,
            max_tokens=5,
            temperature=0.1
        )
        
        if not response:
            logger.warning("⚠️ IA no respondió, usando 'No' por defecto")
            return "No"
        
        # Normalización
        import re
        response_clean = response.lower().strip()
        response_clean = re.sub(r'[.,!?¿¡"\'\(\)\[\]\{\}:;]', '', response_clean)
        response_clean = response_clean.strip()
        
        logger.info(f"✓ Respuesta IA: '{response_clean}'")
        
        # Detectar respuesta - SOLO SÍ O NO
        if any(word in response_clean for word in ['sí', 'si', 'yes', 'oui', 'ja', 'sì', 'sim', 'da']):
            return "Sí"
        else:
            # Cualquier otra respuesta se convierte en "No"
            return "No"


# Instancia global
_groq_instance = None

def get_groq() -> GroqAI:
    """Obtiene la instancia global de GroqAI"""
    global _groq_instance
    if _groq_instance is None:
        _groq_instance = GroqAI()
    return _groq_instance

# Funciones de conveniencia para compatibilidad
def ask_groq(prompt: str, **kwargs) -> Optional[str]:
    """Atajo para hacer una pregunta a Groq"""
    return get_groq().ask(prompt, **kwargs)

def ask_quien_soy(character_info: Dict[str, Any], question: str) -> str:
    """Atajo para preguntas del juego Quien soy - USA INFO DEL PERSONAJE"""
    return get_groq().ask_quien_soy(character_info, question)

# Alias para compatibilidad con código existente que usa GeminiAI
GeminiAI = GroqAI
get_gemini = get_groq
ask_gemini = ask_groq
