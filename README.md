# Prototipo academico para el monitoreo y detección de lenguaje agresivo multimodal para prevenir el maltrato a Adultos Mayores.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![HuggingFace](https://img.shields.io/badge/huggingface-%23FFD21E.svg?style=for-the-badge&logo=huggingface&logoColor=white)

<p>
Este repositorio forma parte del trabajo 
"Monitoreo y detección de lenguaje agresivo multimodal para prevenir el maltrato a Adultos Mayores." del Equipo 3004H para la asignatura de Seminario de Innovación en Inteligencia Artificial (SIIA) de la Maestria en Inteligencia Artificial de UNIR México.<br> El trabajo tiene como objetivo desarrollar una herramienta tecnológica basada en Inteligencia Artificial (IA) para monitorizar y prevenir el maltrato psicológico hacia el adulto mayor, facilitando un envejecimiento saludable de los mismos. <br>
La solución propuesta capturará conversaciones, transcribirá el audio a texto y detectará agresiones mediante un enfoque multimodal: análisis de la tonalidad en el audio y análisis semántico del texto.  
</p>

<!-- TODO: DEMO LINK AL DEMO -->

## Tabla de contenido

- [1. Autores](#1-autores)
- [2. Objetivos](#2-objetivos)
- [3. Carácteristicas](#3-caracteristicas)
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

El objetivo principal es implementar una solución de IA que realice análisis de tonalidades en voz y clasificación de texto para identificar leguaje agresivo de forma automática.

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

### 3. Carácteristicas

- Capturar audio de forma estable.
- Generar y almacenar correctamente los archivos creados.
- Transcribir conversaciones, mostrar el texto en pantalla y almacenarlo en un archivo.
- Rrealizar análisis prosódico (volumen y tonos agresivos) del audio y mostrar una señal visual en pantalla cuando detecte patrones agresivos.
- Identificar palabras agresivas en la transcripción y resaltarlas al mostrar en pantalla.
- Mostrar en pantalla los resultados inntegrados de los modelos prosódico y léxico.

### 4. Arquitectura del sistema

![Diagrama de la solucion](/resources/diagrama_solucion.png)

### 5. Tecnologías

Se utiliza Python como lenguaje de programación.

- Whisper
- Scikit learn

<!-- Explicar -->

### 6. Estructura del repositorio

<!-- Front -->
<!-- Back -->

### 7. Requisitos

<!-- Que programas necesito para levantar el repo  -->

### 8. Instalación

<!-- Que necesito instarlar para  -->
<!-- Front -->
<!-- Back -->

### 9. Uso

<!-- Como se puede levantar el repo -->
<!-- Front -->
<!-- Back -->

### 10. Datasets

<!-- para entrenamiento -->
<!--  -->

### 11. Estado del proyecto

Actualmente el prototipo academico se encuentra en fase de desarrollo.
