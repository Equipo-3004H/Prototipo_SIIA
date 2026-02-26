# Prototipo académico para el monitoreo y detección de lenguaje agresivo multimodal para prevenir el maltrato a Adultos Mayores.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![HuggingFace](https://img.shields.io/badge/huggingface-%23FFD21E.svg?style=for-the-badge&logo=huggingface&logoColor=white)

<p>
Este repositorio forma parte del trabajo 
"Monitoreo y detección de lenguaje agresivo multimodal para prevenir el maltrato a Adultos Mayores." del Equipo 3004H para la asignatura de Seminario de Innovación en Inteligencia Artificial (SIIA) de la Maestría en Inteligencia Artificial de UNIR México.<br> El trabajo tiene como objetivo desarrollar una herramienta tecnológica basada en Inteligencia Artificial (IA) para monitorizar y prevenir el maltrato psicológico hacia el adulto mayor, facilitando un envejecimiento saludable de los mismos. <br>
La solución propuesta capturará conversaciones, transcribirá el audio a texto y detectará agresiones mediante un enfoque multimodal: análisis de la tonalidad en el audio y análisis semántico del texto.  
</p>

````
DEMO técnico del prototipo
Frontend: https://prototipo-siia-9elu.onrender.com/ 
Backend Api: https://prototipo-siia.onrender.com`

````
<!-- Swagger del Backend: https://prototipo-siia.onrender.com/docs -->
<!-- Documentacion tecnica del Backend: https://prototipo-siia.onrender.com/docs -->

## Tabla de contenido

- [1. Autores](#1-autores)
- [2. Objetivos](#2-objetivos)
- [3. Características](#3-caracteristicas)
- [4. Arquitectura](#4-arquitectura-del-sistema)
- [5. Tecnologías](#5-tecnologías)
- [6. Estructura del repositorio](#6-estructura-del-repositorio)
- [7. Requisitos](#7-requisitos)
- [8. Instalación](#8-instalación)
- [9. Uso](#9-uso)
- [10. Datasets](#10-datasets)

### 1. Autores

| Apellidos            | Nombres         |
| -------------------- | --------------- |
| Martínez Cruz        | Luis Arturo.    |
| Rentería Ramírez     | Mariana Jazmín. |
| Rodríguez Valladares | Olga Sarahi.    |

### 2. Objetivos

El objetivo principal es implementar una solución de IA que realice análisis de tonalidades en voz y clasificación de texto para identificar lenguaje agresivo de forma automática.

Los objetivos específicos de la solución de IA son:

- Capturar y transcribir conversaciones de dos personas casi en tiempo real.
  - Mantener una latencia de máximo 500ms.
  - Mantener una Word Error Rate de entre 0 y15%.
- Analizar el audio para clasificar tonalidades de agresividad en la voz.
- Analizar el texto para clasificación de palabras agresivas.
- Combinar ambos análisis bajo un ensamble para determinar la presencia de lenguaje agresivo.
- Obtener métricas de F1 Score en los modelos de clasificación y ensamble iguales o mayores a 0.85, dando prioridad al recall para minimizar los falso negativos; es decir:
  - Valores de recall y precisiones superiores a 0.85
  - Mayor prioridad a valores de recall alto vs precisión.
- Desarrollar un prototipo mínimo viable (MVP) con los puntos anteriores.

### 3. Características

- Capturar audio de forma estable.
- Generar y almacenar correctamente los archivos creados.
- Transcribir conversaciones, mostrar el texto en pantalla y almacenarlo en un archivo.
- Realizar análisis prosódico (volumen y tonos agresivos) del audio y mostrar una señal visual en pantalla cuando detecte patrones agresivos.
- Identificar palabras agresivas en la transcripción y resaltarlas al mostrar en pantalla.
- Mostrar en pantalla los resultados integrados de los modelos prosódico y léxico.

### 4. Arquitectura del sistema

<!-- ![Diagrama de la solución](/resources/diagrama_solucion.png) -->


### 5. Tecnologías

Se utiliza Python como lenguaje de programación.

Frontend

| Herramienta/librería | Version | Uso dentro del proyecto |
| -------------------- | --------------- | --------------- |
|   streamlit       | 1.54.0 |     |
|         |   | 
|  |    |
 

Backend

| Herramienta/librería | Version | Uso dentro del proyecto |
| -------------------- | --------------- | --------------- |
| Fastapi        |0.128.0| Exposición de endpoints Rest del backend   |
| uvicorn     | 0.40.0 | Ejecuta la api como servidor web
|  |    |
 

### 6. Estructura del repositorio
<p>El proyecto se divide en dos carpetas principales Frontend (Cliente) y Backend (Servidor)  </p>

<!-- Front -->

<!-- Back -->
<!-- 195 ├, 192 └  ── -->
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

- **prototipo-client/**: contiene la aplicación cliente encargada de la captura de audio y visualización de resultados.
- **prototipo-api/**: implementa el backend del sistema utilizando FastAPI para exponer los servicios del proyecto.  
  - `main.py`: punto de entrada donde se definen los endpoints del servicio.  
  - `.python-version`: especifica la versión de Python utilizada en el entorno.  
  - `requirements.txt`: lista las dependencias necesarias para ejecutar el backend.
- **resources/**: almacena archivos estáticos como diagramas e imágenes del proyecto.
- **README.md**: documentación principal del repositorio.

### 7. Requisitos

<!-- Que programas necesito para levantar el repo  -->

### 8. Instalación

#### 8.1 Clonar repositorio 
Para clonar el repositorio de manera local se utiliza el siguiente código:

````bash
git clone https://github.com/Equipo-3004H/Prototipo-SIIA.git 
cd Prototipo-SIIA
````
#### 8.2 Instalar dependencias 



### 9. Uso

<!-- Como se puede levantar el repo -->
<!-- Front -->
<!-- Back -->

### 10. Datasets

<!-- para entrenamiento -->
<!--  -->

### 11. Estado del proyecto

Actualmente el prototipo académico se encuentra en fase de desarrollo.
