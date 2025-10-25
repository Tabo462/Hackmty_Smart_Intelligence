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

# Ruta principal - sirve el frontend
@app.get("/index.html")
async def serve_frontend():
    """Servir la página principal del frontend"""
    try:
        frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/index.html")
        return FileResponse(frontend_path)
    except:
        return HTMLResponse("""
        <h1>🚀 Smart Intelligence API</h1>
        <p>Backend funcionando correctamente!</p>
        <p><a href="/docs">Ver documentación de la API</a></p>
        <p><a href="/predictions">Ir a predicciones</a></p>
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

# Endpoint de salud
@app.get("/api/health")
async def health_check():
    """Endpoint de salud para verificar el estado de la API"""
    return {
        "status": "healthy",
        "message": "Backend funcionando correctamente",
        "endpoints": [
            "/api/predict - POST - Predicciones",
            "/api/health - GET - Estado del sistema",
            "/ - GET - Página principal",
            "/predictions - GET - Página de predicciones"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor FastAPI...")
    print("📱 Frontend disponible en: http://localhost:8000")
    print("🔮 Predicciones en: http://localhost:8000/predictions")
    print("📚 Documentación API en: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    