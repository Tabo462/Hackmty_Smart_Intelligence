import os
import snowflake.connector
from dotenv import load_dotenv
from pathlib import Path  # <-- Importamos la librería 'Path'

# --- COMIENZO DE LA CORRECCIÓN ---

# 1. Obtiene la ruta al directorio raíz del proyecto
# __file__ es la ruta de este script (ia_snowflake.py)
# .parent es la carpeta que lo contiene (snowflake)
# .parent.parent es la carpeta padre de esa (backend)
# .parent.parent.parent es la raíz del proyecto (Hackmty_Smart_Intelligence)
# (CORRECCIÓN: Viendo tu estructura, solo son 2 .parent)
script_path = Path(__file__).parent
root_path = script_path.parent.parent # Sube 2 niveles: (snowflake -> backend -> RAÍZ)
env_path = root_path / ".env"         # Apunta al .env en la raíz

# 2. Carga las variables de entorno (para la conexión real)
# Le decimos a load_dotenv exactamente dónde buscar
load_dotenv(dotenv_path=env_path)

# --- FIN DE LA CORRECCIÓN ---


# --- Configuración para la Conexión Real ---
SNOW_USER = os.getenv("SNOWFLAKE_USER")
SNOW_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOW_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOW_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOW_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOW_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

# ===================================================================
# FUNCIÓN 1: OBTENER DATOS (La que usará tu chatbot ahora)
# ===================================================================

def obtener_datos_viaje(pregunta_usuario):
    """
    SIMULACIÓN: Esta función finge ir a Snowflake a buscar datos relevantes.
    """
    print(f"❄️ (Simulación) Buscando en Snowflake datos para: '{pregunta_usuario}'")
    
    # --- DATOS MOCK (DE MENTIRA) ---
    datos_encontrados = """
    - Restaurante: 'El Sabor Zapoteco'
      - Especialidad: Mole Negro
      - Opciones veganas: Sí, tamal de chepil.
      - Horario: 9:00 AM - 10:00 PM
    - Tour: 'Monte Albán Express'
      - Duración: 4 horas
      - Costo: $500 MXN
      - Incluye: Transporte, no incluye entrada.
    - Hotel: 'Oaxaca Dream'
      - Check-in: 3:00 PM
      - Check-out: 12:00 PM
    """
    # -------------------------------
    
    return datos_encontrados

# ===================================================================
# FUNCIÓN 2: PROBAR CONEXIÓN (La que usarás cuando tengas claves)
# ===================================================================

def probar_conexion_snowflake():
    """
    Intenta conectarse a Snowflake y ejecuta una consulta simple.
    """
    print(f"❄️ Intentando conectar a Snowflake (Cuenta: {SNOW_ACCOUNT}, Usuario: {SNOW_USER})...")
    
    # Validar que las variables esenciales existan
    if not all([SNOW_USER, SNOW_PASSWORD, SNOW_ACCOUNT, SNOW_WAREHOUSE, SNOW_DATABASE, SNOW_SCHEMA]):
        print("🚨 Error: Faltan variables de entorno de Snowflake en tu .env (USER, PASSWORD, ACCOUNT, WAREHOUSE, DATABASE, SCHEMA)")
        print("--- REVISA QUE TU .ENV ESTÉ EN LA CARPETA RAÍZ Y SE LLAME '.env' ---")
        return

    try:
        # Establecer la conexión
        conn = snowflake.connector.connect(
            user=SNOW_USER,
            password=SNOW_PASSWORD,
            account=SNOW_ACCOUNT,
            warehouse=SNOW_WAREHOUSE,
            database=SNOW_DATABASE,
            schema=SNOW_SCHEMA
        )
        
        print("✅ ¡Conexión exitosa!")
        
        # Probar una consulta simple
        print("Probando consulta 'SELECT 1'...")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        resultado = cursor.fetchone()
        
        if resultado and resultado[0] == 1:
            print("✅ ¡Consulta exitosa! Snowflake está listo.")
        else:
            print("🚨 La conexión funcionó, pero la consulta falló.")
            
        cursor.close()
        conn.close()
        
    except snowflake.connector.errors.DatabaseError as e:
        print(f"🚨 Error de Base de Datos: {e}")
        print("--- REVISA TUS CREDENCIALES (Especialmente la contraseña) ---")
    except Exception as e:
        print(f"🚨 Error inesperado: {e}")

# --- Bloque de prueba ---
if __name__ == "__main__":
    print("--- Probando Conexión Real de Snowflake ---")
    probar_conexion_snowflake()