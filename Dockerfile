FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY main.py .

# Exponer el puerto
EXPOSE 8000

# Variables de entorno por defecto (sobreescribir con docker-compose o -e)
ENV DB_HOST=localhost
ENV DB_PORT=3306
ENV DB_USER=moodle
ENV DB_PASSWORD=password
ENV DB_NAME=moodle

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
