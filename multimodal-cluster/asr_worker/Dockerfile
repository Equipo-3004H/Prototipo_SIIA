FROM python:3.10-slim-bookworm

WORKDIR /app

# Instalar dependencias del sistema para procesamiento de audio
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# El parámetro -u fuerza a Python a imprimir los logs en la terminal inmediatamente
CMD ["python", "-u", "main.py"]