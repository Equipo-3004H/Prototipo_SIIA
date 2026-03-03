FROM python:3.10-slim

# Instalar ffmpeg (sin sudo)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libavfilter-dev \
    libswscale-dev \
    libswresample-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copiar requirements primero (mejor cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar app
COPY . .


CMD ["streamlit", "run", "app.py", "--server.port=$PORT", "--server.address=0.0.0.0"]