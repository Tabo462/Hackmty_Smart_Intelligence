# 🚀 Guía de Deployment en EC2

## 📋 Prerequisitos

1. **Instancia EC2** (Ubuntu 22.04 o Amazon Linux 2)
2. **Dominio** apuntando a la IP de tu EC2
3. **Security Group** con puertos 80, 443 abiertos

## 🔧 Pasos de Deployment

### 1. Conectar a tu EC2

```bash
ssh -i tu-key.pem ec2-user@TU_IP_EC2
```

### 2. Preparar el servidor

#### Opción A: Usar el script automatizado
```bash
cd ~
git clone https://github.com/TU_REPO/Hackmty_Smart_Intelligence.git
cd Hackmty_Smart_Intelligence
chmod +x deploy-ec2.sh
sudo bash deploy-ec2.sh
```

#### Opción B: Manual (paso a paso)

##### Instalar Docker
```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
```

##### Instalar Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

##### Configurar el proyecto
```bash
cd ~
git clone https://github.com/TU_REPO/Hackmty_Smart_Intelligence.git
cd Hackmty_Smart_Intelligence
cp backend/env_example.txt .env
nano .env  # Configura tus API keys
```

### 3. Instalar Nginx

```bash
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 4. Configurar Nginx como Reverse Proxy

Crea el archivo `/etc/nginx/conf.d/smart-intelligence.conf`:

```nginx
upstream smart_intelligence {
    server localhost:8001;
}

server {
    listen 80;
    server_name tu-dominio.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://smart_intelligence;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://smart_intelligence;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 5. Configurar SSL con Let's Encrypt

```bash
sudo amazon-linux-extras install -y epel
sudo yum install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com --non-interactive --agree-tos --email tu-email@ejemplo.com
```

### 6. Iniciar la aplicación

```bash
cd ~/Hackmty_Smart_Intelligence
docker-compose up -d --build
```

### 7. Configurar reinicio automático

```bash
sudo crontab -e
# Agregar:
@reboot cd ~/Hackmty_Smart_Intelligence && docker-compose up -d
```

### 8. Configurar firewall

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 📝 Configurar Dominio

### En tu proveedor de dominios (Cloudflare, Route53, etc.)

1. **A Record**: apunta tu dominio a la IP de EC2
   ```
   tu-dominio.com    A    1.2.3.4
   www.tu-dominio.com A    1.2.3.4
   ```

2. **Espera propagación DNS**: 5-30 minutos

3. **Verifica**: `nslookup tu-dominio.com`

## ✅ Verificación

```bash
# Ver logs de la aplicación
docker-compose logs -f

# Verificar nginx
sudo nginx -t
sudo systemctl status nginx

# Ver puertos abiertos
sudo netstat -tuln | grep -E ':80|:443|:8001'

# Verificar SSL
curl -I https://tu-dominio.com
```

## 🔄 Comandos Útiles

### Actualizar la aplicación
```bash
cd ~/Hackmty_Smart_Intelligence
git pull
docker-compose down
docker-compose up -d --build
```

### Ver logs
```bash
docker-compose logs -f
sudo tail -f /var/log/nginx/error.log
```

### Reiniciar servicios
```bash
docker-compose restart
sudo systemctl restart nginx
```

### Backup
```bash
# Backup de datos
docker run --rm -v hackmty_smart_intelligence_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/backup.tar.gz /data
```

## 🔒 Security Best Practices

1. **Firewall EC2**: Solo permitir 22, 80, 443
2. **Usar EFS para persistencia** si es necesario
3. **Backup automático** con cron
4. **Logs centralizados** con CloudWatch
5. **HTTPS forzado** en Nginx

### Configurar HTTPS forzado en Nginx

```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;
    
    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;
    
    # ... resto de la configuración
}
```

## 🚨 Troubleshooting

### La aplicación no inicia
```bash
docker-compose logs
docker ps -a
```

### Nginx no redirige
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### SSL no funciona
```bash
sudo certbot renew
sudo systemctl restart nginx
```

### Dominio no resuelve
```bash
nslookup tu-dominio.com
dig tu-dominio.com
```

## 📊 Monitoreo

### Ver recursos usados
```bash
docker stats
htop
```

### Configurar CloudWatch (opcional)
```bash
aws configure
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 -c ssm:/CloudWatch -s
```

## 🎉 ¡Listo!

Tu aplicación está desplegada en:
- **URL**: https://tu-dominio.com
- **Dashboard**: https://tu-dominio.com/exp_dashboard.html
- **API Docs**: https://tu-dominio.com/docs

