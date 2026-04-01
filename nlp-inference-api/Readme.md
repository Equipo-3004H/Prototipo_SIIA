# API REST de Clasificación de Texto en Español Utilizando RoBERTuito

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge\&logo=python\&logoColor=ffdd54)
![HuggingFace](https://img.shields.io/badge/huggingface-%23FFD21E.svg?style=for-the-badge\&logo=huggingface\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge\&logo=fastapi)
![Docker](https://img.shields.io/badge/docker-0db7ed?style=for-the-badge\&logo=docker\&logoColor=white)
![Transformers](https://img.shields.io/badge/Transformers-ffcc00?style=for-the-badge)
![NLP](https://img.shields.io/badge/NLP-Natural%20Language%20Processing-blue?style=for-the-badge)

---

## DEMO técnico del API REST desplegado en Render

| Componente                    | Url                                      |
| ----------------------------- | ---------------------------------------- |
| API REST            | https://nlp-api-6h44.onrender.com |
| Swagger (API docs)            | https://nlp-api-6h44.onrender.com/docs |
|

---

## Tabla de contenido

* [1. Autores](#1-autores)
* [2. Objetivos](#2-objetivos)
* [3. Descripción del Proyecto](#3-descripción-del-proyecto)
* [4. Tecnologías](#4-tecnologías)
* [5. Estructura del repositorio](#5-estructura-del-repositorio)
* [6. Datos de Entrada](#6-datos-de-entrada)
* [7. Datos de Salida](#7-datos-de-salida)
* [8. Requisitos](#8-requisitos)
* [9. Instalación](#9-instalación)
* [10. Uso](#10-uso)
* [11. API Endpoints](#11-api-endpoints)
* [12. Docker](#12-docker)
* [13. CI/CD](#13-cicd)
* [14. Origen de Datos](#14-origen-de-datos)
* [15. Datasets](#15-datasets)
* [16. Integración de los Datasets](#16-integración-de-los-datasets)
* [17. Selección del Modelo](#17-selección-del-modelo)
* [18. Pipeline de Entrenamiento del Modelo](#18-pipeline-de-entrenamiento-del-modelo)
* [19. Entrenamiento y Evaluación del Modelo](#19-entrenamiento-y-evaluación-del-modelo)
* [20. Bibliotecas Utilizadas](#20-bibliotecas-utilizadas)
* [21. Referencias](#21-referencias)
* [22. Trabajo Futuro](#22-trabajo-futuro)

---

## 1. Autores

|       Apellidos      |      Nombres    |
| -------------------- | --------------- |
| Rodríguez Valladares | Olga Sarahi.    |

---

## 2. Objetivos

Implementar una API REST que permita identificar lenguaje agresivo en texto mediante un modelo de clasificación de texto basado en la arquitectura RoBERTa al que se le aplicó fine-tuning.

---

## 3. Descripción del Proyecto

El presente proyecto consiste en el desarrollo de un API REST para la clasificación de texto con el objetivo de detectar de lenguaje ofensivo utilizando procesamiento de lenguaje natural (NLP).
Se utilizó el modelo RoBERTuito, un modelo preentrenado en español basado en la arquitectura RoBERTa, al cual se le aplicó fine-tuning utilizando datasets de lenguaje ofensivo en español.

### Arquitectura del API
![Arquitectura del servicio](/resources/arquitectura-api.png) 

---

## 4. Tecnologías

| Componente           | Tecnología               | Justificación                                      |
| -------------------- | ------------------------ | -------------------------------------------------- |
| Lenguaje             | Python 3.10              | Lenguaje ampliamente utilizado en Machine Learning |
| Control de versiones | GitHub                   | Gestión de versiones y control del código          |
| Contenedor           | Docker                   | Permite empaquetar la aplicación                   |
| Backend API          | FastAPI                  | Permite exponer endpoints REST                     |
| NLP                  | HuggingFace Transformers | Fine-tuning y entrenamiento                        |
| Modelo               | RoBERTuito               | Modelo NLP en español                              |

---

## 5. Estructura del la carpeta

nlp-inference-api/
├── app/
│   ├── _init_.py
│   ├── main.py
│   ├── config.py
│   ├── inference.py
│   ├── model_loader.py
│   └── schemas.py
│
├── best_model/
│
├── model_training/
│   └── Fine-tuning_RoBERTuito.ipynb
│
├── resources/
├── .env
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt

- **nlp-inference-api/**: implementa el API REST que realiza el proceso de inferencia del modelo utilizando Fast API para exponer el endpoint.  
- **app**: carpeta donde se almacena la API
  - `__init__.py`: permite que la carpeta app sea tratada como un módulo de Python
  - `main.py`: archivo donde se definen los endpoints del servicio. 
  - `config.py`: archivo de configuración donde se definen las variables globales.
  - `inference.py`: archivo que contiene la lógica de inferencia del modelo.
  - `model_loader.py`: archivo que sirve para cargar el modelo y el tokenizer desde la carpeta best_model o desde Hugging Face Hub.
  - `schemas.py`: define los esquemas de datos JSON utilizando por los datos de entrada y salida del API.
- **best_model/**: almacena el modelo entrenado y los archivos necesarios para realizar la inferencia.
- **model_training/**: almacena los notebooks relacionados al entrenamiento del modelo.
  - `Fine-tuning_RoBERTuito.ipynb`: notebook donde se realiza el proceso de carga, limpieza y preprocesamiento de los necesarios necesarios para el entrenamiento del modelo, asi como la tokenización de los datos, carga y configuración de los parámetros de entrenamiento del modelo y el almacenamiento del mejor modelo en el hub de hugging face para la posterior inferencia dentro del API. 
- `.env`: almacena los tokens de acceso o configuraciones del entorno.
- `.gitignore`: archivo que define los archivos y carpetas que no deben subirse al repositorio.
- `Dockerfile`: contiene la imagen Docker utilizada para desplegar la API.
- `requirements.txt`: lista las dependencias necesarias para ejecutar el backend. 
- **README.md**: documentación del api.

---

## 6. Datos de Entrada

El sistema recibe datos en formato JSON con la siguiente estructura:

* session_id → Identificador de usuario.
* timestamp_id → Tiempo de creación del segmento de audio.
* text → Texto transcrito.
* completed → Bandera para saber si el texto se ha estabilizado.

---

## 7. Datos de Salida

El sistema devuelve un JSON con la clasificación del texto:

* session_id
* timestamp_id
* lexical_score
* lexical_label

---

## 8. Requisitos

* Git
* Python 3.10
* Docker
* pip
* Entorno virtual (venv o conda)

---

## 9. Instalación

### Clonar repositorio

```
git clone https://github.com/Equipo-3004H/Prototipo-SIIA.git
cd Prototipo-SIIA/nlp-inference-api
```

### Instalar dependencias

```
pip install -r requirements.txt
```

### Configurar los variables de entorno


| Variable | Descripción |
|---------|-------------|
| HF_HOME | Directorio donde Hugging Face almacenará el caché de modelos. |
| TRANSFORMERS_CACHE | Directorio donde Transformers guardará los modelos descargados. |
| HF_HUB_DISABLE_SYMLINKS_WARNING | Desactiva advertencias relacionadas con symlinks en Windows. |
| HF_HUB_DOWNLOAD_TIMEOUT | Aumenta el tiempo de espera para descargar archivos grandes del modelo. |

Antes de ejecutar la API, configurar las variables 
```
HF_HOME=C:\Users\usuario\hf_cache
TRANSFORMERS_CACHE=C:\Users\usuario\hf_cache
HF_HUB_DISABLE_SYMLINKS_WARNING=1
HF_HUB_DOWNLOAD_TIMEOUT=600
```

---

## 10. Uso

Ejecutar la API localmente:

```
uvicorn main:app --reload
```

Accesos:

* API local: http://127.0.0.1:8000/
* Swagger: http://127.0.0.1:8000/docs
* ReDoc: http://127.0.0.1:8000/redoc

---

## 12. Docker

### Construir imagen

```
docker build -t nlp-inference-api
```

### Ejecutar contenedor

```
docker run -p 8000:8000 nlp-inference-api
```

Acceder:
http://localhost:8000/docs

---

## 13. CI/CD en Render

El proyecto implementa Integración Continua y Despliegue Continuo utilizando GitHub y Render.

Flujo de despliegue:

1. Push a repositorio GitHub.
2. Render detecta cambios en la rama configurada.
3. Instalación automática de dependencias.
4. Construcción del servicio.
5. Despliegue automático del servicio en la nube.

Esto permite mantener el servicio disponible en una URL pública sin intervención manual.

---

## 14. Origen de Datos
Los conjuntos de datos utilizados para el entrenamiento del modelo de clasificación de lenguaje ofensivo fueron obtenidos desde la plataforma de Hugging Face, la cual proporciona acceso a modelos previamente entrenados y a conjuntos de datos creados y utilizados por la comunidad en tareas de procesamiento del lenguaje natural.

---

## 15. Datasets

* manueltonneau/spanish-hate-speech-superset
* SINAI/OffendES

### Dataset manueltonneau/spanish-hate-speech-superset.
El primer conjunto de datos utilizado en el proceso de entrenamiento fue manueltonneau/spanish-hate-speech-superset, el cual es un superconjunto de datos con 29,855 registros de publicaciones etiquetadas para la detección de discurso de odio (Tonneau, 2024).  
El conjunto de datos cuenta con un subconjunto de entrenamiento, con las siguientes columnas: text, labels, source, dataset, nb_annotators, tweet_id, post_author_country_location. Para el entrenamiento del modelo se conservaron únicamente las columnas text y labels, se eliminaron las demás columnas ya que no aportaban información relevante para el proceso de ajuste fino (fine tuning) del modelo.
 Como parte del preprocesamiento de los datos se reemplazó en la columna text los tokens @USER por la palabra usuario y URL por enlace esto con el fin de facilitar la interpretación del texto. En cuanto a la columna labels se cambió el tipo de dato de float a int ya que el modelo así lo requiere.

### Dataset SINAI/OffendES.
Como complemento al dataset anterior, se utilizó el conjunto de datos SINAI/OffendES, el cual contiene 30,416 publicaciones extraídas de redes sociales y orientadas a la detección de lenguaje ofensivo (SINAI, 2021).  El dataset está dividido en tres subconjuntos los cuales son entrenamiento, validación y pruebas. Los subconjuntos contienen las siguientes columnas comment_id, comment, influencer, influencer_gender, media, label. Para adaptar los datos al formato requerido por el modelo se mapearon los registros de la columna label a una nueva columna nombrada como labels, en la que se asignó el valor O a los registros etiquetados como NO y el valor 1 al resto de los casos. Posteriormente, se eliminaron las columnas comment_id, influencer, influencer_gender, media, label, conservando solamente las columnas comment que se renombro como text junto con la nueva columna labels.

---

## 16. Integración de los Datasets
Una vez fueron preprocesados los conjuntos de datos utilizados para el entrenamiento, fue necesario realizar un proceso de integración y unificación de los datasets para poder utilizarlos de forma conjunta en el proceso de entrenamiento del modelo.
El primer conjunto se dividió en subconjuntos de entrenamiento, prueba y validación. De esta manera se aseguró que ambos conjuntos de datos contaran con la misma estructura. Posteriormente los tres subconjuntos de ambos datasets fueron concatenados entre si según el uso que se les daría en el proceso de entrenamiento del modelo. 

---

## 17. Selección del Modelo
Se seleccionó RoBERTuito un modelo preentrenado en español basado en el modelo RoBERTa. La selección de este modelo se realizó debido a su desempeño en tareas de procesamiento de lenguaje natural, alcanzando puntuaciones altas de macro F1 en comparación a los otros modelos 

---

## 18. Pipeline de Entrenamiento del Modelo
El pipeline incluye:

* Carga de datasets
* Preprocesamiento
* Tokenización
* Entrenamiento
* Evaluación
* Exportación del modelo

![Flujo de entrenamiento](/resources/training.png) 

---

## 19. Entrenamiento y Evaluación del Modelo

Se utilizó la clase trainer de la librería Transformers de Hugging Face, la cual permite ejecutar el proceso de entrenamiento, validación, evaluación y almacenamiento del modelo en el Hub de Hugging Face. Antes del entrenamiento se configuraron los hiperparámetros del modelo. 

| Parámetro | Valor |
|-----------|------|
| Learning rate | 2e-5 |
| Batch size entrenamiento | 16 |
| Batch size validación | 16 |
| Número de épocas | 4 |
| Weight decay | 0.01 |
| Estrategia de evaluación | Por época |
| Estrategia de guardado | Por época |
| Estrategia de logging | Por época |
| Selección del mejor modelo | Basado en F1 |
| Carga del mejor modelo al finalizar | Sí |
| Publicación en Hugging Face | No |
 
En los resultados del entrenamiento se observa que el mejor modelo se obtuvo en la primera época, ya que la pérdida del entrenamiento y validación presentan valores cercanos. Esto se puede comprobar al ejecutar la función trainer.state.best_metric el cual devuelve 0.871749 como la métrica del mejor modelo. 

---

## 20. Bibliotecas Utilizadas en el Entrenamiento


Para la implementación del flujo de entrenamiento, evaluación e inferencia del modelo RoBERTuito se utilizaron diversas bibliotecas de Python especializadas en procesamiento de lenguaje natural, carga de datos, entrenamiento y evaluación de modelos de aprendizaje automático.
Las principales bibliotecas utilizadas forman parte del ecosistema de Hugging Face, el cual proporciona herramientas para tareas de procesamiento del lenguaje natural. 


| Biblioteca	|Uso dentro del notebook de entrenamiento|
|---|--|
|transformers|	Biblioteca del ecosistema de Hugging Face que proporciona APIs para la carga, entrenamiento e inferencia de modelos.|
|huggingface_hub|	Biblioteca del ecosistema de Hugging Face que permite conectarse al hub de Hugging Face para acceder a modelos y datasets.| 
|datasets	|Biblioteca del ecosistema de Hugging Face que permite cargar, almacenar y concatenar datasets y  modelos preentrenados.|
|evaluate|	Es una biblioteca que facilita y estandariza la evaluación y comparación de modelos, así como la elaboración de informes sobre su rendimiento.|
|numpy	|Es una biblioteca de Python que proporciona métodos para realizar operaciones matemáticas.|
|collections	|Es una biblioteca estándar que permite crear un diccionario de una colección para contar los objetos de una columna.|
|pandas|	Permite la manipulación y visualización de datos.|


---

## 21. Referencias

### Modelo

- pysentimiento/robertuito-sentiment-analysis  
  https://huggingface.co/pysentimiento/robertuito-sentiment-analysis

### Datasets

- manueltonneau/spanish-hate-speech-superset  
  https://huggingface.co/datasets/manueltonneau/spanish-hate-speech-superset

- SINAI/OffendES  
  https://huggingface.co/datasets/SINAI/OffendES

### Librerías y documentación

- Hugging Face Transformers Documentation  
  https://huggingface.co/docs/transformers

- FastAPI Documentation  
  https://fastapi.tiangolo.com/

- Docker Documentation  
  https://docs.docker.com/

### Tutoriales utilizados

- Hugging Face Sequence Classification Tutorial  
  https://huggingface.co/docs/transformers/tasks/sequence_classification

---

## 22. Trabajo Futuro

* Mejorar balance de clases
* Implementar monitoreo del modelo
* Versionado de modelos

