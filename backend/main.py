from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import logging
import os
import json

# Importar nuestros managers
from snowflake_manager import snowflake_manager
from elevenlabs_manager import elevenlabs_manager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(title="Web Scanner API", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Modelos Pydantic
class BarcodeRequest(BaseModel):
    barcode: str

class ProductRequest(BaseModel):
    barcode: str
    productID: str
    productName: str
    quantity: int
    lot: str
    expirationDate: str

class BarcodeResponse(BaseModel):
    exists: bool
    productID: Optional[str] = None
    productName: Optional[str] = None
    quantity: Optional[int] = None
    lot: Optional[str] = None
    expirationDate: Optional[str] = None
    audio_base64: Optional[str] = None

class SaveResponse(BaseModel):
    success: bool
    message: str

class PredictRequest(BaseModel):
    origin: str
    flight_type: str
    service_type: str
    passenger_count: int
    product_name: list
    unit_cost: list
# Endpoints
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Página principal - redirige al scanner"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Web Scanner</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h1>🚀 Web Scanner con FastAPI</h1>
        <p>Bienvenido al sistema de escaneo de códigos de barras.</p>
        <a href="/scanner">Ir al Scanner</a>
    </body>
    </html>
    """

@app.get("/scanner", response_class=HTMLResponse)
async def scanner_page():
    """Página del scanner"""
    try:
        with open("static/scanner.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: Archivo scanner.html no encontrado</h1>", status_code=404)

@app.post("/api/check_barcode", response_model=BarcodeResponse)
async def check_barcode(request: BarcodeRequest):
    """
    Verifica si un código de barras existe en la base de datos
    """
    try:
        logger.info(f"🔍 Verificando barcode: {request.barcode}")
        
        # Verificar en Snowflake
        result = snowflake_manager.check_barcode_exists(request.barcode)
        
        if result is None:
            raise HTTPException(status_code=500, detail="Error conectando a la base de datos")
        
        if result["exists"]:
            # Producto existe
            logger.info(f"✅ Producto encontrado: {result['productName']}")
            return BarcodeResponse(
                exists=True,
                productID=result["productID"],
                productName=result["productName"],
                quantity=result["quantity"],
                lot=result["lot"],
                expirationDate=result["expirationDate"]
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
        
        success = snowflake_manager.save_product(
            barcode=request.barcode,
            product_id=request.productID,
            product_name=request.productName,
            quantity=request.quantity,
            lot=request.lot,
            expiration_date=request.expirationDate
        )
        
        if success:
            return SaveResponse(
                success=True,
                message="Producto guardado exitosamente"
            )
        else:
            raise HTTPException(status_code=500, detail="Error guardando el producto")
            
    except Exception as e:
        logger.error(f"❌ Error en save_product: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Endpoint de salud para verificar el estado de la API"""
    return {
        "status": "healthy",
        "snowflake_connected": snowflake_manager.connection is not None,
        "elevenlabs_configured": elevenlabs_manager.api_key is not None
    }

# Evento de inicio
@app.on_event("startup")
async def startup_event():
    """Inicialización al arrancar la aplicación"""
    logger.info("🚀 Iniciando Web Scanner API")
    
    # Conectar a Snowflake
    if snowflake_manager.connect():
        # Crear tabla si no existe
        snowflake_manager.create_table_if_not_exists()
    else:
        logger.warning("⚠️ No se pudo conectar a Snowflake - usando modo offline")

# Evento de cierre
@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar la aplicación"""
    logger.info("🛑 Cerrando Web Scanner API")
    snowflake_manager.disconnect()

@app.post("/api/predict")
async def predict_consumption(data: PredictRequest):
    """
    Endpoint para predecir el consumo utilizando el modelo de Random Forest
    """
    try:
        from aidata.Random_Forest_Regression import AirlineConsumptionPredictor

        # Cargar el modelo entrenado
        predictor = AirlineConsumptionPredictor.load_trained_model("airline_consumption_model")
        if predictor is None:
            raise HTTPException(status_code=500, detail="Modelo no cargado. Asegúrese de entrenar y guardar el modelo primero.")

        # Realizar la predicción
        prediction = predictor.predict_consumption(
            origin=data.origin,
            flight_type=data.flight_type,
            service_type=data.service_type,
            passenger_count=data.passenger_count,
            product_name=data.product_name[0],
            unit_cost=data.unit_cost[0],
            has_issues=0
        )

        print(f"✅ Predicción exitosa! Consumo estimado: {prediction:.2f} unidades")

        return {"predicted_consumption": prediction}

    except Exception as e:
        logger.error(f"❌ Error en predict_consumption: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)