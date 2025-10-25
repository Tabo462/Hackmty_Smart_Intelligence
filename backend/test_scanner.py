#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad del Web Scanner
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv


# Cargar variables de entorno
load_dotenv()

def test_api_endpoints():
    """Prueba los endpoints de la API"""
    base_url = "http://localhost:8000"
    
    print("🧪 Iniciando pruebas de la API...")
    
    # Test 1: Health Check
    print("\n1️⃣ Probando endpoint de salud...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check exitoso: {data}")
        else:
            print(f"❌ Health check falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en health check: {e}")
    
    # Test 2: Check Barcode (producto no existe)
    print("\n2️⃣ Probando verificación de código de barras (producto no existe)...")
    try:
        test_barcode = "1234567890123"
        payload = {"barcode": test_barcode}
        response = requests.post(f"{base_url}/api/check_barcode", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Verificación exitosa: {data}")
            if not data.get("exists") and data.get("audio_base64"):
                print("🎙️ Audio generado correctamente")
        else:
            print(f"❌ Verificación falló: {response.status_code}")
            print(f"Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
    
    # Test 3: Save Product
    print("\n3️⃣ Probando guardado de producto...")
    try:
        product_data = {
            "barcode": "1234567890123",
            "productID": "TEST001",
            "productName": "Producto de Prueba",
            "quantity": 5,
            "lot": "L-001",
            "expirationDate": "2025-12-31"
        }
        response = requests.post(f"{base_url}/api/save_product", json=product_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Guardado exitoso: {data}")
        else:
            print(f"❌ Guardado falló: {response.status_code}")
            print(f"Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error en guardado: {e}")
    
    # Test 4: Check Barcode (producto existe)
    print("\n4️⃣ Probando verificación de código de barras (producto existe)...")
    try:
        test_barcode = "1234567890123"
        payload = {"barcode": test_barcode}
        response = requests.post(f"{base_url}/api/check_barcode", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Verificación exitosa: {data}")
            if data.get("exists"):
                print("📦 Producto encontrado correctamente")
        else:
            print(f"❌ Verificación falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en verificación: {e}")

def test_environment_variables():
    """Verifica que las variables de entorno estén configuradas"""
    print("🔧 Verificando variables de entorno...")
    
    required_vars = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER", 
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
        "SNOWFLAKE_WAREHOUSE",
        "ELEVENLABS_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables faltantes: {missing_vars}")
        print("💡 Asegúrate de crear un archivo .env con todas las variables necesarias")
        return False
    else:
        print("✅ Todas las variables de entorno están configuradas")
        return True

def test_imports():
    """Verifica que todas las dependencias estén instaladas"""
    print("📦 Verificando dependencias...")
    
    required_modules = [
        "fastapi",
        "uvicorn", 
        "snowflake.connector",
        "requests",
        "pydantic",
        "dotenv"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Módulos faltantes: {missing_modules}")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return False
    else:
        print("✅ Todas las dependencias están instaladas")
        return True

def main():
    """Función principal de pruebas"""
    print("🚀 Web Scanner - Script de Pruebas")
    print("=" * 50)
    
    # Verificar dependencias
    if not test_imports():
        sys.exit(1)
    
    # Verificar variables de entorno
    if not test_environment_variables():
        print("\n⚠️ Continuando con pruebas limitadas...")
    
    # Probar endpoints (solo si el servidor está corriendo)
    print("\n" + "=" * 50)
    print("🌐 Probando endpoints de la API...")
    print("💡 Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    
    try:
        test_api_endpoints()
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
        print("💡 Ejecuta: python main.py")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Pruebas completadas")

if __name__ == "__main__":
    main()
