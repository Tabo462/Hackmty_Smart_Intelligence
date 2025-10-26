# 🔐 Cómo Conectarse a EC2 por SSH

## 📋 Prerequisitos

1. **PEM Key** (archivo .pem que descargaste de AWS)
2. **IP Pública** de tu instancia EC2
3. **Security Group** con puerto 22 abierto

## 🚀 Conexión Básica

### Windows (PowerShell)
```powershell
ssh -i "C:\ruta\a\tu-key.pem" ec2-user@TU_IP_PUBLICA
```

### Linux/Mac
```bash
ssh -i ~/ruta/a/tu-key.pem ec2-user@TU_IP_PUBLICA
```

### Ejemplo Real
```bash
ssh -i "C:\Users\guill\Downloads\mi-key.pem" ec2-user@54.123.45.67
```

## 🔑 Permisos de la Key (MUY IMPORTANTE)

### Windows
```powershell
# Tener cuidado con permisos en Windows
icacls "C:\ruta\a\tu-key.pem" /inheritance:r
icacls "C:\ruta\a\tu-key.pem" /grant:r "%username%:R"
```

### Linux/Mac
```bash
chmod 400 tu-key.pem
```

## 📍 Dónde Encontrar la IP

1. Ve a AWS Console → EC2 → Instances
2. Selecciona tu instancia
3. Copia la **Public IPv4 address**

## 👤 Usuarios por AMI

| AMI | Usuario |
|-----|---------|
| Amazon Linux 2023 | `ec2-user` |
| Amazon Linux 2 | `ec2-user` |
| Ubuntu | `ubuntu` |
| RHEL | `ec2-user` |
| Debian | `admin` |

## 🔧 Troubleshooting

### Error: "Permission denied (publickey)"

**Solución 1**: Verificar permisos
```bash
chmod 400 tu-key.pem
```

**Solución 2**: Especificar key explícitamente
```bash
ssh -i tu-key.pem -v ec2-user@IP
```

**Solución 3**: Windows - Verificar permisos
```powershell
icacls "C:\ruta\a\tu-key.pem"
```

### Error: "WARNING: UNPROTECTED PRIVATE KEY FILE"

```bash
chmod 600 tu-key.pem
# o
chmod 400 tu-key.pem
```

### Error: "Connection timeout"

1. Verifica que el Security Group permita puerto 22
2. Verifica que la instancia esté en estado "running"
3. Verifica que la IP pública sea correcta

### Error: "No route to host"

Tu Security Group no permite el puerto 22 desde tu IP

**Solución**: En AWS Console → EC2 → Security Groups
- Edita inbound rules
- Agrega: SSH (22) desde "My IP"

## 🌐 Conexión con Elastic IP

Si configuraste Elastic IP:
```bash
ssh -i tu-key.pem ec2-user@TU_ELASTIC_IP
```

## 🔄 Conexión con SSH Config (Opcional)

Crea `~/.ssh/config`:
```
Host mi-ec2
    HostName TU_IP_PUBLICA
    User ec2-user
    IdentityFile ~/.ssh/tu-key.pem
```

Luego conecta con:
```bash
ssh mi-ec2
```

## ✅ Verificación Rápida

```bash
# Verificar que eres usuario correcto
whoami

# Verificar instalación Docker (después del setup)
docker --version
docker-compose --version

# Ver recursos
df -h  # Espacio en disco
free -h  # Memoria
```

## 🎯 Next Steps (Después de Conectarte)

```bash
# 1. Actualizar sistema
sudo yum update -y

# 2. Instalar Docker (si no está instalado)
sudo yum install -y docker
sudo systemctl start docker
sudo usermod -aG docker ec2-user

# 3. Salir y reconectar para aplicar cambios
exit
ssh -i tu-key.pem ec2-user@TU_IP

# 4. Verificar Docker
docker ps
```

## 📝 Script de Conexión Rápida (PowerShell)

```powershell
# Conectar.ps1
$KEY = "C:\Users\guill\Downloads\mi-key.pem"
$IP = "54.123.45.67"

ssh -i $KEY ec2-user@$IP
```

Uso:
```powershell
.\Conectar.ps1
```

## 🎉 ¡Conectado!

Ahora puedes:
- Clonar tu repositorio
- Ejecutar `deploy-ec2.sh`
- Configurar tu aplicación

