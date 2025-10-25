# OpenPlate Backend - Quick Start Script
# Run this script to start the FastAPI server

Write-Host "🚀 Starting OpenPlate Backend Server..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

# Set Python path
$env:PYTHONPATH="."

# Start server
Write-Host ""
Write-Host "✅ Server starting on http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Available endpoints:" -ForegroundColor Cyan
Write-Host "  POST http://localhost:8000/api/upload_data" -ForegroundColor White
Write-Host "  POST http://localhost:8000/api/scan" -ForegroundColor White
Write-Host "  GET  http://localhost:8000/api/stats" -ForegroundColor White
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
