import pandas as pd
import sys
import os
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, classification_report
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Configuración de Archivos
ARCHIVO_REALES = 'Clasificaciones_reales_220.csv'

print("📊 Iniciando Evaluación Multimodal con Cruce Dinámico...")
print("-" * 80)

# Validamos que el usuario haya pasado el parámetro
if len(sys.argv) < 2:
    print("❌ Error: Debes proporcionar el nombre del archivo de resultados (.txt).")
    print("👉 Ejemplo: python evaluacion_modelo_v3.py \"QA_Resultados.txt\"")
    exit(1)

ARCHIVO_RESULTADOS = sys.argv[1]

# Validar existencia de archivos
if not os.path.exists(ARCHIVO_REALES):
    print(f"❌ Error: No se encontró el archivo maestro '{ARCHIVO_REALES}'.")
    exit(1)

if not os.path.exists(ARCHIVO_RESULTADOS):
    print(f"❌ Error: No se encontró el archivo de pruebas '{ARCHIVO_RESULTADOS}'.")
    exit(1)

# 2. Carga de Datos
try:
    df_reales = pd.read_csv(ARCHIVO_REALES)
    df_predicciones = pd.read_csv(ARCHIVO_RESULTADOS, sep='\t')
except Exception as e:
    print(f"❌ Error al leer los archivos: {e}")
    exit(1)

# ========================================================
# 🧹 NUEVO: LIMPIEZA DE DATOS (DATA CLEANING)
# ========================================================
# 1. Pasamos todas las cabeceras a minúsculas ('Archivo' -> 'archivo')
df_reales.columns = df_reales.columns.str.lower()
df_predicciones.columns = df_predicciones.columns.str.lower()

# 2. Limpiamos comillas ("") y espacios en blanco de las columnas de cruce
df_reales['archivo'] = df_reales['archivo'].astype(str).str.replace('"', '').str.strip()
df_predicciones['archivo'] = df_predicciones['archivo'].astype(str).str.replace('"', '').str.strip()
# ========================================================

# 3. Cruce Inteligente (Inner Join por la columna 'archivo')
df_merged = pd.merge(df_predicciones, df_reales, on='archivo', how='inner')
total_evaluados = len(df_merged)

print(f"📂 Audios en archivo de prueba: {len(df_predicciones)}")
print(f"🔗 Cruce exitoso. Evaluando un total de {total_evaluados} audios coincidentes.")

if total_evaluados == 0:
    print("⚠️ No hay coincidencias entre el .txt y el .csv. Revisa los nombres en la columna 'archivo'.")
    exit(1)

# 4. Reglas de Mapeo (Alineación de Clases)
def mapear_real(valor):
    val = str(valor).strip().lower()
    if val == 'violencia':
        return 'HOSTILIDAD'
    return 'SEGURO' 

def mapear_prediccion(valor):
    val = str(valor).strip().upper()
    if val in ['HOSTILIDAD', 'SARCASMO']:
        return 'HOSTILIDAD'
    return 'SEGURO'

# Aplicamos las reglas al dataframe combinado
y_true = df_merged['clasificaciones reales'].apply(mapear_real)
y_pred = df_merged['veredicto'].apply(mapear_prediccion)

# 5. Cálculo de Métricas
clase_positiva = 'HOSTILIDAD'
etiquetas = ['HOSTILIDAD', 'SEGURO']

acc = accuracy_score(y_true, y_pred)
prec = precision_score(y_true, y_pred, pos_label=clase_positiva, zero_division=0)
rec = recall_score(y_true, y_pred, pos_label=clase_positiva, zero_division=0)
f1 = f1_score(y_true, y_pred, pos_label=clase_positiva, zero_division=0)
cm = confusion_matrix(y_true, y_pred, labels=etiquetas)

# 6. Reporte en Consola
print("\n🎯 MÉTRICAS GLOBALES (Enfocadas en detección de Hostilidad):")
print(f"Exactitud (Accuracy) : {acc * 100:.2f}%")
print(f"Precisión (Precision): {prec * 100:.2f}%")
print(f"Exhaustividad(Recall): {rec * 100:.2f}%")
print(f"Puntaje F1 (F1-Score): {f1 * 100:.2f}%")

print("\n📋 REPORTE DETALLADO POR CLASE:")
print(classification_report(y_true, y_pred, labels=etiquetas, zero_division=0))

# 7. Generación Visual de la Matriz de Confusión
print("\n🎨 Generando gráfico de Matriz de Confusión...")
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Predicción: HOSTILIDAD', 'Predicción: SEGURO'], 
            yticklabels=['Real: HOSTILIDAD', 'Real: SEGURO'],
            annot_kws={"size": 16})

plt.title(f'Matriz de Confusión ({total_evaluados} audios)', fontsize=16, pad=20)
plt.ylabel('Etiqueta Real (Ground Truth)', fontsize=12)
plt.xlabel('Predicción del Modelo (Veredicto)', fontsize=12)

# Nombre dinámico de la imagen
nombre_imagen = f"Matriz_Confusion_{os.path.splitext(os.path.basename(ARCHIVO_RESULTADOS))[0]}.png"
plt.tight_layout()
plt.savefig(nombre_imagen, dpi=300)
print(f"✅ Gráfico guardado exitosamente como '{nombre_imagen}'.")