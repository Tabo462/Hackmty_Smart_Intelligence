import sys

# --- Importamos TUS funciones (de tus otros archivos) ---
# Asumimos que todos están en la misma carpeta
try:
    # --- ESTA ES LA CORRECCIÓN ---
    # Simplemente importa desde el nombre del archivo,
    # ya que están en la misma carpeta
    from ia_gemini import generar_texto_gemini 
    from ia_audio import generar_audio_elevenlabs
    from ia_snowflake import obtener_datos_viaje
    # ----------------------------
except ImportError as e:
    print(f"🚨 ERROR FATAL: No se pudo importar un módulo.")
    print("Revisa que 'ia_gemini.py', 'ia_audio.py', y 'ia_snowflake.py' estén en la misma carpeta.")
    print(f"Error específico: {e}")
    sys.exit(1)

# ... (El resto de tu código de 'procesar_pregunta_completa' 
# se queda exactamente igual) ...

def procesar_pregunta_completa(pregunta_usuario):
    """
    Orquesta todo el flujo del chatbot:
    1. Busca datos (simulados) en Snowflake
    2. Genera texto con Gemini (RAG)
    3. Genera audio con ElevenLabs
    """
    print(f"--- 🟢 Iniciando Flujo para: '{pregunta_usuario}' ---")
    
    # 1. Recuperar (Retrieval)
    # Llama a tu función de Snowflake (que por ahora usa datos mock)
    contexto_db = obtener_datos_viaje(pregunta_usuario)
    
    # 2. Aumentar (Augment)
    # Creamos el prompt para Gemini
    prompt_rag = f"""
    Eres un asistente de viajes experto en Oaxaca.
    Usa SOLAMENTE la siguiente información de contexto para responder la pregunta del usuario.
    Sé breve, amigable y directo.
    
    Contexto de la Base de Datos:
    {contexto_db}
    
    Pregunta del Usuario:
    {pregunta_usuario}
    
    Tu respuesta:
    """
    
    # 3. Generar (Generate) - Texto
    respuesta_texto = generar_texto_gemini(prompt_rag)
    
    if not respuesta_texto:
        print("🚨 Error: Gemini no devolvió texto.")
        return None, None
        
    print(f"🤖 Respuesta de Gemini: {respuesta_texto}")
    
    # 4. Generar (Generate) - Audio
    nombre_archivo = "respuesta_final_audio.mp3"
    generar_audio_elevenlabs(respuesta_texto, nombre_archivo)
    
    print(f"--- ✅ Flujo Completo Terminado. Audio en: {nombre_archivo} ---")
    return respuesta_texto, nombre_archivo