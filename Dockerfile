# ---------- Build Stage ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---------- Production Stage ----------
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r aceest && useradd -r -g aceest aceest

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code
COPY app.py .
COPY requirements.txt .

# Set ownership
RUN chown -R aceest:aceest /app

# Switch to non-root user
USER aceest

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DB_NAME=aceest_fitness.db
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# Run using gunicorn for production or flask dev server
CMD ["python", "-c", "from app import app, init_db; init_db(); app.run(host='0.0.0.0', port=5000)"]
