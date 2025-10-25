# 🚀 Web Scanner con FastAPI, Snowflake y ElevenLabs

Una aplicación web completa para escanear códigos de barras EAN-13 con integración a Snowflake y generación de audio usando ElevenLabs.

## ✨ Características

- 📱 **Escáner de códigos de barras en tiempo real** usando QuaggaJS
- ❄️ **Integración con Snowflake** para almacenamiento de productos
- 🎙️ **Generación de audio** con ElevenLabs para notificaciones
- 🌐 **Interfaz web moderna** y responsiva
- 🔄 **API REST completa** con FastAPI
- 📊 **Formulario dinámico** para productos nuevos y existentes

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI** - Framework web moderno y rápido
- **Snowflake** - Base de datos en la nube
- **ElevenLabs** - API de text-to-speech
- **Python 3.8+** - Lenguaje de programación

### Frontend
- **HTML5 + CSS3 + JavaScript** - Sin frameworks adicionales
- **QuaggaJS** - Biblioteca para escaneo de códigos de barras
- **Diseño responsivo** - Optimizado para móviles y desktop

## 📋 Requisitos Previos

1. **Python 3.8 o superior**
2. **Cuenta de Snowflake** con acceso a una base de datos
3. **API Key de ElevenLabs** (cuenta gratuita disponible)
4. **Navegador web moderno** con soporte para cámara

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd Hackmty_Smart_Intelligence/backend
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto con:

```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=tu_cuenta_snowflake
SNOWFLAKE_USER=tu_usuario
SNOWFLAKE_PASSWORD=tu_contraseña
SNOWFLAKE_DATABASE=tu_base_de_datos
SNOWFLAKE_SCHEMA=tu_esquema
SNOWFLAKE_WAREHOUSE=tu_warehouse

# ElevenLabs Configuration
ELEVENLABS_API_KEY=tu_api_key_elevenlabs
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB
```

### 5. Crear tabla en Snowflake

Ejecutar este SQL en tu consola de Snowflake:

```sql
CREATE TABLE IF NOT EXISTS Products (
    Barcode STRING PRIMARY KEY,
    ProductID STRING,
    ProductName STRING,
    Quantity INT,
    Lot STRING,
    ExpirationDate DATE
);
```

### 6. Ejecutar la aplicación

```bash
python main.py
```

La aplicación estará disponible en: `http://localhost:8000`

## 📱 Uso de la Aplicación

### 1. Acceder al Scanner
- Navegar a `http://localhost:8000/scanner`
- Permitir acceso a la cámara cuando se solicite

### 2. Escanear Códigos de Barras
- Hacer clic en "▶️ Iniciar Escáner"
- Apuntar la cámara al código de barras EAN-13
- El sistema detectará automáticamente el código

### 3. Gestión de Productos

#### Si el producto existe:
- Se llenarán automáticamente los campos del formulario
- Modificar los datos necesarios
- Hacer clic en "💾 Guardar Producto"

#### Si el producto es nuevo:
- Se reproducirá un audio indicando que no está en la base de datos
- Llenar todos los campos del formulario:
  - **ID del Producto**: Identificador único
  - **Nombre del Producto**: Nombre descriptivo
  - **Cantidad**: Número de unidades
  - **Lote**: Código del lote
  - **Fecha de Vencimiento**: Fecha límite de consumo
- Hacer clic en "💾 Guardar Producto"

## 🔌 API Endpoints

### `POST /api/check_barcode`
Verifica si un código de barras existe en la base de datos.

**Request:**
```json
{
  "barcode": "1234567890123"
}
```

**Response (producto existe):**
```json
{
  "exists": true,
  "productID": "A123",
  "productName": "Cereal",
  "quantity": 10,
  "lot": "L-009",
  "expirationDate": "2025-12-10"
}
```

**Response (producto no existe):**
```json
{
  "exists": false,
  "audio_base64": "base64_encoded_audio_data"
}
```

### `POST /api/save_product`
Guarda o actualiza un producto en la base de datos.

**Request:**
```json
{
  "barcode": "1234567890123",
  "productID": "A123",
  "productName": "Cereal",
  "quantity": 10,
  "lot": "L-009",
  "expirationDate": "2025-12-10"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Producto guardado exitosamente"
}
```

### `GET /api/health`
Verifica el estado de la API y las conexiones.

**Response:**
```json
{
  "status": "healthy",
  "snowflake_connected": true,
  "elevenlabs_configured": true
}
```

## 🎯 Códigos de Barras Soportados

- **EAN-13** (European Article Number)
- **EAN-8** (European Article Number)
- **UPC-A** (Universal Product Code)
- **UPC-E** (Universal Product Code)
- **Code 128** (Código de barras alfanumérico)

## 🔧 Solución de Problemas

### Error de conexión a Snowflake
- Verificar las credenciales en el archivo `.env`
- Asegurar que el warehouse esté activo
- Verificar permisos de acceso a la base de datos

### Error de acceso a la cámara
- Permitir acceso a la cámara en el navegador
- Usar HTTPS en producción (requerido para acceso a cámara)
- Verificar que la cámara no esté siendo usada por otra aplicación

### Error de ElevenLabs
- Verificar que la API key sea válida
- Comprobar el saldo de caracteres en ElevenLabs
- Verificar la conectividad a internet

## 📁 Estructura del Proyecto

```
backend/
├── main.py                 # Aplicación principal FastAPI
├── snowflake_manager.py    # Gestión de conexión a Snowflake
├── elevenlabs_manager.py   # Gestión de API de ElevenLabs
├── requirements.txt        # Dependencias de Python
├── static/
│   └── scanner.html       # Interfaz web del escáner
└── .env                   # Variables de entorno (crear manualmente)
```

## 🤝 Contribuciones

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisar la sección de solución de problemas
2. Verificar los logs de la aplicación
3. Crear un issue en el repositorio

---

**¡Disfruta escaneando códigos de barras! 🎉**
