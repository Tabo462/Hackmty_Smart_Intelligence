import os
import snowflake.connector
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class SnowflakeManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self) -> bool:
        """Establece conexión con Snowflake"""
        try:
            self.connection = snowflake.connector.connect(
                user=os.getenv("SNOWFLAKE_USER"),
                password=os.getenv("SNOWFLAKE_PASSWORD"),
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
                database=os.getenv("SNOWFLAKE_DATABASE"),
                schema=os.getenv("SNOWFLAKE_SCHEMA")
            )
            self.cursor = self.connection.cursor()
            logger.info("✅ Conexión a Snowflake establecida")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando a Snowflake: {e}")
            return False
    
    def disconnect(self):
        """Cierra la conexión con Snowflake"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("🔌 Conexión a Snowflake cerrada")
    
    def check_barcode_exists(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Verifica si un código de barras existe en la base de datos"""
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            query = """
            SELECT ProductID, ProductName, Quantity, Lot, ExpirationDate 
            FROM Products 
            WHERE Barcode = %s
            """
            self.cursor.execute(query, (barcode,))
            result = self.cursor.fetchone()
            
            if result:
                return {
                    "exists": True,
                    "productID": result[0],
                    "productName": result[1],
                    "quantity": result[2],
                    "lot": result[3],
                    "expirationDate": result[4].isoformat() if result[4] else None
                }
            else:
                return {"exists": False}
                
        except Exception as e:
            logger.error(f"❌ Error consultando barcode: {e}")
            return None
    
    def save_product(self, barcode: str, product_id: str, product_name: str, 
                    quantity: int, lot: str, expiration_date: str) -> bool:
        """Guarda o actualiza un producto en la base de datos"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            # Usar MERGE para insertar o actualizar
            query = """
            MERGE INTO Products AS target
            USING (SELECT %s AS Barcode, %s AS ProductID, %s AS ProductName, 
                          %s AS Quantity, %s AS Lot, %s AS ExpirationDate) AS source
            ON target.Barcode = source.Barcode
            WHEN MATCHED THEN
                UPDATE SET ProductID = source.ProductID,
                          ProductName = source.ProductName,
                          Quantity = source.Quantity,
                          Lot = source.Lot,
                          ExpirationDate = source.ExpirationDate
            WHEN NOT MATCHED THEN
                INSERT (Barcode, ProductID, ProductName, Quantity, Lot, ExpirationDate)
                VALUES (source.Barcode, source.ProductID, source.ProductName, 
                       source.Quantity, source.Lot, source.ExpirationDate)
            """
            
            self.cursor.execute(query, (barcode, product_id, product_name, 
                                      quantity, lot, expiration_date))
            self.connection.commit()
            logger.info(f"✅ Producto guardado: {barcode}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando producto: {e}")
            return False
    
    def create_table_if_not_exists(self) -> bool:
        """Crea la tabla Products si no existe"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS Products (
                Barcode STRING PRIMARY KEY,
                ProductID STRING,
                ProductName STRING,
                Quantity INT,
                Lot STRING,
                ExpirationDate DATE
            )
            """
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logger.info("✅ Tabla Products creada/verificada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando tabla: {e}")
            return False

# Instancia global del manager
snowflake_manager = SnowflakeManager()
