# 🛫 Smart Intelligence - Airline Catering Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.120.0-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Snowflake](https://img.shields.io/badge/Snowflake-Enabled-29B5E8.svg)](https://www.snowflake.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive AI-powered platform for airline catering operations, featuring consumption prediction, inventory management, expiration date tracking, and intelligent analytics.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

**Smart Intelligence** is an enterprise-grade solution designed for airline catering companies to optimize inventory management, predict consumption patterns, and streamline operations. The platform combines machine learning, real-time data processing, and AI-powered insights to help airlines reduce waste, minimize costs, and improve operational efficiency.

### Key Capabilities

- 🤖 **AI-Powered Consumption Prediction** - Machine learning models predict product demand based on flight characteristics
- 📊 **Real-Time Inventory Management** - Track products, batches, and expiration dates in real-time
- 🎯 **Expiration Date Management** - Automated alerts and dashboards for products nearing expiration
- 📱 **Mobile Barcode Scanner** - Scan and manage products using mobile camera with voice feedback
- 🤖 **AI Assistant Chatbot** - Get insights and answers using Google Gemini AI
- 🔊 **Voice Feedback** - Text-to-speech notifications using ElevenLabs
- 📈 **Analytics Dashboard** - Comprehensive analytics and visualization tools

## ✨ Features

### 🔮 Consumption Prediction System

Powered by a **Random Forest Regression** model that predicts consumption based on:
- Flight origin and type (short-haul, medium-haul, long-haul)
- Service type (Economy, Business, First Class)
- Passenger count
- Product characteristics
- Historical consumption patterns

### 📦 Inventory Management

- Real-time product tracking with barcode scanning
- Batch and lot management
- Quantity tracking and updates
- Expiration date monitoring
- Automatic alerts for products nearing expiration

### 🤖 AI Integration

- **Google Gemini AI**: Intelligent chatbot for answering questions about operations
- **ElevenLabs TTS**: Natural voice feedback for mobile operations
- **Snowflake Integration**: Enterprise-grade data warehousing

### 📱 Mobile Optimized

- Responsive design for mobile devices
- Camera-based barcode scanning
- Touch-friendly interface
- Offline-capable functionality
- Voice feedback for hands-free operation

### 📊 Dashboard & Analytics

- Product inventory overview
- Expiration tracking
- Consumption analytics
- Demand forecasting
- Cost optimization insights

## 🛠️ Technology Stack

### Backend

- **Framework**: FastAPI 0.120.0
- **Language**: Python 3.11+
- **Database**: Snowflake (cloud data warehouse)
- **ML Framework**: Scikit-learn 1.7.2
- **Data Processing**: Pandas 2.3.2, NumPy 2.3.3

### AI/ML Services

- **Google Gemini AI**: Natural language processing and chatbot
- **ElevenLabs**: Text-to-speech synthesis
- **Random Forest**: Consumption prediction model

### Frontend

- **HTML5/CSS3**: Modern web interfaces
- **Bootstrap 5.3.3**: Responsive UI framework
- **JavaScript**: Interactive features
- **Chart.js**: Data visualization
- **QuaggaJS**: Barcode scanning

### DevOps & Deployment

- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **AWS EC2**: Cloud deployment
- **Nginx**: Reverse proxy and load balancing

### Data Storage

- **Snowflake**: Enterprise data warehouse
- **Files**: Model files, configuration, datasets

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                           │
├─────────────────────────────────────────────────────────────┤
│  index.html  │  pre_flight_predictions.html  │  scanner.html  │
│  exp_dashboard.html  │  exp_adding.html                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│                   FastAPI Backend                            │
├─────────────────────────────────────────────────────────────┤
│  RESTful API  │  WebSocket  │  Static File Server           │
│  CORS Support │  Authentication  │  Error Handling           │
└───────────┬────────────┬──────────────┬────────────────────┘
            │            │              │
    ┌───────▼──────┐ ┌───▼──────────┐ ┌─▼───────────────────┐
    │  Snowflake   │ │  Gemini AI   │ │  ElevenLabs         │
    │  Database    │ │  Chatbot     │ │  Text-to-Speech     │
    └──────────────┘ └──────────────┘ └─────────────────────┘
```

### Directory Structure

```
Hackmty_Smart_Intelligence/
├── backend/                      # FastAPI backend application
│   ├── main.py                  # Main FastAPI application
│   ├── simple_main.py           # Alternative simplified entry point
│   ├── snowflake_manager.py     # Snowflake database manager
│   ├── elevenlabs_manager.py    # ElevenLabs TTS integration
│   ├── SnowflakeFinal.py        # Enhanced Snowflake operations
│   ├── requirements.txt         # Python dependencies
│   ├── aidata/                  # Machine learning data and models
│   │   ├── Random_Forest_Regression.py
│   │   ├── airline_consumption_model/
│   │   └── *(HackMTY2025)_ConsumptionPrediction_Dataset_v1.csv
│   ├── snowflake/               # Snowflake integration modules
│   │   ├── ia_gemini.py         # Gemini AI integration
│   │   ├── ia_audio.py          # Audio processing
│   │   └── ia_snowflake.py      # Snowflake operations
│   ├── static/                  # Static files for scanner
│   │   └── scanner.html         # Barcode scanner interface
│   └── HackMTY2025_ChallengeDimensions/  # Challenge datasets
├── frontend/                    # Frontend applications
│   ├── index.html              # Main landing page
│   ├── pre_flight_predictions.html  # Prediction interface
│   ├── exp_adding.html        # Add expiration data
│   ├── exp_dashboard.html     # Expiration dashboard
│   └── media_files/           # Static media files
│       ├── chat.js            # Chat functionality
│       ├── hero_video.mp4     # Background video
│       └── *.jpg              # Images
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                   # Docker image definition
├── nginx-smart-intelligence.conf  # Nginx configuration
└── README.md                   # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (optional, for containerized deployment)
- Snowflake account with active warehouse
- Google Gemini API key
- ElevenLabs API key
- Git

### System Requirements

- **OS**: Linux, macOS, or Windows (with WSL2 recommended)
- **RAM**: Minimum 4GB, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for API services

## 📦 Installation

### Option 1: Local Development (Recommended)

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/Hackmty_Smart_Intelligence.git
cd Hackmty_Smart_Intelligence
```

2. **Set up Python environment**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. **Configure environment variables**

Create a `.env` file in the project root:

```bash
cp backend/env_example.txt .env
```

Edit `.env` with your credentials:

```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account.us-east-1
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=PUBLIC

# API Keys
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB
```

4. **Initialize Snowflake database**

```bash
cd backend
python SnowflakeFinal.py
```

This will create the necessary tables and load sample data.

### Option 2: Docker Deployment (Quick Start)

1. **Build and run with Docker Compose**

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:8001
- API Documentation: http://localhost:8001/docs
- Barcode Scanner: http://localhost:8001/static/scanner.html

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SNOWFLAKE_ACCOUNT` | Snowflake account identifier | Yes |
| `SNOWFLAKE_USER` | Snowflake username | Yes |
| `SNOWFLAKE_PASSWORD` | Snowflake password | Yes |
| `SNOWFLAKE_WAREHOUSE` | Snowflake warehouse name | Yes |
| `SNOWFLAKE_DATABASE` | Snowflake database name | Yes |
| `SNOWFLAKE_SCHEMA` | Snowflake schema name | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | Yes |
| `ELEVENLABS_VOICE_ID` | ElevenLabs voice ID | Optional |

### Snowflake Table Schema

The system creates the following table in Snowflake:

```sql
CREATE TABLE PRODUCT_DATA (
    Barcode VARCHAR(13) PRIMARY KEY,
    ProductID VARCHAR(6),
    ProductName VARCHAR(40),
    LotNumber VARCHAR(7),
    Quantity INTEGER,
    Exp_Date DATE
);
```

## 💻 Usage

### Running the Application

1. **Start the backend server**

```bash
cd backend
python simple_main.py
```

Or using uvicorn:

```bash
uvicorn simple_main:app --host 0.0.0.0 --port 8001
```

2. **Access the application**

- **Main Dashboard**: http://localhost:8001
- **Pre-Flight Predictions**: http://localhost:8001/pre_flight_predictions.html
- **Expiration Dashboard**: http://localhost:8001/exp_dashboard.html
- **Add Expiration Data**: http://localhost:8001/exp_adding.html
- **Barcode Scanner**: http://localhost:8001/static/scanner.html
- **API Documentation**: http://localhost:8001/docs

### Using the Barcode Scanner

1. Navigate to the scanner interface
2. Grant camera permissions when prompted
3. Point your camera at a barcode
4. The system will:
   - Check if the product exists in the database
   - Provide voice feedback via ElevenLabs TTS
   - Display product information
   - Allow you to add new products if not found

### Making Predictions

1. Navigate to the predictions page
2. Enter flight details:
   - Flight ID
   - Origin (e.g., DOH, JFK)
   - Flight Type (short-haul, medium-haul, long-haul)
   - Service Type (Economy, Business, First)
   - Passenger Count
   - Products with quantities and costs
3. Click "Generate Prediction"
4. View predicted consumption, costs, and per-passenger metrics

## 📚 API Documentation

### Base URL

```
http://localhost:8001
```

### Endpoints

#### Health Check

```http
GET /api/health
```

Returns system health status.

**Response:**
```json
{
  "status": "healthy",
  "message": "Backend funcionando correctamente",
  "endpoints": [...]
}
```

#### Consumption Prediction

```http
POST /api/predict
```

Predicts consumption based on flight characteristics.

**Request Body:**
```json
{
  "flight_id": "QF123",
  "origin": "DOH",
  "flight_type": "medium-haul",
  "service_type": "Economy",
  "passenger_count": 250,
  "product_name": ["Sparkling Water 330ml", "Coffee 200ml"],
  "unit_cost": [0.45, 0.75]
}
```

**Response:**
```json
{
  "flight_info": {
    "flight_id": "QF123",
    "origin": "DOH",
    "flight_type": "medium-haul",
    "service_type": "Economy",
    "passenger_count": 250
  },
  "products": [
    {
      "product_name": "Sparkling Water 330ml",
      "unit_cost": 0.45,
      "predicted_units": 120,
      "total_cost": 54.00
    }
  ],
  "totals": {
    "total_units": 120,
    "total_cost": 54.00,
    "units_per_passenger": 0.48,
    "cost_per_passenger": 0.22
  }
}
```

#### Barcode Check

```http
POST /api/check_barcode
```

Checks if a barcode exists in the database.

**Request Body:**
```json
{
  "barcode": "7501040093135"
}
```

**Response:**
```json
{
  "exists": true,
  "productID": "000001",
  "productName": "Beverage A",
  "quantity": 100,
  "lot": "L00123",
  "expirationDate": "2025-11-06"
}
```

#### Save Product

```http
POST /api/save_product
```

Saves or updates product information.

**Request Body:**
```json
{
  "barcode": "7501040093135",
  "productID": "000001",
  "productName": "Beverage A",
  "quantity": 100,
  "lot": "L00123",
  "expirationDate": "2025-11-06"
}
```

#### Chat with AI

```http
POST /api/chat
```

Chat with the AI assistant powered by Google Gemini.

**Request Body:**
```json
{
  "message": "What products are expiring soon?"
}
```

**Response:**
```json
{
  "reply": "Based on the data, there are 5 products expiring within the next 30 days..."
}
```

#### Dashboard Metrics

```http
GET /api/dashboard/metrics
```

Retrieves dashboard summary metrics.

**Response:**
```json
{
  "total_products": 150,
  "expiring_products": 5,
  "expired_products": 2,
  "total_quantity": 12500,
  "healthy_products": 143
}
```

#### Dashboard Products

```http
GET /api/dashboard/products
```

Retrieves full product list with expiration status.

## 🐳 Docker Deployment

### Building the Image

```bash
docker build -t smart-intelligence:latest .
```

### Running with Docker Compose

```bash
docker-compose up -d
```

### Docker Compose Configuration

The `docker-compose.yml` file includes:
- Automatic health checks
- Port mapping (8001)
- Volume mounting for data persistence
- Environment variable configuration
- Auto-restart policy

### Multi-Architecture Support

The project includes scripts for multi-architecture builds:

```bash
# Linux/macOS
./docker-build-multi-arch.sh

# Windows PowerShell
./docker-build-multi-arch.ps1
```

## ☁️ Cloud Deployment

### AWS EC2 Deployment

See detailed deployment guides:
- [AWS Launch Instance](AWS_LAUNCH_INSTANCE.md)
- [Deploy Quickstart](DEPLOY_QUICKSTART.md)
- [EC2 Setup](ec2-setup.md)
- [Connecting to EC2](CONECTAR_EC2.md)

### Quick Cloud Deployment

```bash
# Clone on server
git clone https://github.com/yourusername/Hackmty_Smart_Intelligence.git
cd Hackmty_Smart_Intelligence

# Configure environment
nano .env  # Edit with your credentials

# Run with Docker
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

## 🔧 Development

### Project Structure

```
backend/
├── main.py                    # Main FastAPI application
├── simple_main.py             # Simplified entry point
├── snowflake_manager.py       # Database manager
├── elevenlabs_manager.py      # TTS integration
├── SnowflakeFinal.py          # Enhanced DB operations
├── requirements.txt           # Dependencies
├── aidata/                    # ML models and data
├── snowflake/                 # Snowflake modules
└── static/                    # Static files

frontend/
├── index.html                 # Landing page
├── pre_flight_predictions.html
├── exp_dashboard.html
├── exp_adding.html
└── media_files/              # Assets
```

### Training the ML Model

To retrain the consumption prediction model:

```bash
cd backend/aidata
python Random_Forest_Regression.py
```

This will:
1. Load the training dataset
2. Preprocess the data
3. Train a Random Forest model
4. Evaluate performance
5. Save the model to `airline_consumption_model/`

### Adding New Features

1. **Backend**: Add endpoints in `simple_main.py`
2. **Frontend**: Create new HTML pages in `frontend/`
3. **Database**: Extend `SnowflakeFinal.py` for new tables
4. **Models**: Update ML models in `aidata/`

## 🧪 Testing

### API Testing

```bash
# Using curl
curl http://localhost:8001/api/health

# Using Python requests
python backend/test_scanner.py
```

### Manual Testing Checklist

- [ ] Health check endpoint responds
- [ ] Snowflake connection established
- [ ] Barcode scanning works
- [ ] Predictions generate correctly
- [ ] Chatbot responds appropriately
- [ ] Voice synthesis works
- [ ] Dashboard displays data

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Use descriptive variable names
- Add docstrings to functions
- Include error handling
- Write meaningful commit messages

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **FastAPI** for the excellent web framework
- **Snowflake** for the cloud data platform
- **Google Gemini** for AI capabilities
- **ElevenLabs** for voice synthesis
- **HackMTY 2025** for the challenge and datasets

## 📞 Support

For issues, questions, or contributions:
- **Issues**: [GitHub Issues](https://github.com/yourusername/Hackmty_Smart_Intelligence/issues)
- **Email**: support@example.com
- **Documentation**: See individual README files in subdirectories

## 🎯 Roadmap

- [ ] Real-time collaboration features
- [ ] Advanced analytics and reporting
- [ ] Mobile app (iOS/Android)
- [ ] Integration with airline systems
- [ ] Machine learning model improvements
- [ ] Additional language support
- [ ] Automated alerting system
- [ ] Export/import functionality

---

**Made with ❤️ for HackMTY 2025**
