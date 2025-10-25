import os
import snowflake.connector
from dotenv import load_dotenv
from pathlib import Path  # <-- Importamos la librería 'Path'

# --- COMIENZO DE LA CORRECCIÓN ---

# 1. Obtiene la ruta al directorio raíz del proyecto
script_path = Path(__file__).parent
root_path = script_path.parent.parent # Sube 2 niveles: (snowflake -> backend -> RAÍZ)
env_path = root_path / ".env"         # Apunta al .env en la raíz

# --- DEBUG: VAMOS A IMPRIMIR LA RUTA QUE ESTÁ BUSCANDO ---
print(f"--- 🔍 Buscando el archivo .env en: {env_path} ---")

# 2. Carga las variables de entorno (para la conexión real)
load_dotenv(dotenv_path=env_path)

# --- FIN DE LA CORRECCIÓN ---


# --- Configuración para la Conexión Real ---
SNOW_USER = os.getenv("SNOWFLAKE_USER")
SNOW_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOW_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOW_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOW_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOW_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

# --- DEBUG: VAMOS A IMPRIMIR LAS VARIABLES QUE ENCONTRÓ ---
print(f"--- 🔑 Variable SNOW_USER cargada: {SNOW_USER} ---")
print(f"--- 🔑 Variable SNOW_ACCOUNT cargada: {SNOW_ACCOUNT} ---")


# ===================================================================
# ... (El resto de tu código, 'obtener_datos_viaje' y 
# 'probar_conexion_snowflake', se queda exactamente igual) ...
# ===================================================================

# ... (código de 'obtener_datos_viaje') ...

def obtener_datos_viaje(pregunta_usuario):
    # ... (código de la función) ...
    pass # Solo para acortar el ejemplo

# ... (código de 'probar_conexion_snowflake') ...

def probar_conexion_snowflake():
    # ... (código de la función) ...
    pass # Solo para acortar el ejemplo

# --- Bloque de prueba ---
# ... (código del bloque de prueba) ...