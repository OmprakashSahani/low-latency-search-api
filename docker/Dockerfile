# Base: small, but with manylinux wheels available
FROM python:3.12-slim

# Security: don't run as root
RUN useradd -ms /bin/bash appuser

WORKDIR /app

# System deps (curl for diagnostics; build tools only if needed)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Install Python deps first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY app ./app

# Expose default port
EXPOSE 8000

# Env hardening
ENV PYTHONUNBUFFERED=1 \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=8000

# Switch to non-root
USER appuser

# Start the API
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
