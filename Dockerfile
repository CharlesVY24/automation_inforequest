# Dockerfile optimizado para producción
FROM python:3.11-slim-bookworm

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Instalar dependencias del sistema necesarias (minimales)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        gcc \
        git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias dentro de un venv
COPY requirements.txt /app/requirements.txt
RUN python -m venv /opt/venv \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --prefer-binary -r /app/requirements.txt \
    && pip install --no-cache-dir gunicorn \
    # limpiar paquetes de compilación para reducir el tamaño de la imagen
    && apt-get remove -y --purge build-essential gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copiar solo lo necesario para reducir el contexto
COPY . /app

# Crear usuario no-root
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Puerto expuesto por la aplicación
EXPOSE 8000

# Comando de producción usando Gunicorn + Uvicorn worker
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "main:app", "--bind", "0.0.0.0:8000", "--timeout", "120"]