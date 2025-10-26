# Build multi-architecture Docker images (AMD64 and ARM64)
# This allows the same image to work on Intel/AMD and ARM devices

Write-Host "🏗️  Building multi-architecture Docker image..." -ForegroundColor Cyan
Write-Host "📦 Platforms: linux/amd64, linux/arm64" -ForegroundColor Yellow
Write-Host ""

# Create a new builder instance (only needed once)
Write-Host "Creating buildx builder..." -ForegroundColor Green
docker buildx create --name multiarch-builder --use 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Builder already exists or created successfully" -ForegroundColor Yellow
}

docker buildx inspect --bootstrap

# Build for multiple platforms
Write-Host ""
Write-Host "Building for multiple platforms..." -ForegroundColor Green
docker buildx build `
  --platform linux/amd64,linux/arm64 `
  -t hackmty_smart_intelligence-smart-intelligence-api:latest `
  -t hackmty_smart_intelligence-smart-intelligence-api:multiarch `
  .

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Multi-architecture build complete!" -ForegroundColor Green
    Write-Host "🚀 You can now use: docker-compose up" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Build failed. Check the errors above." -ForegroundColor Red
}

