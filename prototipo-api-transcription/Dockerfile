FROM python:3.10-slim

# Instalar ffmpeg (sin sudo)
RUN apt-get update && apt-get install -y ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copiar requirements primero (mejor cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar app
COPY . .

# Render usa variable $PORT → necesitamos shell
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]