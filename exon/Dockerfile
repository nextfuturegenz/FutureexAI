FROM python:3.11-slim

WORKDIR /app

# Copy only Exon code and the entire FutureexAI repo (will be mounted via volume in compose)
COPY exon/ /app/exon/
COPY src/ /app/src/
COPY old/ /app/old/

# Install dependencies
RUN pip install --no-cache-dir -r /app/exon/requirements.txt

ENV PYTHONPATH=/app
ENV FUTUREEX_PATH=/app

EXPOSE 8000

CMD ["uvicorn", "exon.api.app:app", "--host", "0.0.0.0", "--port", "8000"]