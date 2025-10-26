# 📱 Instrucciones para Probar la App en tu Teléfono

## 🚀 Inicio Rápido

### 1. Inicia el Servidor
```bash
cd backend
python simple_main.py
```

El servidor iniciará con HTTPS y te mostrará las URLs disponibles.

### 2. Conecta tu Teléfono

**Pasos importantes:**
1. ✅ Asegúrate de que tu teléfono esté en la **misma red WiFi** que tu computadora
2. 📱 Busca la IP que se muestra en la consola (ejemplo: `192.168.1.100`)
3. 🌐 Abre el navegador en tu teléfono e ingresa:
   ```
   https://TU_IP:8001/exp_adding.html
   ```

### 3. Acepta el Certificado SSL

Al entrar por primera vez, el navegador mostrará una advertencia de seguridad porque estamos usando un certificado autofirmado. Esto es **seguro en tu red local**.

- **Chrome/Android**: Haz clic en "Avanzado" → "Continuar a sitio web"
- **Safari/iOS**: Haz clic en "Mostrar detalles" → "Visitar sitio web"

### 4. Permite Acceso a la Cámara

Cuando lo solicite:
1. 📷 Dale permisos a la cámara
2. Selecciona la cámara trasera (si es posible)
3. Acepta para usar el escáner

## 🔍 Usar el Escáner de Códigos de Barras

1. Haz clic en **"Start Scanner"**
2. Apunta la cámara al código de barras
3. El escáner detectará automáticamente el código
4. El formulario se llenará automáticamente si el producto existe en la base de datos

## ⚠️ Troubleshooting

### El navegador no deja acceder al sitio
- Asegúrate de usar **HTTPS** (no HTTP)
- Acepta la advertencia de certificado

### La cámara no funciona
- Verifica los permisos de cámara en tu navegador
- Intenta recargar la página
- Asegúrate de estar usando HTTPS (no HTTP)

### No puedo acceder desde el teléfono
- Verifica que ambos dispositivos estén en la misma red WiFi
- Verifica que el firewall de Windows permita conexiones en el puerto 8001
- Intenta desactivar temporalmente el firewall para probar

### Deseo cambiar la cámara
- Haz clic en **"Select Camera"** para elegir una cámara específica

## 🔧 Configuración del Firewall

Si no puedes acceder desde tu teléfono, necesitas permitir el puerto 8001:

1. Abre **Windows Defender Firewall**
2. Haz clic en **"Permitir una aplicación o característica"**
3. Haz clic en **"Configuración avanzada"**
4. Selecciona **"Reglas de entrada"**
5. Busca Python y asegúrate de que esté habilitado para puerto 8001

O agrega una regla temporal:
- Nuevo → Regla de entrada
- Puerto → TCP → 8001
- Permitir conexión

## 📝 Notas Importantes

- ✅ Todo funciona desde `simple_main.py` - no necesitas correr nada extra
- ✅ Los certificados SSL se generan automáticamente la primera vez
- ✅ Los certificados se guardan en `backend/cert.pem` y `backend/key.pem`
- ✅ Los certificados están agregados a `.gitignore` - no se subirán al repositorio

