#!/bin/bash
# Script to clone and deploy Smart Intelligence on EC2

set -e

echo "🚀 Starting deployment..."

# 1. Clone repository
echo "📥 Cloning repository..."
cd ~
if [ -d "Hackmty_Smart_Intelligence" ]; then
    echo "⚠️  Directory exists, pulling latest..."
    cd Hackmty_Smart_Intelligence
    git pull
else
    echo "📥 Cloning repository..."
    git clone https://github.com/TU_USERNAME/Hackmty_Smart_Intelligence.git
    cd Hackmty_Smart_Intelligence
fi

# 2. Create .env file
echo "⚙️  Setting up .env file..."
if [ ! -f ".env" ]; then
    cp backend/env_example.txt .env
    echo "⚠️  Created .env from template. Please edit it with your API keys:"
    echo "   nano .env"
    echo ""
    echo "Required keys:"
    echo "  - GEMINI_API_KEY"
    echo "  - ELEVENLABS_API_KEY"
    echo "  - SNOWFLAKE credentials"
    read -p "Press Enter after editing .env file..."
else
    echo "✅ .env file already exists"
fi

# 3. Check Docker
echo "🐳 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "❌ Cannot connect to Docker daemon. Please add user to docker group and reconnect."
    exit 1
fi

# 4. Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 5. Build and start the application
echo "🏗️  Building and starting application..."
docker-compose down || true
docker-compose up -d --build

# 6. Show status
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Checking status..."
docker-compose ps

echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop app: docker-compose down"
echo "  Restart: docker-compose restart"
echo ""
echo "🌐 Your app should be running on:"
echo "  - http://$(curl -s ifconfig.me):8001"
echo "  - http://$(curl -s ifconfig.me):8001/docs"
echo ""

