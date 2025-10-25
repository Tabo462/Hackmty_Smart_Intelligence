import os
import requests  # Usamos requests, no la librería 'elevenlabs'
from dotenv import load_dotenv
from pathlib import Path

# --- Carga del .env desde la raíz ---
script_path = Path(__file__).parent
root_path = script_path.parent.parent # Sube 2 niveles
env_path = root_path / ".env"
load_dotenv(dotenv_path=env_path)

# --- Configuración de la API ---
api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    raise ValueError("No se encontró la ELEVENLABS_API_KEY en el .env")

# --- Constantes de la API ---
VOICE_ID = "pNInz6obpgDQGcFmaJgB" # ID de la voz "Adam"
API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
MODEL_ID = "eleven_multilingual_v2"

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": api_key
}

# --- FUNCIÓN QUE TU CHATBOT NECESITA ---
def generar_audio_elevenlabs(texto_para_audio, nombre_archivo_salida):
    """
    Toma un texto y lo convierte en un MP3 usando una llamada HTTP directa.
    """
    print(f"🎙️ Enviando a ElevenLabs (via HTTP): '{texto_para_audio[:50]}...'")
    data = { "text": texto_para_audio, "model_id": MODEL_ID }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers)
        response.raise_for_status() # Da error si algo sale mal

        with open(nombre_archivo_salida, 'wb') as f:
            f.write(response.content)
        
        # print(f"\n✅ ¡Audio guardado como '{nombre_archivo_salida}'!")
        return nombre_archivo_salida
        
    except requests.exceptions.HTTPError as http_err:
        print(f"🚨 Error HTTP en ElevenLabs: {http_err}")
        print(f"Respuesta del servidor: {response.text}")
        return None
    except Exception as e:
        print(f"Error al guardar audio de ElevenLabs: {e}")
        return None

# --- Bloque para Probar ESTE Archivo Directamente ---
if __name__ == "__main__":
    print("--- Probando el Módulo de Audio (ia_audio.py) ---")
    texto_ejemplo = "¡Hola! Esto es una prueba de audio directa."
    archivo = generar_audio_elevenlabs(texto_ejemplo, "audio_prueba_directa.mp3")
    if archivo:
        print(f"\n✅ ¡Audio guardado como '{archivo}'!")