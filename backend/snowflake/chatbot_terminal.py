import os
from dotenv import load_dotenv
from pathlib import Path
import sys

# --- CONFIGURACIÓN DE RUTAS ---
# 1. Añade la carpeta actual (backend/snowflake) al path de Python
#    para que pueda encontrar 'chatbot_flujo_completo' Y
#    para que 'chatbot_flujo_completo' pueda encontrar 'test.py', etc.
script_path = Path(__file__).parent
sys.path.append(str(script_path))

# 2. Encuentra y carga el archivo .env de la raíz del proyecto
root_path = script_path.parent.parent # Sube 2 niveles: (snowflake -> backend -> RAÍZ)
env_path = root_path / ".env"
    
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("--- ✅ Archivo .env cargado ---")
else:
    print(f"🚨 ADVERTENCIA: No se encontró el archivo .env en {env_path}")
    print("Asegúrate de que tu .env está en la carpeta raíz 'Hackmty_Smart_Intelligence'.")
    sys.exit(1)


# --- IMPORTAMOS TU LÓGICA ---
# Lo importamos DESPUÉS de configurar la ruta y el .env
try:
    from chatbot_flujo_completo import procesar_pregunta_completa
except ImportError:
    print("🚨 ERROR: No se pudo encontrar 'chatbot_flujo_completo.py'.")
    print("Asegúrate de que 'chatbot_terminal.py' y 'chatbot_flujo_completo.py' están en la misma carpeta.")
    sys.exit(1)


def main():
    """
    Función principal que corre el bucle del chatbot.
    """
    print("--- 🤖 Iniciando Chatbot de Terminal (RAG + Audio) ---")
    print("Escribe tu pregunta o 'salir' para terminar.")
    
    while True:
        # 1. Pide la pregunta
        pregunta_usuario = input("\nTú: ")
        
        # 2. Comando para salir
        if pregunta_usuario.lower() == 'salir':
            print("Chatbot: ¡Hasta luego!")
            break
        if not pregunta_usuario:
            continue
            
        # 3. Llama a tu lógica de IA
        respuesta_texto, archivo_audio = procesar_pregunta_completa(pregunta_usuario)
        
        # 4. Muestra los resultados
        if respuesta_texto and archivo_audio:
            print(f"\nChatbot: {respuesta_texto}")
            print(f"      [ 🎧 Audio guardado en: {archivo_audio} ]")
        else:
            print("\nChatbot: Lo siento, ocurrió un error al procesar tu solicitud.")

# --- Punto de entrada ---
if __name__ == "__main__":
    main()