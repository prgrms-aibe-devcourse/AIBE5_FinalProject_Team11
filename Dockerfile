# ──────────────────────────────────────────────────────────────────────────────
# aeogeo — FastAPI application image
# Used by docker-compose.yml for the fastapi service.
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Build deps for packages that compile C extensions (e.g. numpy)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first so Docker can cache this layer
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy application source
COPY app/ ./app/
COPY run.py .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
