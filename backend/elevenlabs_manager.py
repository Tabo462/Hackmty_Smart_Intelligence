import os
import requests
import base64
from dotenv import load_dotenv
from typing import Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class ElevenLabsManager:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")
        self.model_id = "eleven_multilingual_v2"
        
        if not self.api_key:
            logger.warning("⚠️ ELEVENLABS_API_KEY no encontrada en variables de entorno")
    
    def text_to_speech_base64(self, text: str) -> Optional[str]:
        """
        Convierte texto a audio usando ElevenLabs API y devuelve el audio en base64
        """
        if not self.api_key:
            logger.error("❌ API key de ElevenLabs no configurada")
            return None
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        try:
            logger.info(f"🎙️ Generando audio para: '{text[:50]}...'")
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            # Convertir el audio a base64
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            logger.info("✅ Audio generado y convertido a base64")
            return audio_base64
            
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"❌ Error HTTP en ElevenLabs: {http_err}")
            if hasattr(http_err, 'response') and http_err.response is not None:
                logger.error(f"Respuesta del servidor: {http_err.response.text}")
            return None
        except Exception as e:
            logger.error(f"❌ Error generando audio: {e}")
            return None
    
    def text_to_speech_file(self, text: str, filename: str) -> bool:
        """
        Convierte texto a audio y lo guarda en un archivo
        """
        if not self.api_key:
            logger.error("❌ API key de ElevenLabs no configurada")
            return False
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        try:
            logger.info(f"🎙️ Generando audio para archivo: '{text[:50]}...'")
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Audio guardado en: {filename}")
            return True
            
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"❌ Error HTTP en ElevenLabs: {http_err}")
            return False
        except Exception as e:
            logger.error(f"❌ Error guardando audio: {e}")
            return False

# Instancia global del manager
elevenlabs_manager = ElevenLabsManager()
