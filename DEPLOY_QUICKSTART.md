# 🚀 Quick Start: Deploy en EC2

## ⚡ Deployment Rápido (5 minutos)

### 1️⃣ Preparar EC2

```bash
# Conectar a tu instancia EC2
ssh -i tu-key.pem ec2-user@TU_IP_EC2
```

### 2️⃣ Instalar Docker

```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3️⃣ Clonar Proyecto

```bash
cd ~
git clone https://github.com/TU_REPO/Hackmty_Smart_Intelligence.git
cd Hackmty_Smart_Intelligence
```

### 4️⃣ Configurar .env

```bash
cp backend/env_example.txt .env
nano .env  # Edita con tus credenciales
```

### 5️⃣ Instalar Nginx + SSL

```bash
sudo yum install -y nginx certbot python3-certbot-nginx
```

### 6️⃣ Configurar Nginx

```bash
sudo nano /etc/nginx/conf.d/smart-intelligence.conf
```

Pega esto (reemplaza `tu-dominio.com`):

```nginx
upstream smart_intelligence {
    server localhost:8001;
}

server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://smart_intelligence;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 7️⃣ Activar SSL

```bash
sudo certbot --nginx -d tu-dominio.com --agree-tos --email tu@email.com
```

### 8️⃣ Iniciar Aplicación

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### 9️⃣ Configurar Dominio

En tu DNS (Route53, Cloudflare, etc.):
```
A Record: tu-dominio.com → IP_DE_TU_EC2
```

## ✅ ¡Listo!

Tu app está en: **https://tu-dominio.com**

---

## 📋 Comandos Útiles

```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Actualizar
git pull && docker-compose up -d --build

# Verificar
curl https://tu-dominio.com/docs
```

---

## 🔧 Security Group (AWS)

Abre estos puertos en tu EC2 Security Group:
- **22** (SSH)
- **80** (HTTP)
- **443** (HTTPS)

---

## 📚 Documentación Completa

- **ec2-setup.md** - Guía completa detallada
- **deploy-ec2.sh** - Script automatizado

## 🆘 Troubleshooting

### App no responde
```bash
docker-compose logs
sudo systemctl status nginx
```

### SSL no funciona
```bash
sudo certbot renew --dry-run
sudo systemctl restart nginx
```

### Dominio no resuelve
```bash
nslookup tu-dominio.com
# Espera 5-30 minutos para propagación DNS
```

