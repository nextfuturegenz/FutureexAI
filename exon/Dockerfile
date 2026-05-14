# FROM python:3.11-slim

# WORKDIR /app

# # Install system dependencies for sentence-transformers and build tools
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# # Copy entire FutureexAI project
# COPY . /app/

# # Install Python dependencies
# RUN pip install --no-cache-dir -r /app/exon/requirements.txt

# # Set environment variables
# ENV PYTHONPATH=/app
# ENV FUTUREEX_PATH=/app

# # Create necessary directories
# RUN mkdir -p /app/exon/api/routes /app/exon/api/websocket /app/exon/personas /app/exon/scripts

# # Create knowledge directory (will be populated by volume mount or COPY)
# RUN mkdir -p /app/knowledge

# # Copy knowledge files into the image (optional - you can also use a volume)
# COPY exon/knowledge/ /app/knowledge/

# # Expose port
# EXPOSE 8000

# # Health check
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#   CMD curl -f http://localhost:8000/ || exit 1

# # Run the API server
# CMD ["uvicorn", "exon.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for sentence-transformers, build tools, and Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    # Chromium dependencies (all available in Debian)
    libnss3 \
    libnspr4 \
    libatk1.0-0t64 \
    libatk-bridge2.0-0t64 \
    libcups2t64 \
    libdrm2 \
    libdbus-1-3 \
    libatspi2.0-0t64 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2t64 \
    libxkbcommon0 \
    libwayland-client0 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libglib2.0-0t64 \
    # Fonts
    fonts-liberation \
    fonts-unifont \
    && rm -rf /var/lib/apt/lists/*

# Copy entire FutureexAI project
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/exon/requirements.txt

# Install Playwright Chromium browser only (skip deps - we installed them above)
RUN playwright install chromium --with-deps 2>/dev/null || playwright install chromium

# Set environment variables
ENV PYTHONPATH=/app
ENV FUTUREEX_PATH=/app
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Create necessary directories
RUN mkdir -p /app/exon/api/routes /app/exon/api/websocket /app/exon/personas /app/exon/scripts

# Create knowledge directory
RUN mkdir -p /app/knowledge

# Copy knowledge files
COPY exon/knowledge/ /app/knowledge/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Run the API server
CMD ["uvicorn", "exon.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]