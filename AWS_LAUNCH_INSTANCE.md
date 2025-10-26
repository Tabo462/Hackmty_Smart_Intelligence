# 🚀 Guía Paso a Paso: Lanzar Instancia EC2

## 📋 Paso 1: Name and tags

**Instance name**: 
```
smart-intelligence-app
```

Click **Next**

---

## 💻 Paso 2: Application and OS Images (AMI)

**AMI**: 
- ✅ Amazon Linux 2023 AMI (recomendado)
- O: Ubuntu Server 22.04 LTS

**Architecture**: 
- x86_64 (Intel/AMD)

Click **Next**

---

## 🔧 Paso 3: Instance type

Para empezar:
- ✅ **t3.small** (2 vCPU, 2 GB RAM) - Suficiente para desarrollo
- **t3.medium** (2 vCPU, 4 GB RAM) - Mejor para producción
- **t3.large** (2 vCPU, 8 GB RAM) - Para más carga

**Nota**: El pricing aparece en la parte inferior.

Click **Next**

---

## 🔑 Paso 4: Key pair (login)

**Create new key pair**:
- **Key pair name**: `smart-intelligence-key`
- **Key pair type**: RSA
- **Private key file format**: .pem
- **Download**: Click **Create key pair**

**¡IMPORTANTE!**: Guarda el archivo `.pem` en un lugar seguro:
```
C:\Users\guill\Downloads\smart-intelligence-key.pem
```

Click **Next**

---

## 🔒 Paso 5: Network settings

### Configuración básica (desarrollo):

**VPC**: `default-vpc` (o la que ya tengas)

**Subnet**: Cualquiera

**Auto-assign public IP**: ✅ Enable

**Security group**:
- ✅ **Create security group**
- **Name**: `smart-intelligence-sg`
- **Description**: Security group for Smart Intelligence app

**Inbound Security Group Rules**:

| Type | Protocol | Port Range | Source |
|------|----------|------------|--------|
| SSH | TCP | 22 | My IP ✅ |
| HTTP | TCP | 80 | Anywhere-IPv4 (0.0.0.0/0) |
| HTTPS | TCP | 443 | Anywhere-IPv4 (0.0.0.0/0) |

**Outbound**: Dejar por defecto (All traffic)

Click **Next**

---

## 💾 Paso 6: Configure storage

**Size (GiB)**: `20 GB` (mínimo)

**Volume type**: 
- General Purpose SSD (gp3) - Recomendado
- gp2 - Más barato

**Delete on termination**: 
- ❌ Desmarcar si quieres conservar datos

Click **Next**

---

## 📝 Paso 7: Advanced details

**User data** (opcional): 

Dejar vacío por ahora. Lo configuraremos después.

Click **Next**

---

## 📊 Paso 8: Summary

**Review summary**:
- Instance type: t3.small
- Key pair: smart-intelligence-key.pem
- Security group: smart-intelligence-sg
- Storage: 20 GB

**Estimated cost**: Ver el precio en la esquina superior derecha

---

## ✅ Paso 9: Launch Instance

Click **Launch instance**

Espera 1-2 minutos mientras se crea...

---

## 📍 Paso 10: Obtener IP Pública

1. Ve a **EC2 Dashboard** → **Instances**
2. Selecciona tu instancia
3. Copia la **Public IPv4 address**
4. Ejemplo: `54.123.45.67`

---

## 🔐 Paso 11: Conectarse por SSH

### Windows (PowerShell):

```powershell
ssh -i "C:\Users\guill\Downloads\smart-intelligence-key.pem" ec2-user@TU_IP_PUBLICA
```

Ejemplo:
```powershell
ssh -i "C:\Users\guill\Downloads\smart-intelligence-key.pem" ec2-user@54.123.45.67
```

**Si hay error de permisos**:
```powershell
icacls "C:\Users\guill\Downloads\smart-intelligence-key.pem" /inheritance:r
icacls "C:\Users\guill\Downloads\smart-intelligence-key.pem" /grant:r "%username%:R"
```

---

## ✅ Paso 12: Verificar Conexión

```bash
# En la terminal SSH de EC2:
whoami
# Debe mostrar: ec2-user

# Ver recursos disponibles
df -h
free -h
```

---

## 🚀 Siguiente: Deploy de la App

Una vez conectado, sigue las instrucciones en:
- **DEPLOY_QUICKSTART.md**

O ejecuta el script automático:
```bash
git clone https://github.com/TU_REPO/Hackmty_Smart_Intelligence.git
cd Hackmty_Smart_Intelligence
chmod +x deploy-ec2.sh
bash deploy-ec2.sh
```

---

## 💰 Costos Aproximados

- **t3.small**: ~$0.02/hr (~$15/mes) - Para desarrollo
- **t3.medium**: ~$0.04/hr (~$30/mes) - Para producción
- **t3.large**: ~$0.08/hr (~$60/mes) - Para alta carga

**Storage**: ~$2/mes por 20 GB

**Total estimado**: $17-65/mes dependiendo del tamaño

---

## 🆘 Troubleshooting

### No puedo conectarme por SSH

1. **Verificar Security Group**: Puerto 22 debe estar abierto para "My IP"
2. **Verificar estado**: La instancia debe estar "running"
3. **Verificar IP**: Usa la Public IPv4, no la Elastic IP

### "Permission denied (publickey)"

```powershell
icacls "C:\ruta\a\smart-intelligence-key.pem" /grant:r "%username%:R"
```

### No tengo acceso al puerto 22

En **Security Groups** → **Edit inbound rules** → Add rule:
- Type: SSH
- Port: 22
- Source: My IP (o 0.0.0.0/0 para pruebas)

---

## 📚 Recursos Adicionales

- **CONECTAR_EC2.md** - Guía de conexión SSH
- **DEPLOY_QUICKSTART.md** - Deploy rápido
- **ec2-setup.md** - Configuración completa

---

## 🎉 ¡Listo!

Tu instancia está lista para deployar la aplicación Smart Intelligence.


