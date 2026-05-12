FROM python:3.11-slim

WORKDIR /app

# Copy entire FutureexAI project
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r /app/exon/requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV FUTUREEX_PATH=/app

# Create necessary directories
RUN mkdir -p /app/exon/api/routes /app/exon/api/websocket /app/exon/personas /app/exon/scripts

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Run the API server
CMD ["uvicorn", "exon.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]