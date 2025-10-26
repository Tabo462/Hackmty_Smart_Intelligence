from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List
import logging
import os
import random
from aidata.Random_Forest_Regression import AirlineConsumptionPredictor
import pandas as pd
from typing import Optional
from SnowflakeFinal import SnowflakeConnection
from elevenlabs_manager import elevenlabs_manager
import google.generativeai as genai 
import sys
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta

# Global variable for the Snowflake Connection
sf = SnowflakeConnection()

def generate_self_signed_cert(cert_file="cert.pem", key_file="key.pem"):
    """Genera certificados SSL autofirmados si no existen"""
    cert_path = Path(cert_file)
    key_path = Path(key_file)
    
    if cert_path.exists() and key_path.exists():
        print("✅ Certificados SSL ya existen")
        return cert_file, key_file
    
    print("🔐 Generando certificados SSL autofirmados...")
    
    # Generar clave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Crear el certificado
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Smart Intelligence"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Guardar certificado
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    
    # Guardar clave privada
    key_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    )
    
    print(f"✅ Certificados generados: {cert_file}, {key_file}")
    return cert_file, key_file


# Global variable for Gemini
# --- Configure Gemini API ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
modelo_gemini = None # Initialize as None

if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY not found in .env file. Chatbot functionality will be limited.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Use the stable Gemini 2.5 Flash model
        modelo_gemini = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ Modelo Gemini inicializado exitosamente.")
    except Exception as e:
        print(f"🚨 Error al inicializar el modelo Gemini: {e}")
        modelo_gemini = None # Ensure it's None if initialization fails

try:
    from snowflake.ia_gemini import generar_texto_gemini, modelo_gemini as ia_modelo_gemini
    print("Imported generar_texto_gemini from ia_gemini.py")
except Exception as e:
    print(f"Could not import ia_gemini module: {e}")
    generar_texto_gemini = None
    ia_modelo_gemini = None

script_path = Path(__file__).parent
data_root_folder = script_path / "HackMTY2025_ChallengeDimensions"

available_files = []
for root, dirs, files in os.walk(data_root_folder):
    for file in files:
        if file.lower().endswith((".csv", ".xlsx", ".xls", ".pdf")):
            relative_path = os.path.relpath(os.path.join(root, file), data_root_folder)
            available_files.append(relative_path)

# --- Load CSV Data ---
CSV_FILE_PATH = "aidata/(HackMTY2025)_ConsumptionPrediction_Dataset_v1.csv" # MUST be in the same folder as main.py
flight_data_df = None
csv_column_names = "CSV no cargado."

try:
    # Construct path relative to main.py
    csv_full_path = script_path / CSV_FILE_PATH
    flight_data_df = pd.read_csv(csv_full_path)
    flight_data_df.columns = flight_data_df.columns.str.strip()
    csv_column_names = ", ".join(flight_data_df.columns.tolist())
    print(f"✅ CSV '{csv_full_path}' cargado. Columnas: {csv_column_names}")
except FileNotFoundError:
    print(f"❌ Error: No se encontró el archivo CSV en '{csv_full_path}'.")
except Exception as e:
    print(f"❌ Error al cargar CSV '{csv_full_path}': {e}")

predictor = AirlineConsumptionPredictor.load_trained_model("airline_consumption_model")
if predictor is None:
    print("❌ Failed to load model. Make sure to run Random_Forest_Regression.py first to train and save the model.")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(title="Smart Intelligence API", version="1.0.0")

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo para la predicción
class PredictRequest(BaseModel):
    flight_id: str
    origin: str
    flight_type: str
    service_type: str
    passenger_count: int
    product_name: List[str]
    unit_cost: List[float]

class BarcodeResponse(BaseModel):
    exists: bool
    productID: Optional[str] = None
    productName: Optional[str] = None
    quantity: Optional[int] = None
    lot: Optional[str] = None
    expirationDate: Optional[str] = None
    audio_base64: Optional[str] = None

class BarcodeRequest(BaseModel):
    barcode: str

class SaveResponse(BaseModel):
    success: bool
    message: str

class ProductRequest(BaseModel):
    barcode: str
    productID: str
    productName: str
    quantity: int
    lot: str
    expirationDate: str

class ChatMessage(BaseModel):
    message: str

class ChatMessageRequest(BaseModel): message: str
class ChatMessageResponse(BaseModel): reply: str

# Ruta raíz - redirige a index.html
@app.get("/")
async def root():
    """Redirige a index.html"""
    try:
        frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/index.html")
        return FileResponse(frontend_path)
    except:
        return HTMLResponse("""
        <h1>🚀 Smart Intelligence API</h1>
        <p>Backend funcionando correctamente!</p>
        <p><a href="/docs">Ver documentación de la API</a></p>
        <p><a href="/index.html">Ir al frontend</a></p>
        """)

# Ruta principal - sirve el frontend
@app.get("/index.html")
async def serve_frontend():
    """Servir la página principal del frontend"""
    try:
        frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/index.html")
        return FileResponse(frontend_path)
    except Exception as e:
        return HTMLResponse(f"""
        <h1>❌ Error cargando frontend</h1>
        <p>Error: {str(e)}</p>
        <p><a href="/docs">Ver documentación de la API</a></p>
        """)

# Servir la página de predicciones
@app.get("/pre_flight_predictions.html")
async def serve_predictions():
    """Servir la página de predicciones"""
    try:
        predictions_path = os.path.join(os.path.dirname(__file__), "../frontend/pre_flight_predictions.html")
        return FileResponse(predictions_path)
    except:
        return HTMLResponse("<h1>Error: No se pudo cargar la página de predicciones</h1>")
    
# Servir la página de predicciones
@app.get("/exp_adding.html")
async def serve_exp_adding():
    """Servir la página de exp_adding"""
    try:
        exp_adding_path = os.path.join(os.path.dirname(__file__), "../frontend/exp_adding.html")
        return FileResponse(exp_adding_path)
    except:
        return HTMLResponse("<h1>Error: No se pudo cargar la página de exp_adding</h1>")
    
@app.get("/exp_dashboard.html")
async def serve_exp_dashboard():
    """Servir la página de exp_dashboard"""
    try:
        exp_dashboard_path = os.path.join(os.path.dirname(__file__), "../frontend/exp_dashboard.html")
        return FileResponse(exp_dashboard_path)
    except:
        return HTMLResponse("<h1>Error: No se pudo cargar la página de exp_dashboard</h1>")

# Servir archivos estáticos (CSS, JS, imágenes)
@app.get("/media_files/{file_path:path}")
async def serve_media(file_path: str):
    """Servir archivos de media"""
    try:
        media_path = os.path.join(os.path.dirname(__file__), "../frontend/media_files", file_path)
        return FileResponse(media_path)
    except:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

# Endpoint de predicción (SIMULADO para testing)
@app.post("/api/predict")
async def predict_consumption(data: PredictRequest):
    """
    Endpoint para predecir el consumo (VERSIÓN SIMULADA)
    """

    try:
        logger.info(f"🔄 Recibiendo request de predicción: {data.flight_id}")
        
        # SIMULACIÓN: Generar predicciones aleatorias para cada producto
        predictions = []
        total_units = 0
        total_cost = 0
        
        for product_name, unit_cost in zip(data.product_name, data.unit_cost):
            # Generar una predicción aleatoria basada en el número de pasajeros
            current_prediction = predictor.predict_consumption(
                origin=data.origin,
                flight_type=data.flight_type,
                service_type=data.service_type,
                passenger_count=data.passenger_count,
                product_name=product_name,
                unit_cost=unit_cost,
                has_issues=0
            )
            total_units += current_prediction
            total_cost += current_prediction * unit_cost
            predictions.append({
                "product_name": product_name,
                "unit_cost": unit_cost,
                "predicted_units": current_prediction,
                "total_cost": round(current_prediction * unit_cost, 2)
            })

        logger.info(f"✅ Predicción exitosa! Total: {total_units} unidades, ${total_cost:.2f}")

        return {
            "flight_info": {
                "flight_id": data.flight_id,
                "origin": data.origin,
                "flight_type": data.flight_type,
                "service_type": data.service_type,
                "passenger_count": data.passenger_count
            },
            "products": predictions,
            "totals": {
                "total_units": total_units,
                "total_cost": round(total_cost, 2),
                "units_per_passenger": round(total_units / data.passenger_count, 2),
                "cost_per_passenger": round(total_cost / data.passenger_count, 2)
            }
        }

    except Exception as e:
        logger.error(f"❌ Error en predict_consumption: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
@app.post("/api/check_barcode", response_model=BarcodeResponse)
async def check_barcode(request: BarcodeRequest):
    """
    Verifica si un código de barras existe en la base de datos
    """
    logger.info(f"🔍 Verificando barcode: {request.barcode}")
    try:
        logger.info(f"🔍 Verificando barcode: {request.barcode.strip()}")

        result = sf.check_barcode_exists(request.barcode.strip())

        if result is None:
            raise HTTPException(status_code=500, detail="Error conectando a la base de datos")
        
        if result["exists"]:
            # Producto existe
            logger.info(f"✅ Producto encontrado: {result['product_info']['product_name']}")
            return BarcodeResponse(
                exists=True,
                productID=result["product_info"]["product_id"],
                productName=result["product_info"]["product_name"],
                quantity=result["product_info"]["quantity"],
                lot=result["product_info"]["lot_number"],
                expirationDate=str(result["product_info"]["exp_date"])
            )
        else:
            # Producto no existe - generar audio
            logger.info("❌ Producto no encontrado - generando audio")
            audio_text = "El producto no está en la base de datos"
            audio_base64 = elevenlabs_manager.text_to_speech_base64(audio_text)
            
            return BarcodeResponse(
                exists=False,
                audio_base64=audio_base64
            )
    
            
    except Exception as e:
        logger.error(f"❌ Error en check_barcode: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/api/save_product", response_model=SaveResponse)
async def save_product(request: ProductRequest):
    """
    Guarda o actualiza un producto en la base de datos
    """
    try:
        logger.info(f"💾 Guardando producto: {request.barcode}")
        
        result = sf.check_barcode_exists(request.barcode.strip())

        if result["exists"]:
            logger.info("⚠️ El producto ya existe. Actualizando información.")
            if sf.update_existing_product(barcode=request.barcode.strip(), product_id=request.productID, product_name=request.productName, quantity=request.quantity, lot_number=request.lot, exp_date=request.expirationDate)["success"]:
                logger.info("✅ Producto actualizado correctamente.")
                return SaveResponse(
                    success=True,
                    message="Producto guardado exitosamente"
                )
            else:
                logger.error("❌ Error actualizando el producto existente.")
                raise HTTPException(status_code=500, detail="Error actualizando el producto existente")
        else:
            logger.info("🆕 Producto nuevo. Insertando en la base de datos.")
            single_product_dict = {
                'barcode': request.barcode.strip(),
                'product_id': request.productID,
                'product_name': request.productName,
                'lot_number': request.lot,
                'quantity': request.quantity,
                'exp_date': request.expirationDate
            }
            if sf.add_product_data(single_product_dict):
                logger.info("✅ Producto insertado correctamente.")
                return SaveResponse(
                    success=True,
                    message="Producto guardado exitosamente"
                )
            else:
                logger.error("❌ Error insertando el nuevo producto.")
                raise HTTPException(status_code=500, detail="Error insertando el nuevo producto")            
    except Exception as e:
        logger.error(f"❌ Error en save_product: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# Endpoints para el Dashboard
@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Obtiene métricas generales para el dashboard"""
    try:
        logger.info("📊 Obteniendo métricas del dashboard")
        
        # Total de productos
        total_query = "SELECT COUNT(*) as total FROM PRODUCT_DATA"
        total_result = sf.execute_query(total_query)
        total_products = total_result[0][0] if total_result else 0
        
        # Productos próximos a vencer (30 días)
        expiring_query = """
        SELECT COUNT(*) as expiring 
        FROM PRODUCT_DATA 
        WHERE Exp_Date <= DATEADD(day, 30, CURRENT_DATE()) 
        AND Exp_Date >= CURRENT_DATE()
        """
        expiring_result = sf.execute_query(expiring_query)
        expiring_products = expiring_result[0][0] if expiring_result else 0
        
        # Productos vencidos
        expired_query = """
        SELECT COUNT(*) as expired 
        FROM PRODUCT_DATA 
        WHERE Exp_Date < CURRENT_DATE()
        """
        expired_result = sf.execute_query(expired_query)
        expired_products = expired_result[0][0] if expired_result else 0
        
        # Suma total de cantidades
        quantity_query = "SELECT SUM(Quantity) as total_quantity FROM PRODUCT_DATA"
        quantity_result = sf.execute_query(quantity_query)
        total_quantity = quantity_result[0][0] if quantity_result and quantity_result[0][0] else 0
        
        return {
            "total_products": total_products,
            "expiring_products": expiring_products,
            "expired_products": expired_products,
            "total_quantity": total_quantity,
            "healthy_products": total_products - expiring_products - expired_products
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo métricas: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo métricas: {str(e)}")

@app.get("/api/dashboard/products")
async def get_dashboard_products():
    """Obtiene lista de productos para el dashboard"""
    try:
        logger.info("📋 Obteniendo lista de productos")
        
        query = """
        SELECT 
            Barcode,
            ProductID,
            ProductName,
            LotNumber,
            Quantity,
            Exp_Date,
            CASE 
                WHEN Exp_Date < CURRENT_DATE() THEN 'Expired'
                WHEN Exp_Date <= DATEADD(day, 30, CURRENT_DATE()) THEN 'Expiring Soon'
                ELSE 'Healthy'
            END as Status
        FROM PRODUCT_DATA 
        ORDER BY Exp_Date ASC
        """
        
        result = sf.execute_query(query)
        
        if not result:
            return {"products": []}
        
        products = []
        for row in result:
            products.append({
                "barcode": row[0],
                "product_id": row[1],
                "product_name": row[2],
                "lot_number": row[3],
                "quantity": row[4],
                "exp_date": str(row[5]),
                "status": row[6]
            })
        
        return {"products": products}
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo productos: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo productos: {str(e)}")

@app.get("/api/dashboard/charts")
async def get_dashboard_charts():
    """Obtiene datos para gráficos del dashboard"""
    try:
        logger.info("📈 Obteniendo datos para gráficos")
        
        # Productos por estado
        status_query = """
        SELECT 
            CASE 
                WHEN Exp_Date < CURRENT_DATE() THEN 'Expired'
                WHEN Exp_Date <= DATEADD(day, 30, CURRENT_DATE()) THEN 'Expiring Soon'
                ELSE 'Healthy'
            END as Status,
            COUNT(*) as Count
        FROM PRODUCT_DATA 
        GROUP BY Status
        ORDER BY Count DESC
        """
        
        status_result = sf.execute_query(status_query)
        status_data = {}
        if status_result:
            for row in status_result:
                status_data[row[0]] = row[1]
        
        # Top 10 productos por cantidad
        top_products_query = """
        SELECT ProductName, SUM(Quantity) as TotalQuantity
        FROM PRODUCT_DATA 
        GROUP BY ProductName
        ORDER BY TotalQuantity DESC
        LIMIT 10
        """
        
        top_result = sf.execute_query(top_products_query)
        top_products = []
        if top_result:
            for row in top_result:
                top_products.append({
                    "name": row[0],
                    "quantity": row[1]
                })
        
        # Productos próximos a vencer por fecha
        expiring_timeline_query = """
        SELECT 
            Exp_Date,
            COUNT(*) as Count
        FROM PRODUCT_DATA 
        WHERE Exp_Date <= DATEADD(day, 30, CURRENT_DATE()) 
        AND Exp_Date >= CURRENT_DATE()
        GROUP BY Exp_Date
        ORDER BY Exp_Date ASC
        """
        
        timeline_result = sf.execute_query(expiring_timeline_query)
        timeline_data = []
        if timeline_result:
            for row in timeline_result:
                timeline_data.append({
                    "date": str(row[0]),
                    "count": row[1]
                })
        
        return {
            "status_distribution": status_data,
            "top_products": top_products,
            "expiring_timeline": timeline_data
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo datos de gráficos: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos de gráficos: {str(e)}")

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
    'HackMTY2025_ChallengeDimensions', which contains multiple subfolders and files
    with consumption, cost, and operational metrics.

    The available files include (non-exhaustive list):
    {', '.join(available_files[:15])}...

    Main dataset columns (from the main CSV): {csv_column_names}

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


# Endpoint de salud
@app.get("/api/health")
async def health_check():
    """Endpoint de salud para verificar el estado de la API"""
    return {
        "status": "healthy",
        "message": "Backend funcionando correctamente",
        "endpoints": [
            "/api/predict - POST - Predicciones",
            "/api/dashboard/metrics - GET - Métricas del dashboard",
            "/api/dashboard/products - GET - Lista de productos",
            "/api/dashboard/charts - GET - Datos para gráficos",
            "/api/health - GET - Estado del sistema",
            "/ - GET - Página principal",
            "/predictions - GET - Página de predicciones"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    import socket
    import sys
    
    # Función para obtener la IP local
    def get_local_ip():
        """Obtiene la IP local de la máquina"""
        try:
            # Conectarse a un servidor externo para obtener la IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"
    
    local_ip = get_local_ip()
    
    if not sf.connect():
        print("❌ Failed to connect to Snowflake. Please check your credentials.")
    
    print("🚀 Iniciando servidor FastAPI...")
    print("\n" + "="*60)
    print("📍 URLs disponibles (HTTP - Local):")
    print("="*60)
    print(f"📱 Frontend local:  http://localhost:8001/")
    print(f"📦 Exp Adding:      http://localhost:8001/exp_adding.html")
    print(f"🔮 Predicciones:    http://localhost:8001/pre_flight_predictions.html")
    print(f"📊 Dashboard:       http://localhost:8001/exp_dashboard.html")
    print(f"📚 Documentación:   http://localhost:8001/docs")
    print("="*60)
    print(f"\n📍 URLs disponibles (HTTP - Móvil):")
    print("="*60)
    print(f"📱 Frontend móvil:  http://{local_ip}:8001/")
    print(f"📦 Exp Adding:      http://{local_ip}:8001/exp_adding.html")
    print("="*60)
    print(f"\n⚠️  NOTA: Para la cámara en móvil necesitas HTTPS")
    print(f"   Si necesitas probar la cámara, avísame y configuro HTTPS")
    print("="*60)
    print()
    
    # Usar HTTP por defecto (sin advertencia de seguridad)
    uvicorn.run(app, host="0.0.0.0", port=8001)
    