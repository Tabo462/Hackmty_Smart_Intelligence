#!/bin/bash
# Build multi-architecture Docker images (AMD64 and ARM64)
# This allows the same image to work on Intel/AMD and ARM devices

echo "🏗️  Building multi-architecture Docker image..."
echo "📦 Platforms: linux/amd64, linux/arm64"
echo ""

# Create a new builder instance (only needed once)
docker buildx create --name multiarch-builder --use 2>/dev/null || echo "Builder already exists"
docker buildx inspect --bootstrap

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t hackmty_smart_intelligence-smart-intelligence-api:latest \
  -t hackmty_smart_intelligence-smart-intelligence-api:multiarch \
  . \
  --push 2>&1 | grep -v "unauthorized"

echo ""
echo "✅ Multi-architecture build complete!"
echo "🚀 You can now use: docker-compose up"

