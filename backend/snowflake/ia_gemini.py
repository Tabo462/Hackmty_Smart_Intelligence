import google.generativeai as genai
from dotenv import load_dotenv
import os

# Cargar las variables del archivo .env
load_dotenv()

# Obtener la API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("No se encontró la GEMINI_API_KEY en el archivo .env")

# Configurar el cliente
genai.configure(api_key=api_key)

try:
    # --- ¡LA CORRECCIÓN! ---
    # Usamos uno de los modelos de TU lista. 
    # 'models/gemini-2.5-flash' es perfecto para un hackathon (rápido y potente).
    client = genai.GenerativeModel('models/gemini-2.5-flash')

    # Hacer la petición
    response = client.generate_content(
        "Explain how AI works in a few words"
    )

    print(response.text)

except Exception as e:
    print(f"Ocurrió un error: {e}")