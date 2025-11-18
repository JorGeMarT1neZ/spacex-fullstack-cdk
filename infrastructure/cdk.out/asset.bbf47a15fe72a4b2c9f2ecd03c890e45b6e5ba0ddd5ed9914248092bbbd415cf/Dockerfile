FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Colectar archivos estáticos
RUN python manage.py collectstatic --noinput --clear

# Crear directorio para archivos estáticos si no existe
RUN mkdir -p /app/staticfiles

EXPOSE 8000

# Health check mejorado
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run gunicorn con configuración mejorada
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-", "spacex_site.wsgi:application"]