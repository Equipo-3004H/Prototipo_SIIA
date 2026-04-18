# Usamos una imagen base ligera de Python
FROM python:3.10-slim

# Evitamos que Python genere archivos basura (.pyc) y forzamos el volcado de logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos dependencias del sistema necesarias para compilar librerías de C/C++
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos primero el archivo de requerimientos (aprovecha la caché de Docker)
COPY requirements.txt .

# Instalamos las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Pre-descarga del Modelo RoBERTa
# Descargamos el modelo de pysentimiento en la fase de construcción de la imagen.
# Esto hace que la imagen sea más pesada, pero el contenedor arrancará en 1 segundo.
RUN python -c "from pysentimiento import create_analyzer; create_analyzer(task='sentiment', lang='es')"

# Copiamos el resto del código fuente (el main.py que haremos en el siguiente paso)
COPY . .

# Comando para iniciar el trabajador
CMD ["python", "main.py"]