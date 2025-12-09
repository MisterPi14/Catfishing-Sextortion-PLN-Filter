import requests
import json
import logging
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, RISK_THRESHOLD, THREAT_TYPES

logger = logging.getLogger(__name__)

class LLMProcessor:
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL

    def analyze_message(self, message_content):
        """
        Analiza un mensaje usando Ollama para detectar amenazas.
        
        Retorna:
        {
            'threat_detected': bool,
            'threat_type': str (sextorsion, catfishing, scam, harassment),
            'confidence': float (0-1),
            'risk_level': str (low, medium, high)
        }
        """
        try:
            # Construir prompt para el análisis
            prompt = self._build_prompt(message_content)
            
            # Llamar a Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code}")
                return self._default_analysis()
            
            # Parsear respuesta
            result = response.json()
            analysis = self._parse_response(result.get('response', ''))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing message with Ollama: {str(e)}")
            return self._default_analysis()

    def _build_prompt(self, message_content):
        """Construye el prompt para Ollama"""
        return f"""Analiza el siguiente mensaje de chat para detectar amenazas de seguridad.

Mensaje: "{message_content}"

Responde en JSON con el siguiente formato:
{{
    "threat_detected": true/false,
    "threat_type": "sextorsion" | "catfishing" | "scam" | "harassment" | "none",
    "confidence": 0.0-1.0,
    "reasoning": "breve explicación"
}}

Solo responde con el JSON, sin explicaciones adicionales."""

    def _parse_response(self, response_text):
        """Parsea la respuesta de Ollama"""
        try:
            # Intentar extraer JSON de la respuesta
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                
                threat_detected = data.get('threat_detected', False)
                threat_type = data.get('threat_type', 'none')
                confidence = float(data.get('confidence', 0))
                
                # Determinar nivel de riesgo
                if not threat_detected or confidence < RISK_THRESHOLD:
                    risk_level = 'low'
                elif confidence < 0.85:
                    risk_level = 'medium'
                else:
                    risk_level = 'high'
                
                return {
                    'threat_detected': threat_detected and confidence >= RISK_THRESHOLD,
                    'threat_type': threat_type if threat_type in THREAT_TYPES else 'none',
                    'confidence': confidence,
                    'risk_level': risk_level
                }
        except Exception as e:
            logger.error(f"Error parsing Ollama response: {str(e)}")
        
        return self._default_analysis()

    def _default_analysis(self):
        """Retorna análisis por defecto (sin amenaza detectada)"""
        return {
            'threat_detected': False,
            'threat_type': 'none',
            'confidence': 0.0,
            'risk_level': 'low'
        }
