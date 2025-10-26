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

# Global variable for the Snowflake Connection
sf = SnowflakeConnection()

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
    if not sf.connect():
        print("❌ Failed to connect to Snowflake. Please check your credentials.")
    print("🚀 Iniciando servidor FastAPI...")
    print("📱 Frontend disponible en: http://localhost:8001/index.html")
    print("🔮 Predicciones en: http://localhost:8001/predictions")
    print("📚 Documentación API en: http://localhost:8001/docs")
    uvicorn.run(app, host="0.0.0.0", port=8001)
    