# 🔧 Solución: Connection Timed Out en SSH

## 🚨 Problema
```
Connection timed out
Connection to 98.88.84.164 port 22: Connection timed out
```

## ✅ Soluciones (Probarlas en orden)

---

### 🔴 Solución 1: Verificar Security Group (MÁS COMÚN)

**Paso 1**: Ve a AWS Console → EC2 → Security Groups

**Paso 2**: Selecciona tu Security Group

**Paso 3**: Abre la pestaña **Inbound rules**

**Paso 4**: Busca la regla de **SSH (Port 22)**

**❌ Si NO existe o no permite tu IP**:

1. Click **Edit inbound rules**
2. Click **Add rule**
3. Configurar:
   - **Type**: SSH
   - **Protocol**: TCP
   - **Port**: 22
   - **Source**: `My IP` (debería auto-detectar tu IP)
   - O si no funciona: `0.0.0.0/0` (permite desde cualquier lugar - solo para pruebas)

4. Click **Save rules**

---

### 🔴 Solución 2: Verificar Estado de la Instancia

1. Ve a EC2 Console → Instances
2. Verifica que tu instancia esté en estado **"running"**
3. Verifica que el estado de checks sea **"2/2 checks passed"**
4. Si está en "pending", espera 1-2 minutos

---

### 🔴 Solución 3: Verificar IP Pública

1. En EC2 Console → Instances
2. Selecciona tu instancia
3. Copia la **Public IPv4 address** (no la Private IP)
4. Verifica que sea correcta: `98.88.84.164`

**Nota**: Si reinicias la instancia, la IP puede cambiar (a menos que uses Elastic IP)

---

### 🔴 Solución 4: Verificar Instancia en Subnet Pública

**Verificar**:
1. EC2 → Instances → Click en tu instancia
2. Ver **Subnet ID**
3. Click en el Subnet
4. Verifica que tenga "Auto-assign public IPv4" = **Yes**

**Si es No**:
- Tu instancia está en subnet privada
- Crear nueva instancia en subnet pública

---

### 🔴 Solución 5: Firewall o Antivirus Local

**Windows Firewall / Antivirus puede estar bloqueando**

```powershell
# Temporalmente deshabilitar firewall para probar
# (Solo para diagnóstico, luego reactivar)

netsh advfirewall set allprofiles state off

# Probar conexión
ssh -i "tu-key.pem" ec2-user@98.88.84.164

# Reactivar firewall
netsh advfirewall set allprofiles state on
```

---

### 🔴 Solución 6: Verificar Puerto 22 desde tu Computadora

```powershell
# Probar si puedes conectarte al puerto 22
Test-NetConnection -ComputerName 98.88.84.164 -Port 22
```

Si dice "TcpTestSucceeded: True" → El puerto funciona  
Si dice "TcpTestSucceeded: False" → Hay problema de red

---

## 🔧 Quick Fix (Solución Rápida)

### Opción A: Abrir Puerto 22 para Cualquiera (Solo para pruebas)

1. EC2 → Security Groups
2. Selecciona tu security group
3. Inbound rules → Edit
4. Add rule:
   - Type: SSH
   - Port: 22
   - Source: `0.0.0.0/0`
5. Save rules

**⚠️ Advertencia**: Esto permite acceso SSH desde cualquier lugar. Solo para pruebas.

---

### Opción B: Obtener tu IP Actual

```powershell
# Ver tu IP pública actual
curl https://ifconfig.me
```

Luego en Security Group, usa esa IP específica:
- Source: `TU_IP/32` (ejemplo: `123.45.67.89/32`)

---

## 📋 Checklist de Diagnóstico

✅ Security Group permite puerto 22 desde tu IP
✅ Instancia está en estado "running"
✅ Estás usando la Public IPv4 address (no la privada)
✅ La instancia pasó los health checks (2/2)
✅ El archivo .pem tiene permisos correctos en Windows

---

## 🆘 Si Nada Funciona

**Recrear la instancia** con configuración correcta:

1. Terminar la instancia actual
2. Launch nueva instancia
3. **En Security Group**: Asegúrate de agregar regla SSH desde el principio
4. Durante launch, configura correctamente el security group

---

## 📞 Verificación Final

```powershell
# Verificar conexión
ssh -v -i "tu-key.pem" ec2-user@98.88.84.164
```

La flag `-v` muestra detalles del proceso de conexión.

---

## 🎯 Solución Más Probable

**99% de las veces**: Security Group no permite SSH desde tu IP

**Fix rápido**:
1. EC2 Console → Security Groups
2. Edit inbound rules
3. Asegúrate de tener:
   ```
   SSH | TCP | 22 | My IP (o 0.0.0.0/0)
   ```
4. Save

**Luego reconectar**:
```powershell
ssh -i "tu-key.pem" ec2-user@98.88.84.164
```

