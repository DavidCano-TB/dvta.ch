#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper para integración con Gemini (Google) API
Versión optimizada y corregida para DVDBank
"""

import os
import json
import urllib.request
import urllib.error
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class GeminiAI:
    """Cliente para Gemini API con manejo de errores"""
    
    def __init__(self):
        self.api_key = self._load_api_key()
        self.model = "gemini-2.5-flash"
        self.api_url_base = "https://generativelanguage.googleapis.com/v1/models"
        self.timeout = 30
        self.max_retries = 3
        
    def _load_api_key(self) -> Optional[str]:
        """Carga la API key desde diferentes ubicaciones"""
        locations = [
            "config/.gemini_key",
            "config/.google_key",
            ".gemini_key",
            os.environ.get("GEMINI_API_KEY"),
            os.environ.get("GOOGLE_API_KEY")
        ]
        
        for loc in locations:
            if not loc:
                continue
            if os.path.exists(str(loc)):
                try:
                    with open(loc, 'r') as f:
                        key = f.read().strip()
                        if key:
                            logger.info(f"Gemini API key loaded from: {loc}")
                            return key
                except Exception as e:
                    logger.warning(f"Error reading {loc}: {e}")
        
        logger.warning("Gemini API key not found")
        return None
    
    def ask(self, 
            prompt: str, 
            system: Optional[str] = None,
            max_tokens: int = 100,
            temperature: float = 1.0) -> Optional[str]:
        """Hace una pregunta a Gemini y devuelve la respuesta"""
        if not self.api_key:
            logger.warning("No API key available")
            return None
        
        for attempt in range(self.max_retries):
            try:
                full_prompt = prompt
                if system:
                    full_prompt = f"{system}\n\n{prompt}"
                
                payload_dict = {
                    "contents": [{
                        "parts": [{
                            "text": full_prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max(max_tokens, 500),
                        "topP": 0.95,
                        "topK": 40
                    },
                    "safetySettings": [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                }
                
                payload = json.dumps(payload_dict).encode('utf-8')
                url = f"{self.api_url_base}/{self.model}:generateContent?key={self.api_key}"
                
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    
                    if result.get("candidates"):
                        candidate = result["candidates"][0]
                        content = candidate.get("content", {})
                        parts = content.get("parts", [])
                        
                        if parts and "text" in parts[0]:
                            answer = parts[0]["text"].strip()
                            return answer
                    
                    return None
                        
            except urllib.error.HTTPError as e:
                logger.error(f"Gemini API HTTP error {e.code}: {e.reason}")
                if e.code in [400, 401, 403]:
                    return None
                elif e.code == 429:
                    if attempt < self.max_retries - 1:
                        import time
                        time.sleep(2 ** attempt)
                        continue
                return None
                    
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                return None
        
        return None
    
    def verify_character(self, character: str) -> Dict[str, Any]:
        """Verifica si un personaje existe - 100% IA"""
        
        system_prompt = "You are an EXPERT character validator. Be VERY FLEXIBLE with spelling. Respond ONLY with valid JSON."
        
        prompt = f"""Character: "{character}"

Determine if this is a valid, recognizable character for a guessing game.
Accept spelling errors and variations.

Consider ALL types:
- Real people (scientists, athletes, musicians, politicians, actors)
- Fictional characters (movies, TV, books, comics, video games)
- Cartoons (Disney, Looney Tunes, anime, etc.)
- Mythological figures
- Video game characters

Examples:
- "dedpol" -> Deadpool
- "bugs buny" -> Bugs Bunny
- "gusiluz" -> Glow Worm
- "pato donald" -> Donald Duck
- "mickey mause" -> Mickey Mouse

Respond with JSON:
{{
  "exists": true or false,
  "corrected_name": "Correct Name",
  "is_real": true or false,
  "is_fictional": true or false,
  "is_mythological": true or false,
  "category": "category",
  "main_known_for": "description",
  "confidence": "high/medium/low",
  "suggestions": []
}}

If character doesn't exist, provide 5 famous character suggestions."""
        
        response = self.ask(
            prompt=prompt,
            system=system_prompt,
            max_tokens=2000,
            temperature=0.3
        )
        
        if not response:
            logger.error("Gemini API failed for character verification")
            return {
                "exists": False,
                "corrected_name": character.title(),
                "is_real": False,
                "is_fictional": False,
                "is_mythological": False,
                "category": "error",
                "main_known_for": "Error: IA no disponible",
                "confidence": "low",
                "suggestions": [],
                "error": "AI_NOT_AVAILABLE"
            }
        
        logger.info(f"Gemini response for '{character}': {response[:500]}")
        
        try:
            # Limpiar markdown
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
                
                # Validar campos
                if "corrected_name" not in result or result.get("corrected_name") is None:
                    result["corrected_name"] = character.title()
                if "main_known_for" not in result or result.get("main_known_for") is None:
                    result["main_known_for"] = "Información no disponible"
                if "suggestions" not in result or not isinstance(result["suggestions"], list):
                    result["suggestions"] = []
                
                logger.info(f"Character verified: {result['corrected_name']} (exists: {result.get('exists')})")
                return result
            else:
                logger.error("No JSON found in response")
                return {
                    "exists": False,
                    "corrected_name": character.title(),
                    "is_real": False,
                    "is_fictional": False,
                    "is_mythological": False,
                    "category": "error",
                    "main_known_for": "Error: Respuesta inválida de la IA",
                    "confidence": "low",
                    "suggestions": [],
                    "error": "INVALID_RESPONSE"
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {
                "exists": False,
                "corrected_name": character.title(),
                "is_real": False,
                "is_fictional": False,
                "is_mythological": False,
                "category": "error",
                "main_known_for": f"Error: No se pudo parsear respuesta JSON",
                "confidence": "low",
                "suggestions": [],
                "error": "JSON_PARSE_ERROR"
            }
    
    def ask_quien_soy(self, character: str, question: str) -> str:
        """Pregunta específica para el juego Quien Soy"""
        
        # Primero verificar el personaje
        char_info = self.verify_character(character)
        
        if not char_info.get("exists", True):
            logger.warning(f"Character '{character}' does not exist, returning 'No'")
            return "No"
        
        corrected_name = char_info.get("corrected_name", character)
        main_known_for = char_info.get("main_known_for", "")
        category = char_info.get("category", "")
        is_real = char_info.get("is_real", False)
        is_fictional = char_info.get("is_fictional", False)
        
        system_prompt = """You are an expert assistant for the Quien Soy guessing game.
Answer yes/no questions about a secret character based on their MAIN characteristics.

CRITICAL RULES:
1. Respond with ONLY: "Sí" or "No"
2. NO "Ni sí ni no" - this option is FORBIDDEN
3. NO explanations, NO punctuation, NO extra text
4. Base answers on PRIMARY characteristics
5. Use your FULL knowledge of the character
6. If unsure or ambiguous, answer "No"

RESPONSE GUIDELINES:
- "Sí" = clearly YES based on main traits
- "No" = clearly NO, or ambiguous, or doesn't apply, or secondary detail"""
        
        prompt = f"""SECRET CHARACTER: {corrected_name}
Category: {category}
Known for: {main_known_for}
Is real: {is_real}
Is fictional: {is_fictional}

PLAYER QUESTION: {question}

Use your COMPLETE knowledge of {corrected_name}.
Answer based on their MAIN characteristics.
Respond with ONLY: "Sí" or "No"
If the question is ambiguous or about secondary details, answer "No".

RESPOND NOW:"""
        
        response = self.ask(
            prompt=prompt,
            system=system_prompt,
            max_tokens=20,
            temperature=0.1
        )
        
        if not response:
            logger.warning("Gemini API failed, returning 'No'")
            return "No"
        
        # Normalizar respuesta - SOLO "Sí" o "No"
        response_lower = response.lower().strip().rstrip('.')
        
        if response_lower in ['sí', 'si', 'yes', 'oui', 'ja']:
            return "Sí"
        else:
            # Cualquier otra respuesta (incluyendo "no", "ni sí ni no", etc.) → "No"
            return "No"


# Instancia global
_gemini_instance = None

def get_gemini() -> GeminiAI:
    """Obtiene la instancia global de GeminiAI"""
    global _gemini_instance
    if _gemini_instance is None:
        _gemini_instance = GeminiAI()
    return _gemini_instance

# Funciones de conveniencia
def ask_gemini(prompt: str, **kwargs) -> Optional[str]:
    """Atajo para hacer una pregunta a Gemini"""
    return get_gemini().ask(prompt, **kwargs)

def ask_quien_soy(character: str, question: str) -> str:
    """Atajo para preguntas del juego Quien soy"""
    return get_gemini().ask_quien_soy(character, question)
