# --- Imports ---
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
# Adjust List import based on Python version if needed (from typing import List)
from typing import Optional, List
import logging
import os
import pandas as pd
from pathlib import Path # <-- Added
from dotenv import load_dotenv # <-- Added
import google.generativeai as genai # <-- Added
import sys

# --- Logging and App Setup (No change) ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Load .env File ---
# Assumes main.py is in 'backend/' and .env is in the parent directory
try:
    script_path = Path(__file__).parent
    root_path = script_path.parent # Go up one level from 'backend'
    env_path = root_path / ".env"
    load_dotenv(dotenv_path=env_path)
    logger.info(f"Attempting to load .env from: {env_path}")
    if not env_path.exists():
        logger.warning(f".env file not found at {env_path}. Make sure it exists.")
except Exception as e:
    logger.error(f"Error loading .env file: {e}")


# --- Configure Gemini API ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
modelo_gemini = None # Initialize as None

if not GEMINI_API_KEY:
    logger.warning("⚠️ GEMINI_API_KEY not found in .env file. Chatbot functionality will be limited.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Use the stable Gemini Pro model
        modelo_gemini = genai.GenerativeModel('gemini-pro')
        logger.info("✅ Modelo Gemini inicializado exitosamente.")
    except Exception as e:
        logger.error(f"🚨 Error al inicializar el modelo Gemini: {e}")
        modelo_gemini = None # Ensure it's None if initialization fails

# --- Import Managers ---
from snowflake_manager import snowflake_manager
from elevenlabs_manager import elevenlabs_manager

# --- Reuse existing ia_gemini (same initialization used in snowflake/ia_gemini.py)
# Ensure Python can import the module located in backend/snowflake
sys.path.append(os.path.join(os.path.dirname(__file__), 'snowflake'))
try:
    from ia_gemini import generar_texto_gemini, modelo_gemini as ia_modelo_gemini
    logger.info("Imported generar_texto_gemini from ia_gemini.py")
except Exception as e:
    logger.warning(f"Could not import ia_gemini module: {e}")
    generar_texto_gemini = None
    ia_modelo_gemini = None

app = FastAPI(title="Smart Plate API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your actual frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chat message model
class ChatMessage(BaseModel):
    message: str

# Note: chat endpoint implemented further below re-uses ia_gemini.generate_texto_gemini

# --- CORS and Static Files (No change) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Ensure 'static' folder is inside the 'backend' folder for this path to work
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Load CSV Data ---
CSV_FILE_PATH = "(HackMTY2025)_ConsumptionPrediction_Dataset_v1.csv" # MUST be in the same folder as main.py
flight_data_df = None
csv_column_names = "CSV no cargado."

try:
    # Construct path relative to main.py
    csv_full_path = script_path / CSV_FILE_PATH
    flight_data_df = pd.read_csv(csv_full_path)
    flight_data_df.columns = flight_data_df.columns.str.strip()
    csv_column_names = ", ".join(flight_data_df.columns.tolist())
    logger.info(f"✅ CSV '{csv_full_path}' cargado. Columnas: {csv_column_names}")
except FileNotFoundError:
    logger.error(f"❌ Error: No se encontró el archivo CSV en '{csv_full_path}'.")
except Exception as e:
    logger.error(f"❌ Error al cargar CSV '{csv_full_path}': {e}")


# --- Pydantic Models (Added Chat models, ensure PredictRequest exists if needed) ---
class BarcodeRequest(BaseModel): barcode: str
class ProductRequest(BaseModel):
    barcode: str; productID: str; productName: str; quantity: int; lot: str; expirationDate: str
class BarcodeResponse(BaseModel):
    exists: bool; productID: Optional[str]=None; productName: Optional[str]=None; quantity: Optional[int]=None; lot: Optional[str]=None; expirationDate: Optional[str]=None; audio_base64: Optional[str]=None
class SaveResponse(BaseModel): success: bool; message: str
# Model for the prediction endpoint data
class PredictRequest(BaseModel):
     flight_id: str # Added based on frontend JSON
     origin: str
     flight_type: str
     service_type: str
     passenger_count: int
     product_name: List[str] # Corrected typing
     unit_cost: List[float] # Corrected typing (assuming costs can be decimals)
# Chat models
class ChatMessageRequest(BaseModel): message: str
class ChatMessageResponse(BaseModel): reply: str

# --- Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Added link to main_code based on previous version
    return """<!DOCTYPE html><html><head><title>API Root</title></head><body>
            <h1>🚀 API Backend</h1><p>Endpoints disponibles:</p><ul>
            <li><a href="/scanner">/scanner</a> - Interfaz de escaneo</li>
            <li><a href="/main_code">/main_code</a> - Interfaz Principal (Frontend)</li>
            <li>/api/check_barcode (POST)</li><li>/api/save_product (POST)</li>
            <li>/api/predict (POST)</li><li>/api/chat (POST)</li><li>/api/health (GET)</li>
            </ul></body></html>"""

@app.get("/scanner", response_class=HTMLResponse)
async def scanner_page():
    try:
        # Assumes static/scanner.html exists inside the backend folder
        with open("static/scanner.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        logger.error("scanner.html not found in static folder")
        return HTMLResponse(content="<h1>Error: scanner.html not found</h1>", status_code=404)

@app.get("/main_code", response_class=HTMLResponse)
async def main_code_page():
    try:
         # Correct path assuming frontend is sibling to backend
        frontend_index_path = root_path / "frontend" / "index.html"
        logger.info(f"Attempting to serve frontend index from: {frontend_index_path}")
        with open(frontend_index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        logger.error(f"index.html not found at {frontend_index_path}")
        return HTMLResponse(content="<h1>Error: Frontend index.html not found</h1>", status_code=404)
    except Exception as e:
        logger.error(f"Error serving main_code_page: {e}")
        raise HTTPException(status_code=500, detail="Could not load main page.")

# --- Barcode and Save Endpoints (No change needed) ---
@app.post("/api/check_barcode", response_model=BarcodeResponse)
async def check_barcode(request: BarcodeRequest):
     # ... (Existing code) ...
    try:
        result = snowflake_manager.check_barcode_exists(request.barcode)
        if result is None: raise HTTPException(status_code=500, detail="DB Error")
        if result["exists"]:
            return BarcodeResponse(exists=True, **result) # Simplified return
        else:
            audio_base64 = elevenlabs_manager.text_to_speech_base64("El producto no está en la base de datos")
            return BarcodeResponse(exists=False, audio_base64=audio_base64)
    except Exception as e:
        logger.error(f"❌ Error check_barcode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/save_product", response_model=SaveResponse)
async def save_product(request: ProductRequest):
    # ... (Existing code) ...
    try:
        success = snowflake_manager.save_product(
            barcode=request.barcode, product_id=request.productID, product_name=request.productName,
            quantity=request.quantity, lot=request.lot, expiration_date=request.expirationDate
        )
        if success:
            return SaveResponse(success=True, message="Producto guardado")
        else:
             raise HTTPException(status_code=500, detail="Error saving product")
    except Exception as e:
        logger.error(f"❌ Error save_product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Health Check (No change) ---
@app.get("/api/health")
async def health_check():
    # ... (Existing code) ...
     return {
        "status": "healthy",
        "snowflake_connected": snowflake_manager.connection is not None,
        # "elevenlabs_configured": elevenlabs_manager.api_key is not None # Check if still needed
        "gemini_model_loaded": modelo_gemini is not None
     }

# --- Prediction Endpoint (Ensure it exists if needed by frontend) ---
@app.post("/api/predict")
async def predict_consumption(data: PredictRequest):
    logger.info(f"🔄 Recibiendo request de predicción para Flight ID: {data.flight_id}") # Log flight_id
    try:
        # IMPORTANT: Make sure this import path is correct relative to main.py
        # If 'aidata' is a folder at the same level as 'backend', this might need adjustment
        from aidata.Random_Forest_Regression import AirlineConsumptionPredictor

        # Assuming model file is in the same directory or accessible path
        model_path = "airline_consumption_model.joblib" # Or full path if needed
        predictor = AirlineConsumptionPredictor.load_trained_model(model_path)

        if predictor is None:
            logger.error(f"Modelo no encontrado o no cargado desde {model_path}")
            raise HTTPException(status_code=500, detail=f"Model not loaded from {model_path}")

        predictions = []
        total_units = 0
        total_cost = 0.0 # Use float

        for i, (product_name, unit_cost) in enumerate(zip(data.product_name, data.unit_cost)):
            # Assuming predict_consumption expects these arguments
            prediction_float = predictor.predict_consumption(
                origin=data.origin, flight_type=data.flight_type, service_type=data.service_type,
                passenger_count=data.passenger_count, product_name=product_name, unit_cost=unit_cost,
                has_issues=0 # Assuming 0 for no issues by default
            )
            # Ensure prediction is an integer if needed by logic, but keep cost calc float
            prediction_units = int(round(prediction_float))

            product_total_cost = prediction_units * unit_cost
            total_units += prediction_units
            total_cost += product_total_cost

            predictions.append({
                "product_name": product_name, "unit_cost": unit_cost,
                "predicted_units": prediction_units, "total_cost": round(product_total_cost, 2)
            })

        logger.info(f"✅ Predicción exitosa! Total: {total_units} unidades, ${total_cost:.2f}")

        # Calculate totals safely, avoid division by zero
        units_per_passenger = round(total_units / data.passenger_count, 2) if data.passenger_count > 0 else 0
        cost_per_passenger = round(total_cost / data.passenger_count, 2) if data.passenger_count > 0 else 0

        return {
            "flight_info": {
                "flight_id": data.flight_id, # Include flight_id in response
                "origin": data.origin, "flight_type": data.flight_type,
                "service_type": data.service_type, "passenger_count": data.passenger_count
            },
            "products": predictions,
            "totals": {
                "total_units": total_units, "total_cost": round(total_cost, 2),
                "units_per_passenger": units_per_passenger,
                "cost_per_passenger": cost_per_passenger
            }
        }

    except ImportError as ie:
         logger.error(f"❌ Error importing prediction module: {ie}. Check path 'aidata.Random_Forest_Regression'")
         raise HTTPException(status_code=500, detail=f"Prediction module import error: {ie}")
    except FileNotFoundError as fnfe:
         logger.error(f"❌ Error loading model: {fnfe}. Ensure '{model_path}' exists.")
         raise HTTPException(status_code=500, detail=f"Model file not found: {fnfe}")
    except Exception as e:
        logger.exception(f"❌ Error inesperado en predict_consumption: {e}") # Use logger.exception for full traceback
        raise HTTPException(status_code=500, detail=f"Internal prediction error: {str(e)}")

# --- List all available files in HackMTY2025_ChallengeDimensions ---
data_root_folder = script_path / "HackMTY2025_ChallengeDimensions"

available_files = []
for root, dirs, files in os.walk(data_root_folder):
    for file in files:
        if file.lower().endswith((".csv", ".xlsx", ".xls", ".pdf")):
            relative_path = os.path.relpath(os.path.join(root, file), data_root_folder)
            available_files.append(relative_path)

# --- Chatbot Endpoint (Using actual Gemini logic) ---
@app.post("/api/chat", response_model=ChatMessageResponse)
async def handle_chat_message(request: ChatMessageRequest):
    user_message = request.message
    logger.info(f"💬 Mensaje recibido del chat: {user_message}")

    # Prefer using the tested function from ia_gemini if available
    if 'generar_texto_gemini' in globals() and generar_texto_gemini is not None:
        use_external_generador = True
    else:
        use_external_generador = False

    if not use_external_generador and not modelo_gemini:
        logger.error("🚨 Modelo Gemini no está cargado. No se puede procesar el chat.")
        raise HTTPException(status_code=503, detail="Chat service unavailable (Model not loaded).")

    prompt_context = f"""
You are an expert assistant for airline catering data analysis.
You have access to structured and unstructured data located in the folder:
'HackMTY2025_ChallengeDimensions' which contains multiple Excel, CSV, and PDF files
with consumption, cost, and operational metrics.

Available data columns (from the main CSV): {csv_column_names}

User asks: "{user_message}"

Instructions:
1. Respond with professionalism and conciseness. Prioritize clarity and tone balance—formal yet approachable.
2. When listing items, use clean formatting such as:
   - Bulleted points
   - Numbered lists (1., 2., 3.)
   - Short paragraphs
3. When the question involves specific data, mention that you can consult the relevant file or dataset in the HackMTY2025_ChallengeDimensions folder.
4. Avoid verbose explanations or unnecessary preambles. Go straight to the insight.
5. If the user's question is general or exploratory, summarize the key aspects clearly and elegantly.
6. If unsure about specific data, guide the user on how to specify what they need (e.g., file name, flight, or product).
"""

    try:
        logger.info(f"🤖 Enviando a Gemini: '{prompt_context[:100]}...'" )
        # If available, use the tested generar_texto_gemini function from ia_gemini.py
        if use_external_generador:
            try:
                response_text = generar_texto_gemini(prompt_context)
            except Exception as e:
                logger.error(f"Error calling generar_texto_gemini: {e}")
                raise HTTPException(status_code=500, detail=f"Error generating response: {e}")
        else:
            try:
                respuesta = modelo_gemini.generate_content(prompt_context)
                response_text = respuesta.text
            except Exception as e:
                logger.error(f"Error generating content with modelo_gemini: {e}")
                raise HTTPException(status_code=500, detail=f"Error generating response: {e}")
            
        # Basic cleanup to remove potential leftover markdown list starters
        response_text = response_text.replace("* ", "").replace("- ", "")
        lines = response_text.split('\n')
        cleaned_lines = [line.lstrip('0123456789. ') for line in lines]
        gemini_reply = "\n".join(cleaned_lines)

        logger.info(f"🤖 Respuesta recibida (len {len(response_text) if response_text else 0})...")
        return ChatMessageResponse(reply=response_text)

    except Exception as e:
        logger.error(f"❌ Error al llamar a Gemini API: {e}")
        # Provide a user-friendly error, but log the specific details
        raise HTTPException(status_code=500, detail="Error communicating with the AI assistant.")


# --- Startup/Shutdown Events (No change) ---
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Iniciando Web Scanner API")
    if snowflake_manager.connect():
        snowflake_manager.create_table_if_not_exists()
    else:
        logger.warning("⚠️ No se pudo conectar a Snowflake")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Cerrando Web Scanner API")
    snowflake_manager.disconnect()

# --- Run Command ---
if __name__ == "__main__":
    import uvicorn
    # Corrected host for better accessibility if needed, 127.0.0.1 limits to local machine only
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)