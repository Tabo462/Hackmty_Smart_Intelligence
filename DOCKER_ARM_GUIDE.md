# Guía de Compatibilidad ARM para Docker

Este proyecto ahora tiene soporte para procesadores ARM (Apple Silicon M1/M2, ARM servers, etc.)

## 📋 Opciones de Uso

### Opción 1: AMD64 (Intel/AMD - Default)
Para máquinas Intel o AMD (Windows x64, Linux x64, Mac Intel):

```bash
docker-compose up --build
```

El archivo `docker-compose.yml` por defecto usa `platform: linux/amd64`

### Opción 2: ARM64 (Apple Silicon M1/M2, ARM Servers)
Para Mac con Apple Silicon o servidores ARM:

```bash
docker-compose -f docker-compose.arm.yml up --build
```

O modifica `docker-compose.yml` cambiando la línea:
```yaml
platform: linux/amd64  # Cambia a linux/arm64
```

### Opción 3: Build Multi-Arquitectura (Recomendado para Producción)
Crea una imagen que funciona en ambas arquitecturas:

#### Windows (PowerShell):
```powershell
# Crear builder multi-plataforma
docker buildx create --name multiarch-builder --use

# Build para ambas arquitecturas
docker buildx build --platform linux/amd64,linux/arm64 -t hackmty_smart_intelligence-smart-intelligence-api:latest .

# Build y push (si tienes Docker Hub)
docker buildx build --platform linux/amd64,linux/arm64 -t hackmty_smart_intelligence-smart-intelligence-api:latest --push .
```

#### Linux/Mac:
```bash
bash docker-build-multi-arch.sh
```

## 🎯 ¿Cómo Saber Qué Plataforma Usar?

### Ver tu arquitectura:
```bash
# Windows
echo $env:PROCESSOR_ARCHITECTURE

# Linux/Mac
uname -m
```

- `x86_64` o `AMD64` → usa `linux/amd64`
- `ARM64` o `aarch64` → usa `linux/arm64`
- Mac M1/M2 → usa `linux/arm64`

## ⚠️ Notas Importantes

1. **Performance en ARM**: Si usas ARM pero especificas AMD64, Docker usará emulación (más lento)
2. **Dependencies**: Algunos paquetes Python con extensiones C pueden necesitar compilarse para ARM
3. **Snowflake SDK**: El `snowflake-connector-python` tiene wheels pre-compilados para ambas arquitecturas

## 🔧 Solución de Problemas

### Error: "platform is not supported"
```bash
# Verifica que Docker buildx esté disponible
docker buildx version

# Si no está, instala Docker Desktop actualizado
```

### Imagen muy lenta en Mac M1/M2
- Cambia de `linux/amd64` a `linux/arm64`
- O usa el archivo `docker-compose.arm.yml`

### Error de compilación en ARM
Algunos paquetes necesitan dependencias del sistema:
```dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
```

## 📚 Recursos

- [Docker multi-platform build](https://docs.docker.com/build/building/multi-platform/)
- [Docker buildx](https://docs.docker.com/buildx/working-with-buildx/)

