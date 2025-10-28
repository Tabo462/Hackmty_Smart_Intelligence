# 🚀 Comandos Útiles para Gestionar tu EC2

## 📡 Conectarse a EC2

### Desde PowerShell (si SSH funciona desde casa):
```powershell
ssh -i "C:\Users\guill\OneDrive\Escritorio\smart-intelligence-key.pem" ec2-user@13.218.229.125
```

### Desde AWS Console (si SSH está bloqueado):
1. AWS Console → EC2 → Instances
2. Selecciona tu instancia
3. Click **"Connect"**
4. Pestaña **"EC2 Instance Connect"**
5. Click **"Connect"**

---

## 🐳 Docker Compose - Gestión de la Aplicación

### Ver estado de contenedores
```bash
sudo docker-compose ps
```

### Ver logs en tiempo real
```bash
sudo docker-compose logs -f
```
*Presiona Ctrl + C para salir (el contenedor sigue corriendo)*

### Ver logs de las últimas 100 líneas
```bash
sudo docker-compose logs --tail=100
```

### Reiniciar la aplicación
```bash
sudo docker-compose restart
```

### Detener la aplicación
```bash
sudo docker-compose down
```

### Iniciar la aplicación
```bash
sudo docker-compose up -d
```

### Reconstruir y reiniciar (después de cambios)
```bash
sudo docker-compose down
sudo docker-compose -f docker-compose.prod.yml up -d --build
```

### Ver uso de recursos de contenedores
```bash
sudo docker stats
```

### Entrar al contenedor (para debugging)
```bash
sudo docker exec -it smart-intelligence-api bash
```

---

## 🔄 Actualizar la Aplicación desde GitHub

```bash
# 1. Ir al directorio del proyecto
cd ~/Hackmty_Smart_Intelligence

# 2. Descargar últimos cambios
git pull

# 3. Reconstruir y reiniciar
sudo docker-compose down
sudo docker-compose -f docker-compose.prod.yml up -d --build

# 4. Ver logs para verificar
sudo docker-compose logs -f
```

---

## 🌐 Nginx - Servidor Web

### Ver estado de Nginx
```bash
sudo systemctl status nginx
```
*Presiona 'q' para salir*

### Reiniciar Nginx
```bash
sudo systemctl restart nginx
```

### Detener Nginx
```bash
sudo systemctl stop nginx
```

### Iniciar Nginx
```bash
sudo systemctl start nginx
```

### Probar configuración de Nginx (antes de reiniciar)
```bash
sudo nginx -t
```

### Ver logs de acceso de Nginx
```bash
sudo tail -f /var/log/nginx/access.log
```

### Ver logs de errores de Nginx
```bash
sudo tail -f /var/log/nginx/error.log
```

### Editar configuración de Nginx
```bash
sudo nano /etc/nginx/conf.d/smart-intelligence.conf
```

---

## 🔧 Variables de Entorno

### Editar archivo .env
```bash
cd ~/Hackmty_Smart_Intelligence
nano .env
```

### Ver contenido del .env (sin editar)
```bash
cat .env
```

**Nota**: Después de cambiar el .env, debes reconstruir:
```bash
sudo docker-compose down
sudo docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 📊 Monitoreo del Sistema

### Ver uso de disco
```bash
df -h
```

### Ver uso de memoria
```bash
free -h
```

### Ver procesos corriendo
```bash
top
```
*Presiona 'q' para salir*

### Ver uso de CPU y memoria por Docker
```bash
sudo docker stats
```

---

## 🔍 Debugging

### Ver todos los logs del contenedor
```bash
sudo docker-compose logs
```

### Ver logs de un servicio específico
```bash
sudo docker-compose logs smart-intelligence-api
```

### Probar conectividad interna
```bash
curl http://localhost:8001/api/health
curl http://localhost:80/api/health
```

### Ver variables de entorno del contenedor
```bash
sudo docker exec smart-intelligence-api env
```

### Revisar configuración de Docker Compose
```bash
cat docker-compose.prod.yml
```

---

## 🔐 Seguridad

### Ver reglas del firewall
```bash
sudo firewall-cmd --list-all
```

### Ver puertos abiertos
```bash
sudo netstat -tuln | grep -E ':80|:443|:8001'
```

---

## 💾 Backup

### Crear backup de datos
```bash
cd ~
tar -czf backup-$(date +%Y%m%d).tar.gz Hackmty_Smart_Intelligence/
```

### Descargar backup a tu PC (desde PowerShell local)
```powershell
scp -i "C:\Users\guill\OneDrive\Escritorio\smart-intelligence-key.pem" ec2-user@13.218.229.125:~/backup-*.tar.gz C:\Users\guill\Downloads\
```

---

## 🆘 Solución de Problemas Comunes

### Aplicación no responde
```bash
# 1. Ver logs
sudo docker-compose logs -f

# 2. Verificar contenedor está corriendo
sudo docker-compose ps

# 3. Reiniciar
sudo docker-compose restart
```

### Puerto 8001 ocupado
```bash
# Ver qué proceso usa el puerto
sudo lsof -i :8001

# Matar proceso (reemplaza PID)
sudo kill -9 PID
```

### Nginx da error 502 Bad Gateway
```bash
# 1. Verificar app está corriendo
sudo docker-compose ps

# 2. Probar conexión directa
curl http://localhost:8001

# 3. Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log
```

### Sin espacio en disco
```bash
# Ver espacio usado
df -h

# Limpiar imágenes Docker antiguas
sudo docker system prune -a

# Limpiar logs antiguos
sudo journalctl --vacuum-time=3d
```

---

## 🌍 URLs de tu Aplicación

- **Página Principal**: http://13.218.229.125/
- **API Docs**: http://13.218.229.125/docs
- **Predicciones**: http://13.218.229.125/pre_flight_predictions.html
- **Dashboard**: http://13.218.229.125/exp_dashboard.html
- **Health Check**: http://13.218.229.125/api/health

---

## 📝 Cambiar a Dominio Personalizado

### 1. Configurar DNS (en tu proveedor de dominio)
```
Tipo: A
Nombre: @
Valor: 13.218.229.125
TTL: 300
```

### 2. Actualizar configuración de Nginx
```bash
sudo nano /etc/nginx/conf.d/smart-intelligence.conf
```

Cambiar:
```nginx
server_name 13.218.229.125;
```

Por:
```nginx
server_name tudominio.com www.tudominio.com;
```

### 3. Instalar SSL (HTTPS)
```bash
# Instalar Certbot
sudo yum install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tudominio.com -d www.tudominio.com --non-interactive --agree-tos --email tu@email.com

# Auto-renovación (ya viene configurada)
sudo certbot renew --dry-run
```

### 4. Reiniciar Nginx
```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🌐 Pasos Rápidos: Conectar smartplating.tech (Dominio + HTTPS)

1) DNS (en tu proveedor)
- Crea estos registros (TTL mínimo permitido por tu panel, por ejemplo 7200):
   - A @ → 13.218.229.125
   - A www → 13.218.229.125

2) Verificar propagación (en EC2)
```bash
nslookup smartplating.tech
nslookup www.smartplating.tech
```
Debe devolver 13.218.229.125.

3) Nginx (en EC2)
```bash
sudo nano /etc/nginx/conf.d/smart-intelligence.conf
```
Poner:
```nginx
server_name smartplating.tech www.smartplating.tech;
```
Aplicar:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

4) HTTPS con Certbot (en EC2)
```bash
sudo yum install -y certbot python3-certbot-nginx
sudo certbot --nginx -d smartplating.tech -d www.smartplating.tech --non-interactive --agree-tos --email TU_EMAIL
sudo certbot renew --dry-run
```

5) Probar
- https://smartplating.tech
- https://smartplating.tech/exp_adding.html (cámara funciona con HTTPS)

Troubleshooting rápido
- Si DNS no resuelve aún: espera 5–30 min (o hasta TTL), verifica que ambos A (@ y www) apunten a 13.218.229.125.
- Si Certbot falla: asegúrate que puerto 80 esté abierto y que `server_name` es el dominio correcto.
- Logs útiles:
```bash
sudo tail -n 200 /var/log/nginx/error.log
sudo docker-compose logs --tail=200
```

---

## 📞 Información de tu Instancia

- **IP Pública**: 13.218.229.125
- **Región**: us-east-1 (Virginia)
- **Usuario SSH**: ec2-user
- **Key File**: smart-intelligence-key.pem
- **Puerto App**: 8001
- **Puerto Web**: 80 (HTTP), 443 (HTTPS)

---

## 🎓 Comandos de Aprendizaje

### Ver qué hace cada servicio
```bash
# Ver contenido del Dockerfile
cat Dockerfile

# Ver configuración de Docker Compose
cat docker-compose.prod.yml

# Ver estructura del proyecto
tree -L 2
```

---

## 🔄 Reinicio Automático al Reiniciar EC2

Tu aplicación ya está configurada para iniciarse automáticamente cuando reinicies la instancia EC2.

### Verificar auto-inicio
```bash
sudo systemctl is-enabled docker
sudo systemctl is-enabled nginx
```

Ambos deben decir: `enabled`

---

## 💡 Tips Útiles

1. **Siempre verifica logs antes de reiniciar**
   ```bash
   sudo docker-compose logs -f
   ```

2. **Prueba configuración de Nginx antes de aplicar**
   ```bash
   sudo nginx -t
   ```

3. **Haz backup antes de cambios importantes**
   ```bash
   cd ~
   tar -czf backup.tar.gz Hackmty_Smart_Intelligence/
   ```

4. **Monitorea uso de recursos**
   ```bash
   sudo docker stats
   ```

---

# 📘 Operaciones y Mantenimiento (Playbook)

## 🚀 Flujo para actualizar la aplicación

```bash
# En EC2
cd ~/Hackmty_Smart_Intelligence
git pull
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml up -d --build
```

## 🔁 Fix de reconexión automática (Snowflake)

Si aplicas cambios a `backend/SnowflakeFinal.py` para reconectar cuando expire el token:

```powershell
# Desde tu PC (PowerShell)
cd C:\Users\guill\Hackmty_Smart_Intelligence
git add backend\SnowflakeFinal.py
git commit -m "Add auto-reconnect for Snowflake token expiration"
git push
```

```bash
# En EC2
cd ~/Hackmty_Smart_Intelligence
git pull
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml up -d --build
```

## 🔒 SSL / HTTPS

```bash
# Verificar renovación automática
sudo certbot renew --dry-run

# Renovar manualmente si fuese necesario
sudo certbot renew

# Reiniciar Nginx tras renovar (opcional)
sudo systemctl restart nginx
```

## 🌍 Elastic IP (IP fija recomendada)

1. AWS Console → EC2 → Elastic IPs → Allocate Elastic IP
2. Actions → Associate Elastic IP → Selecciona tu instancia
3. Si cambia la IP, actualiza los registros DNS A (@ y www)

Nota: Elastic IP es gratuita mientras esté asociada a una instancia en ejecución.

## 🧠 Monitoreo rápido

```bash
# Estado de contenedores
sudo docker-compose ps

# Logs de la app
sudo docker-compose logs -f

# Nginx
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Recursos del sistema
df -h
free -h
sudo docker stats
```

## 💾 Backups

```bash
# Crear backup comprimido
cd ~
tar -czf backup-$(date +%Y%m%d).tar.gz Hackmty_Smart_Intelligence/

# Descargar a tu PC (PowerShell)
scp -i "C:\\Users\\guill\\OneDrive\\Escritorio\\smart-intelligence-key.pem" \
   ec2-user@13.218.229.125:~/backup-*.tar.gz \
   C:\\Users\\guill\\Downloads\\
```

## 🔐 Buenas prácticas de seguridad

- Mantener el sistema actualizado: `sudo yum update -y`
- Security Group: permitir solo 22, 80, 443
- Rotar API keys y considerar AWS Secrets Manager para producción
- Restringir CORS en producción si aplica

## 💰 Costos aproximados

- EC2 t3.small: ~USD 15/mes
- EBS 20GB: ~USD 2/mes
- Transferencia de datos: variable
- Total típico: USD 17–25/mes

Reducir costos: usar t3.micro para baja carga; detener instancia cuando no se use (la IP cambia si no hay Elastic IP).

## 🆘 Troubleshooting rápido

```bash
# Sitio caído
sudo docker-compose ps
sudo docker-compose logs --tail=200
sudo systemctl status nginx

# 502 Bad Gateway
curl -I http://localhost:8001
sudo tail -n 200 /var/log/nginx/error.log

# DNS
nslookup smartplating.tech
nslookup www.smartplating.tech

# SSL
sudo tail -n 200 /var/log/letsencrypt/letsencrypt.log
sudo certbot renew --dry-run

# Poco espacio en disco
df -h
sudo docker system prune -a
sudo journalctl --vacuum-time=7d

# Snowflake token expirado (con reconexión automática). Si persiste:
sudo docker-compose restart
```

## 🔗 URLs clave (dominio)

- Sitio: https://smartplating.tech
- API Docs: https://smartplating.tech/docs
- Dashboard: https://smartplating.tech/exp_dashboard.html
- Predicciones: https://smartplating.tech/pre_flight_predictions.html
- Scanner (cámara): https://smartplating.tech/exp_adding.html


## 📚 Documentación Adicional

- **Deployment Completo**: Ver `DEPLOY_QUICKSTART.md`
- **Setup EC2**: Ver `ec2-setup.md`
- **Conexión SSH**: Ver `CONECTAR_EC2.md`
- **Docker Multi-arch**: Ver `docker-multiarch-deploy.md`

---

**¡Guarda este archivo para referencia futura!** 🚀
