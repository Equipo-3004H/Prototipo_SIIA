# Prototipo SIIA: Detección de lenguaje agresivo multimodal

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![HuggingFace](https://img.shields.io/badge/huggingface-%23FFD21E.svg?style=for-the-badge&logo=huggingface&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-D82C20?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-4A154B?style=for-the-badge&logo=socketdotio&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Transformers](https://img.shields.io/badge/Transformers-FFBF00?style=for-the-badge&logo=huggingface&logoColor=black)

Este repositorio contiene un prototipo académico para el monitoreo y detección de lenguaje agresivo en conversaciones, con enfoque multimodal (audio + texto). El trabajo fue desarrollado por el Equipo 3004H para la asignatura de Seminario de Innovación en Inteligencia Artificial (SIIA), Maestría en Inteligencia Artificial de UNIR México.

La solución combina:

- Transcripción automática del audio (ASR).
- Análisis semántico de texto para detección de agresividad.
- Análisis acústico/prosódico del audio.
- Ensamble final para clasificar el nivel de riesgo/agresividad.

## Tabla de contenido

- [1. Autores](#1-autores)
- [2. Objetivo](#2-objetivo)
- [3. Arquitectura](#3-arquitectura)
- [4. Estructura del repositorio](#4-estructura-del-repositorio)
- [5. Requisitos](#5-requisitos)
- [6. Ejecución rápida con Docker](#6-ejecución-rápida-con-docker)
- [7. Ejecución local por servicio](#7-ejecución-local-por-servicio)
- [8. Scripts de evaluación y datos](#8-scripts-de-evaluación-y-datos)

## 1. Autores

| Apellidos            | Nombres        |
| -------------------- | -------------- |
| Martínez Cruz        | Luis Arturo    |
| Rentería Ramírez     | Mariana Jazmín |
| Rodríguez Valladares | Olga Sarahi    |

## 2. Objetivo

Implementar una solución de IA multimodal que permita identificar lenguaje agresivo en conversaciones casi en tiempo real, priorizando recall alto para reducir falsos negativos en escenarios de posible maltrato psicológico hacia personas adultas mayores.

## 3. Arquitectura

El prototipo actual se ejecuta como una arquitectura de microservicios orquestada con Docker Compose:

- `caddy_proxy`: reverse proxy y servidor estático del frontend.
- `redis_broker`: bus de mensajería (Pub/Sub).
- `ws_gateway`: entrada WebSocket y enrutamiento de sesiones.
- `asr_worker`: transcripción de audio.
- `robertuito_worker`: clasificación semántica en texto.
- `wav2vec_worker`: clasificación acústica/prosódica.
- `ensemble_worker`: integración y veredicto final.

Flujo general:

1. El frontend envía audio al gateway por WebSocket.
2. El gateway publica audio en Redis.
3. Los workers procesan y publican resultados parciales.
4. El ensamble emite el resultado final.
5. El gateway devuelve salidas al cliente en tiempo real.

## 4. Estructura del repositorio

```text
Prototipo_SIIA/
├── README.md
├── evaluacion_modelo_v3.py
├── test_whisper_chunk.py
├── test_whisper_sin_chunk.py
├── 220_test_WER_whisper_Correcto.py
├── Set de datos/
│   ├── Clasificaciones_reales_220.csv
│   ├── Nombre Archivo VS Frase_Clasif.txt
│   └── qa_audios_asr225/
└── multimodal-cluster/
    ├── Caddyfile
    ├── docker-compose.yml
    ├── frontend/
    ├── gateway/
    ├── asr_worker/
    ├── robertuito_worker/
    ├── wav2vec_worker/
    └── ensemble_worker/
```

## 5. Requisitos

- Docker Engine 24+.
- Docker Compose v2.
- Git. 

## 6. Ejecución rápida con Docker

Desde la raíz del repositorio:

```bash
cd multimodal-cluster
docker compose up --build
```

Accesos por defecto:

- Frontend: `http://localhost:80`
- Gateway (health): `http://localhost:8000` (si se expone manualmente en local)
- Redis: `localhost:6379` (solo para pruebas locales)

Para detener:

```bash
docker compose down
```

## 7. Ejecución local por servicio

Si prefieres levantar componentes sin Docker, entra a cada carpeta de servicio, crea un entorno virtual e instala dependencias con su `requirements.txt`.

Ejemplo genérico:

```bash
cd multimodal-cluster/gateway
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Nota: para funcionamiento completo necesitas Redis activo y la comunicación entre todos los workers.

## 8. Scripts de evaluación y datos

En la raíz del proyecto encontrarás scripts para pruebas y evaluación de modelos ASR/ensamble, por ejemplo:

- `evaluacion_modelo_v3.py`
- `test_whisper_chunk.py`
- `test_whisper_sin_chunk.py`
- `220_test_WER_whisper_Correcto.py`

Los conjuntos de datos están en `Set de datos/` y en `multimodal-cluster/frontend/qa_audios_asr225/`.
