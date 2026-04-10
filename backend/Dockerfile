FROM python:3.12-slim

WORKDIR /app

# Prevents .pyc files; forces stdout/stderr to be unbuffered for Railway logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# gcc: needed to compile asyncpg C extensions
# libpq-dev: PostgreSQL client headers for psycopg
# curl: used by the HEALTHCHECK below
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies in a separate layer so rebuilds are fast when
# only application code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

EXPOSE 8000

# Docker will mark the container unhealthy if this fails three times.
# Railway surfaces this in its dashboard.
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
