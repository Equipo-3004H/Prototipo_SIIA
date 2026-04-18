# Usamos una imagen base ligera de Python
FROM python:3.10-slim

# Evitamos que Python genere archivos basura (.pyc) y forzamos logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecemos el directorio de trabajo
WORKDIR /app

# Instalamos ffmpeg y librerías de construcción (vitales para torchaudio)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiamos los requerimientos y los instalamos usando la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-descarga del Modelo Acústico Wav2Vec2
# Usamos un modelo estándar de HuggingFace optimizado para extracción de características de audio.
# Esto descargará varios cientos de megabytes a la imagen de Docker para un arranque instantáneo.
RUN python -c "from transformers import Wav2Vec2FeatureExtractor, AutoModelForAudioClassification; \
model_name = 'superb/wav2vec2-base-superb-er'; \
Wav2Vec2FeatureExtractor.from_pretrained(model_name); \
AutoModelForAudioClassification.from_pretrained(model_name)"

# Copiamos el resto del código (el main.py que construiremos luego)
COPY . .

# Comando de inicio
CMD ["python", "main.py"]

