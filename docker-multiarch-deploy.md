# Build Multi-Arquitectura para Distribución

## Opción 1: Con Docker Hub (Recomendado para Producción)

1. **Login a Docker Hub:**
```bash
docker login
```

2. **Tag de tu imagen:**
```bash
docker tag hackmty_smart_intelligence-smart-intelligence-api:latest TU_USERNAME/hackmty_smart_intelligence:latest
```

3. **Build y Push multi-arquitectura:**
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t TU_USERNAME/hackmty_smart_intelligence:latest --push .
```

## Opción 2: Sin Registry (Build y Load Local)

### Para tu arquitectura actual (AMD64 en tu caso):
```bash
docker buildx build --platform linux/amd64 -t hackmty_smart_intelligence-smart-intelligence-api:amd64 --load .
```

### Para ARM64 (si tienes o vas a tener un Mac M1/M2):
```bash
docker buildx build --platform linux/arm64 -t hackmty_smart_intelligence-smart-intelligence-api:arm64 --load .
```

### Luego usarlos en docker-compose:
En `docker-compose.yml` cambia el tag según tu arquitectura:
```yaml
image: hackmty_smart_intelligence-smart-intelligence-api:amd64  # o :arm64
```

## Opción 3: Registry Local con Docker Registry

```bash
# Iniciar registry local
docker run -d -p 5000:5000 --name registry registry:2

# Build y push al registry local
docker buildx build --platform linux/amd64,linux/arm64 -t localhost:5000/hackmty_smart_intelligence:latest --push .

# Usar en docker-compose
# Agregar: image: localhost:5000/hackmty_smart_intelligence:latest
```

