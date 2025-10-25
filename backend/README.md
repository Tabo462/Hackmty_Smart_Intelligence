# Barcode Scanner System

A complete barcode scanning system with FastAPI backend and mobile-optimized frontend.

## Features

- 📱 Mobile-optimized barcode scanner using QuaggaJS
- ❄️ Snowflake database integration
- 🤖 Gemini AI for product descriptions
- 🔊 ElevenLabs text-to-speech
- ✅ Form validation and error handling
- 🎨 Modern UI with TailwindCSS

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the backend directory with your API keys:

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Snowflake Configuration
SNOWFLAKE_USER=your_snowflake_user
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_ACCOUNT=your_snowflake_account
SNOWFLAKE_WAREHOUSE=your_snowflake_warehouse
SNOWFLAKE_DATABASE=your_snowflake_database
SNOWFLAKE_SCHEMA=your_snowflake_schema
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Create Snowflake Tables

Run the SQL script in `snowflake_tables.sql` in your Snowflake environment:

```sql
-- Products table
CREATE TABLE IF NOT EXISTS products (
  barcode VARCHAR PRIMARY KEY,
  product_id VARCHAR,
  name VARCHAR
);

-- Batches table
CREATE TABLE IF NOT EXISTS batches (
  id INTEGER AUTOINCREMENT PRIMARY KEY,
  barcode VARCHAR,
  product_id VARCHAR,
  lot_number VARCHAR,
  quantity INTEGER,
  expiration_date DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### 4. Run the Application

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the Scanner

Open your browser and navigate to:
- `http://localhost:8000/scanner` - Barcode scanner interface
- `http://localhost:8000/` - Frontpage placeholder

## API Endpoints

- `GET /` - Frontpage placeholder
- `GET /scanner` - Scanner interface
- `POST /check_barcode` - Check if barcode exists in database
- `POST /add_product_data` - Save product data to database
- `POST /describe` - Generate product description using Gemini AI
- `POST /speak` - Convert text to speech using ElevenLabs

## Supported Barcode Types

- EAN-13
- EAN-8
- UPC-A
- UPC-E
- Code 128

## Mobile Optimization

The scanner is optimized for mobile devices with:
- Responsive design
- Touch-friendly interface
- Camera access optimization
- Mobile-specific barcode scanning settings

## Error Handling

The system includes comprehensive error handling for:
- Camera access issues
- Barcode reading failures
- Database connection problems
- API failures (Gemini, ElevenLabs)
- Form validation errors

All errors are communicated via voice using ElevenLabs TTS.
