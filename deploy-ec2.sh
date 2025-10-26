#!/bin/bash
# Script de deployment para EC2
# Uso: bash deploy-ec2.sh

set -e

echo "🚀 Iniciando deployment en EC2..."

# Variables
DOMAIN="${DOMAIN:-tu-dominio.com}"
EMAIL="${EMAIL:-tu-email@ejemplo.com}"

# 1. Instalar Docker y Docker Compose
echo "📦 Instalando Docker..."
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 2. Clonar o copiar el proyecto
echo "📥 Configurando proyecto..."
cd ~
if [ ! -d "Hackmty_Smart_Intelligence" ]; then
    echo "Por favor, clona el repositorio o sube los archivos"
    echo "git clone https://github.com/TU_REPO/Hackmty_Smart_Intelligence.git"
    exit 1
fi

cd Hackmty_Smart_Intelligence

# 3. Configurar .env
if [ ! -f ".env" ]; then
    echo "⚠️  Creando archivo .env..."
    cp backend/env_example.txt .env
    echo "Por favor, configura el archivo .env con tus credenciales"
fi

# 4. Instalar Nginx
echo "🌐 Instalando Nginx..."
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# 5. Instalar Certbot para SSL
echo "🔒 Instalando Certbot..."
sudo amazon-linux-extras install -y epel
sudo yum install -y certbot python3-certbot-nginx

# 6. Configurar Nginx
echo "⚙️  Configurando Nginx..."
sudo tee /etc/nginx/conf.d/smart-intelligence.conf > /dev/null <<EOF
upstream smart_intelligence {
    server localhost:8001;
}

server {
    listen 80;
    server_name ${DOMAIN};

    client_max_body_size 100M;

    location / {
        proxy_pass http://smart_intelligence;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://smart_intelligence;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }
}
EOF

# 7. Configurar SSL
echo "🔐 Configurando SSL..."
sudo certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos --email ${EMAIL}

# 8. Iniciar aplicación con Docker Compose
echo "🐳 Iniciando aplicación..."
docker-compose down || true
docker-compose up -d --build

# 9. Configurar reinicio automático
echo "⚙️  Configurando reinicio automático..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# 10. Firewall
echo "🔥 Configurando firewall..."
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

echo ""
echo "✅ Deployment completado!"
echo "🌐 Tu aplicación está en: https://${DOMAIN}"
echo "📚 API docs: https://${DOMAIN}/docs"
echo ""
echo "Para ver logs: docker-compose logs -f"
echo "Para reiniciar: docker-compose restart"

