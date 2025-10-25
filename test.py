from google import genai
from dotenv import load_dotenv
import os

# Cargar las variables del archivo .env
load_dotenv()

# Obtener la API key
api_key = os.getenv("GEMINI_API_KEY")

# Crear el cliente
client = genai.Client(api_key=api_key)

# Hacer una petición
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain how AI works in a few words"
)

print(response.text)

