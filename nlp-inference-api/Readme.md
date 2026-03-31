# API REST de Clasificación de Texto Utilizando RoBERTuito.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![HuggingFace](https://img.shields.io/badge/huggingface-%23FFD21E.svg?style=for-the-badge&logo=huggingface&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/docker-0db7ed?style=for-the-badge&logo=docker&logoColor=white)
![Transformers](https://img.shields.io/badge/Transformers-ffcc00?style=for-the-badge)
![NLP](https://img.shields.io/badge/NLP-Natural%20Language%20Processing-blue?style=for-the-badge)

### DEMO técnico del prototipo desplegado en Render
|Componente|Url|
|--|--|
|Swagger (API docs)|https://prototipo-siia.onrender.com/docs|
|Documentación técnica (ReDoc)|https://prototipo-siia.onrender.com/|


## Tabla de contenido

- [1. Autores](#1-autores)
- [2. Objetivos](#2-objetivos)
- [3. Descripción del Proyecto](#3-descripción-del-proyecto)
- [4. Tecnologías](#4-tecnologías)
- [5. Estructura del repositorio](#5-estructura-del-repositorio)
- [6. Datos de Entrada](#6-datos-de-entrada)
- [7. Datos de Salida](#7-datos-de-salida)
- [8. Requisitos](#8-requisitos)
- [9. Instalación](#9-instalación)
- [10. Uso](#10-uso)
- [11. API Endpoints](#11-api-endpoints)
- [12. Docker](#12-docker)
- [13. CI/CD](#13-cicd)
- [14. Origen de Datos](#14-origen-de-datos)
- [15. Datasets](#15-datasets)
- [16. Integración de los Datasets](#16-integración-de-los-datasets)
- [17. Selección del Modelo](#17-selección-del-modelo)
- [18. Pipeline de Entrenamiento del Modelo](#18-pipeline-de-entrenamiento-del-modelo)
- [19. Entrenamiento y Evaluación del Modelo](#19-entrenamiento-y-evaluación-del-modelo)
- [20. Bibliotecas Utilizadas](#20-bibliotecas-utilizadas)
- [21. Resultados](#21-resultados)
- [22. Trabajo Futuro](#22-trabajo-futuro)

### 1. Autores

| Apellidos            | Nombres         |
| -------------------- | --------------- |
| Rodríguez Valladares | Olga Sarahi.    |

### 2. Objetivos

Implementar API que permita identificar lenguaje agresivo en texto mediante un modelo de clasificación de texto basado en la arquitectura RoBERTa al que se le aplico fine-tuning.


## 3. Descripción del Proyecto

## 4. Tecnologías

Componente	Tecnología	Justificación 
Lenguaje 	Python 3.10	Lenguaje ampliamente consolidado en el ámbito del aprendizaje automático. 
Control de versiones	GitHub	Gestión de versiones, control del código fuente y trazabilidad del desarrollo del proyecto.
Contenedor	Docker	Permite el empaquetado de aplicaciones en contenedores ligeros y aislados del sistema operativo.
Backend API	FastAPI	Framework que permite exponer web API y endpoints API REST para inferencia sobre modelos entrenados.


Para la implementación del flujo de entrenamiento, evaluación e inferencia del modelo RoBERTuito se utilizaron diversas bibliotecas de Python especializadas en procesamiento de lenguaje natural, carga de datos, entrenamiento y evaluación de modelos de aprendizaje automático. Estas bibliotecas se utilizaron para la implementación del pipeline de entrenamiento del modelo descrito en la  Figura 19.
Las principales bibliotecas utilizadas forman parte del ecosistema de Hugging Face, el cual proporciona herramientas para tareas de procesamiento del lenguaje natural. La biblioteca transformes se utilizó para realizar el proceso de fine-tuning del modelo RoBERTuito, incluyendo la carga del modelo, la tokenización de los datos, configuración de los hiperparámetros de entrenamiento y el entrenamiento del modelo. La biblioteca huggingface_hub permitió la autenticación mediante un token generado en la cuenta del usuario, con el fin de acceder al dataset spanish-hate-speech-superset, el cual requiere la aceptación de condiciones de uso debido a la enorme cantidad de contenido de odio que se encuentra presente en el conjunto de datos. La biblioteca datasets se utilizó para la carga, procesamiento, transformación de los conjuntos de datos y la división en subconjuntos de entrenamiento, validación y pruebas.
Además de las bibliotecas del ecosistema de Hugging Face se utilizaron otras bibliotecas. La biblioteca evaluate se utilizó para evaluar el rendimiento del modelo utilizando F1-Score como la métrica principal durante el proceso de entrenamiento y validación. La biblioteca NumPy se utilizó en operaciones numéricas y manipulación de datos. La biblioteca Pandas se utilizó para la visualización de los conjuntos de datos. La biblioteca collections se utilizó para el análisis de la distribución de las clases de los datasets, con el objetivo de detectar problemas de desbalance de clases. 


## 5. Estructura del repositorio
```
Repositorio

├── prototipo-client/
|   ├──app.py
|   ├──.python-version
|   └──requirements.txt
|
├── prototipo-api/
|   ├──main.py
|   ├──.python-version
|   └──requirements.txt
|
├── README.md
└── resources
```
- **prototipo-api/**: implementa el backend del sistema utilizando FastAPI para exponer los servicios del proyecto.  
  - `main.py`: punto de entrada donde se definen los endpoints del servicio.  
  - `.python-version`: especifica la versión de Python utilizada en el entorno.  
  - `requirements.txt`: lista las dependencias necesarias para ejecutar el backend.
- **resources/**: almacena archivos estáticos como diagramas e imágenes del proyecto.
- **README.md**: documentación principal del repositorio.

## 6. Datos de Entrada

RoBERTuito obtiene del canal text_stream de Redis la transcripción que publico Whisper en el JSON de control. Los datos en formato JSON son los siguientes:
session_id  Identificador de usuario.
timestamp_id  Tiempo de creación del segmento de audio.
text  texto transcrito.
completed  bandera para saber si el texto se ha estabilizado. Si esto es False, RoBERTuito lo descarta.
Nota: timestamp_id debe mantenerse como referencia para que el resultado de RoBERTuito pueda ser relacionado con el de Wav2Vec y Ensamble Multimodal pueda relacionar ambas ponderaciones para su clasificación y cálculo final.

## 7. Datos de Salida
RoBERTuito solo tiene comunicación con Redis al publicar su resultado en el canal lexical_score. El formato del JSON con la probabilidad estadística del texto tendrá los siguientes datos:
session_id  Identificador de usuario.
timestamp_id  Tiempo de creación del segmento de audio.
lexical_score  Probabilidad de la etiqueta de sentimiento identificada.
lexical_label  Etiqueta del sentimiento.

## 8. Requisitos
- Git bash / Git Desktop
- Python 3.9
- Entorno virtual (venv o conda)
- Visual Studio Code o terminal

## 9. Instalación

#### 8.1 Clonar repositorio 
Para clonar el repositorio de manera local se utiliza el siguiente código:

````bash
git clone https://github.com/Equipo-3004H/Prototipo-SIIA.git 
cd Prototipo-SIIA
````

#### 8.2 Crear entorno virtual

```
python -m venv venv
source venv/bin/activate   # mac/linux
venv\Scripts\activate      # windows
```


#### 8.3 Instalar dependencias 

Tanto el frontend como el backend cuentan con un archivo `requirements` el cual contiene todas las dependencias necesarias para levantar cada solución 

````
pip install -r requirements.txt
````

## 10. Uso

## 11. API Endpoints
Para levantar el repositorio del backend se ejecuta el siguiente comando en la terminal 

<!-- #fastapi dev main.py -->

``` 
uvicorn main:app --reload
```
Accesos:
- Api local: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 12. Docker

## 13. CI/CD
El proyecto implementa Integracion Continua, Despliegie Continuo (CI/CD) utilizando GitHub y Rendeer.
Se utiliza un modelo de despliegue automatico, donde cada actualizacion en la rama configurada activa el proceso de construccion y publicacion de los servicios web para frontend y backend.

Flujo de despliegue
1. Push a repositorio GitHub.
2. Render detecta cambios en la rama configurada.
3. Instalación automática de dependencias.
4. Construcción del servicio.
5. Despliegue automático del servicio en la nube.

Esto permite mantener el prototipo disponible en una URL publica sin intervención manual.



## 14. Origen de Datos
Los conjuntos de datos utilizados para el entrenamiento del modelo de clasificación de lenguaje ofensivo fueron obtenidos desde la plataforma de Hugging Face, la cual proporciona acceso a modelos previamente entrenados y a conjuntos de datos creados y utilizados por la comunidad en tareas de procesamiento del lenguaje natural. Asimismo, se utilizó la librería Transformers de Hugging Face, ya que permite gestionar la carga de los datos, el entrenamiento y evaluación de los modelos basados en arquitecturas Transformers.
Para el entrenamiento del modelo se seleccionaron los conjuntos de datos en español manueltonneau/spanish-hate-speech-superset y SINAI/OffendES, con el objetivo de aumentar la diversidad de ejemplos para mejorar la capacidad de detección del modelo. Durante el preprocesamiento, los datos fueron adaptados al formato requerido por el tokenizador y el modelo.

## 15. Datasets
### Dataset manueltonneau/spanish-hate-speech-superset.
El primer conjunto de datos utilizado en el proceso de entrenamiento fue manueltonneau/spanish-hate-speech-superset, el cual es un superconjunto de datos con 29,855 registros de publicaciones etiquetadas para la detección de discurso de odio (Tonneau, 2024).  Este conjunto fusiona varios datasets documentados en español. Este conjunto de datos aporta diversidad de ejemplos relacionados con ataques, discriminación y expresiones peyorativas presentes en comentarios de redes sociales.
El conjunto de datos cuenta únicamente con un subconjunto de entrenamiento, con las siguientes columnas: text, labels, source, dataset, nb_annotators, tweet_id, post_author_country_location. Para el entrenamiento del modelo se conservaron únicamente las columnas text y labels, se eliminaron las demás columnas ya que no aportaban información relevante para el proceso de ajuste fino (fine tuning) del modelo.
 Como parte del preprocesamiento de los datos se reemplazó en la columna text los tokens @USER por la palabra usuario y URL por enlace esto con el fin de facilitar la interpretación del texto. En cuanto a la columna labels se cambió el tipo de dato de float a int ya que el modelo así lo requiere.

### Dataset SINAI/OffendES.
Como complemento al dataset anterior, se utilizó el conjunto de datos SINAI/OffendES, el cual contiene 30,416 publicaciones extraídas de redes sociales y orientadas a la detección de lenguaje ofensivo (SINAI, 2021).  El dataset está dividido en tres subconjuntos los cuales son entrenamiento, validación y pruebas. Los subconjuntos contienen las siguientes columnas comment_id, comment, influencer, influencer_gender, media, label. Para adaptar los datos al formato requerido por el modelo se mapearon los registros de la columna label a una nueva columna nombrada como labels, en la que se asignó el valor O a los registros etiquetados como NO y el valor 1 al resto de los casos. Posteriormente, se eliminaron las columnas comment_id, influencer, influencer_gender, media, label, conservando solamente las columnas comment que se renombro como text junto con la nueva columna labels.

## 16. Integración de los Datasets
Una vez descritos los conjuntos de datos utilizados para el entrenamiento, fue necesario realizar un proceso de integración y unificación de los datasets para poder utilizarlos de forma conjunta en el proceso de entrenamiento del modelo.
El primer conjunto se dividió en subconjuntos de entrenamiento, prueba y validación. De esta manera se aseguró que ambos conjuntos de datos contaran con la misma estructura. Posteriormente los tres subconjuntos de ambos datasets fueron concatenados entre si según el uso que se les daría en el proceso de entrenamiento del modelo. Esta estrategia permitió disponer de conjuntos de datos más amplios y con mayor diversidad de ejemplos de lenguaje ofensivo, mejorando la capacidad de generalización del modelo durante el entrenamiento. 
Los conjuntos de datos concatenados presentaban un desbalance en la clase labels la cual contiene las etiquetas de maltrato, siendo el maltrato positivo una tercera parte de los datos, este desbalance podría afectar el ajuste fino del modelo.

## 17. Selección del Modelo
Después de preparar e integrar los conjuntos de datos, se procedió a la selección del modelo de clasificación de texto que sería utilizado en el proceso de ajuste fino (fine-tuning).
Se seleccionó RoBERTuito un modelo preentrenado en español basado en el modelo RoBERTa. La selección de este modelo se realizó debido a su desempeño en tareas de procesamiento de lenguaje natural, alcanzando puntuaciones altas de macro F1 en comparación a los otros modelos 


## 18. Pipeline de Entrenamiento del Modelo
El entrenamiento del modelo es un proceso compuesto de diferentes etapas, las cuales incluyen la carga de los conjuntos de datos, el preprocesamiento de los datos, la integración de los subconjuntos de datos, la tokenización de los datos, la inicialización del modelo, la configuración de los argumentos del entrenamiento, así como el entrenamiento y evaluación del modelo como se muestra en la Figura 19.

## 19. Entrenamiento y Evaluación del Modelo
Una vez seleccionado el modelo RoBERTuito, se procedió a realizar el proceso de entrenamiento y evaluación del modelo utilizando los conjuntos de datos previamente preparados e integrados.
Se utilizó la clase trainer de la librería Transformers de Hugging Face, la cual permite ejecutar el proceso de entrenamiento, validación, evaluación y almacenamiento del modelo tanto local como en la nube. Antes del entrenamiento se configuraron los hiperparámetros del modelo. La tasa de aprendizaje se estableció en 2e-5, el tamaño de los lotes de muestras para el entrenamiento y validación se fijó en 16, se utilizó un decaimiento de pesos (weight decay) de 0.01 y el modelo fue entrenado durante cuatro épocas. La evaluación del modelo se realizó al final de cada época, evaluando el F1 score como la métrica principal para determinar el mejor modelo. 
En la Figura 19 se muestran los resultados de las métricas obtenidas en el entrenamiento de cada época. Se observa que el mejor modelo se obtuvo en la primera época, ya que la pérdida del entrenamiento y validación presentan valores cercanos. Esto se puede comprobar al ejecutar la función trainer.state.best_metric el cual devuelve 0.871749 como la métrica del mejor modelo. 

## 20. Bibliotecas Utilizadas

## 21. Referencias 

### Modelos

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

## 22. Trabajo Futuro

