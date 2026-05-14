FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for sentence-transformers and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy entire FutureexAI project
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/exon/requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV FUTUREEX_PATH=/app

# Create necessary directories
RUN mkdir -p /app/exon/api/routes /app/exon/api/websocket /app/exon/personas /app/exon/scripts

# Create knowledge directory (will be populated by volume mount or COPY)
RUN mkdir -p /app/knowledge

# Copy knowledge files into the image (optional - you can also use a volume)
COPY exon/knowledge/ /app/knowledge/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Run the API server
CMD ["uvicorn", "exon.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]