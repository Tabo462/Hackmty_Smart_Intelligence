import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# --- Carga del .env desde la raíz ---
script_path = Path(__file__).parent
root_path = script_path.parent.parent # Sube 2 niveles: (snowflake -> backend -> RAÍZ)
env_path = root_path / ".env"
load_dotenv(dotenv_path=env_path)

# --- Configuración de la API ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("No se encontró la GEMINI_API_KEY en el .env")

genai.configure(api_key=api_key)

# --- Inicialización del Modelo ---
try:
    # Usamos el modelo que SÍ está en tu lista de acceso
    modelo_gemini = genai.GenerativeModel('models/gemini-2.5-flash')
except Exception as e:
    print(f"🚨 Error al inicializar el modelo Gemini: {e}")
    modelo_gemini = None

# --- FUNCIÓN QUE TU CHATBOT NECESITA ---
def generar_texto_gemini(prompt_usuario):
    """
    Toma un prompt (texto) del usuario y devuelve la respuesta de Gemini.
    """
    if not modelo_gemini:
        print("🚨 Error: El modelo Gemini no se inicializó correctamente.")
        return None

    print(f"🤖 Enviando a Gemini: '{prompt_usuario[:50]}...'")
    try:
        # Genera el contenido
        respuesta = modelo_gemini.generate_content(prompt_usuario)
        return respuesta.text
    except Exception as e:
        print(f"Error al llamar a Gemini API: {e}")
        return None

# --- Bloque para Probar ESTE Archivo Directamente ---
if __name__ == "__main__":
    print("--- Probando el Módulo de Gemini (ia_gemini.py) ---")
    mi_prompt = "Explain how AI works in a few words"
    resultado = generar_texto_gemini(mi_prompt)
    if resultado:
        print("\n✅ Respuesta de Gemini:")
        print(resultado)