from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import httpx
import snowflake.connector
from dotenv import load_dotenv
from pathlib import Path
import json
import io
import base64
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
SNOW_USER = os.getenv("SNOWFLAKE_USER")
SNOW_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOW_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOW_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOW_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOW_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

# Pydantic models
class BarcodeRequest(BaseModel):
    barcode: str

class ProductData(BaseModel):
    barcode: str
    product_id: str
    lot_number: str
    quantity: int
    expiration_date: str

class DescribeRequest(BaseModel):
    barcode: str
    name: str
    quantity: int
    expiration_date: str

class SpeakRequest(BaseModel):
    text: str

class LinkBarcodeRequest(BaseModel):
    barcode: str
    product_id: str
    name: str

# Snowflake connection function
def get_snowflake_connection():
    try:
        conn = snowflake.connector.connect(
            user=SNOW_USER,
            password=SNOW_PASSWORD,
            account=SNOW_ACCOUNT,
            warehouse=SNOW_WAREHOUSE,
            database=SNOW_DATABASE,
            schema=SNOW_SCHEMA
        )
        return conn
    except Exception as e:
        print(f"Snowflake connection error: {e}")
        return None

# Root endpoint - empty placeholder
@app.get("/")
async def root():
    return {"message": "Frontpage placeholder"}

# Scanner page
@app.get("/scanner", response_class=HTMLResponse)
async def scanner_page(request: Request):
    return templates.TemplateResponse("scanner.html", {"request": request})

# Check barcode endpoint
@app.post("/check_barcode")
async def check_barcode(request: BarcodeRequest):
    conn = get_snowflake_connection()
    if not conn:
        return {"found": False, "error": "Database connection failed"}
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT product_id, name FROM products WHERE barcode = %s",
            (request.barcode,)
        )
        result = cursor.fetchone()
        
        if result:
            return {
                "found": True,
                "product_id": result[0],
                "name": result[1]
            }
        else:
            return {"found": False}
    except Exception as e:
        print(f"Error checking barcode: {e}")
        return {"found": False, "error": "Database query failed"}
    finally:
        if conn:
            conn.close()

# Add product data endpoint
@app.post("/add_product_data")
async def add_product_data(request: ProductData):
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor()
        
        # Insert into batches table
        cursor.execute(
            """INSERT INTO batches (barcode, product_id, lot_number, quantity, expiration_date)
               VALUES (%s, %s, %s, %s, %s)""",
            (request.barcode, request.product_id, request.lot_number, 
             request.quantity, request.expiration_date)
        )
        
        conn.commit()
        return {"success": True, "message": "Product data saved successfully"}
    except Exception as e:
        print(f"Error adding product data: {e}")
        raise HTTPException(status_code=500, detail="Failed to save product data")
    finally:
        if conn:
            conn.close()

# Link barcode endpoint
@app.post("/link_barcode")
async def link_barcode(request: LinkBarcodeRequest):
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor()
        
        # Insert or update product in products table
        cursor.execute(
            """INSERT INTO products (barcode, product_id, name)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE
               product_id = VALUES(product_id),
               name = VALUES(name)""",
            (request.barcode, request.product_id, request.name)
        )
        
        conn.commit()
        return {"success": True, "message": "Barcode linked successfully"}
    except Exception as e:
        print(f"Error linking barcode: {e}")
        raise HTTPException(status_code=500, detail="Failed to link barcode")
    finally:
        if conn:
            conn.close()

# Describe endpoint using Gemini AI
@app.post("/describe")
async def describe_product(request: DescribeRequest):
    try:
        prompt = f"Summarize these product details in a friendly sentence, maximum 10 words, for voice reading: Product: {request.name}, Quantity: {request.quantity}, Expiration: {request.expiration_date}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                description = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return {"description": description}
            else:
                return {"description": f"{request.quantity} pieces of {request.name} expire on {request.expiration_date}"}
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return {"description": f"{request.quantity} pieces of {request.name} expire on {request.expiration_date}"}

# Speak endpoint using ElevenLabs
@app.post("/speak")
async def speak_text(request: SpeakRequest):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB",
                json={
                    "text": request.text,
                    "model_id": "eleven_multilingual_v2"
                },
                headers={
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": ELEVENLABS_API_KEY
                }
            )
            
            if response.status_code == 200:
                return StreamingResponse(
                    io.BytesIO(response.content),
                    media_type="audio/mpeg",
                    headers={"Content-Disposition": "inline; filename=audio.mp3"}
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to generate audio")
    except Exception as e:
        print(f"Error with ElevenLabs API: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate audio")