# PartnerOpsAI Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=5 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Make start script executable
RUN chmod +x /app/start.sh

# Run startup script
CMD ["/app/start.sh"]
