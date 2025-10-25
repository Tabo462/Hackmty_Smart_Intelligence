import os
import requests  # Usamos requests en lugar de 'elevenlabs'
from dotenv import load_dotenv

# --- Configuración Inicial ---
load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    raise ValueError("No se encontró la ELEVENLABS_API_KEY")

# --- Constantes de la API (lo que hace la librería por detrás) ---
VOICE_ID = "pNInz6obpgDQGcFmaJgB" # Este es el ID de la voz "Adam"
API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
MODEL_ID = "eleven_multilingual_v2"

# Encabezados para la autenticación
headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": api_key
}

# --- Definición de la Función ---
def generar_audio_elevenlabs(texto_para_audio, nombre_archivo_salida):
    """
    Toma un texto y lo convierte en un MP3 usando una llamada HTTP directa.
    """
    print(f"🎙️ Enviando a ElevenLabs (via HTTP): '{texto_para_audio[:50]}...'")

    # Datos que enviamos en el body
    data = {
        "text": texto_para_audio,
        "model_id": MODEL_ID
    }
    
    try:
        # --- Hacemos la llamada HTTP directa ---
        response = requests.post(API_URL, json=data, headers=headers)
        
        # Si algo sale mal (ej: mala API key), esto dará un error
        response.raise_for_status() 

        # --- Guardamos el archivo de audio (MP3) ---
        # 'response.content' tiene los datos binarios del audio
        with open(nombre_archivo_salida, 'wb') as f:
            f.write(response.content)
        
        print(f"\n✅ ¡Audio guardado como '{nombre_archivo_salida}'!")
        return nombre_archivo_salida
        
    except requests.exceptions.HTTPError as http_err:
        print(f"🚨 Error HTTP: {http_err}")
        print(f"Respuesta del servidor: {response.text}") # Muestra el error
        return None
    except Exception as e:
        print(f"Error al llamar a ElevenLabs API: {e}")
        return None

# --- Bloque de prueba (sin cambios) ---
if __name__ == "__main__":
    print("--- Probando el Módulo de ElevenLabs ---")
    texto_ejemplo = "Fer, gracias a ti el código funciono. Eres la mejor!"
    generar_audio_elevenlabs(texto_ejemplo, "mi_audio_de_prueba.mp3")