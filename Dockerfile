# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project structure
COPY . /app/

# Create necessary directories and set permissions
RUN mkdir -p /app/backend/static && \
    mkdir -p /app/frontend/media_files

# Copy the backend code
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# Set the working directory to backend where simple_main.py is located
WORKDIR /app/backend

# Create a startup script
RUN echo '#!/bin/bash\n\
    echo "🚀 Starting Smart Intelligence API..."\n\
    echo "📱 Frontend available at: http://localhost:8001/index.html"\n\
    echo "🔮 Predictions at: http://localhost:8001/pre_flight_predictions.html"\n\
    echo "📚 API docs at: http://localhost:8001/docs"\n\
    python simple_main.py' > /app/start.sh && chmod +x /app/start.sh

# Expose the port that the app runs on
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/health || exit 1

# Run the application
CMD ["/app/start.sh"]
