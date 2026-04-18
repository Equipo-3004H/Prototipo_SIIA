import os
import json
import redis
import torch # Importamos PyTorch para validar el hardware
from pysentimiento import create_analyzer

print("⏳ [ROBERTUITO] Inicializando Cerebro Semántico...")

# 👇 NUEVO: Detección estricta de Hardware
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🖥️ [HARDWARE] RoBERTuito ejecutándose en: {device.upper()}")

print("⏳ [ROBERTUITO] Cargando modelo RoBERTa en memoria (esto es instantáneo gracias a la caché de Docker)...")

# 1. Inicialización del Modelo NLP# hate_speech --> se entreno con palabras y races de twitter HatEval Odio real y violencia extrema
# sentiment --> detecta negatividad.
# Usamos la tarea 'hate_speech'/ que está optimizada para detectar agresividad en español
analyzer = create_analyzer(task="sentiment", lang="es", device=device)
print("✅ [ROBERTUITO] Modelo cargado y listo para inferencia.")

# 2. Configuración de la Conexión a Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis_broker") # En Docker será el nombre del servicio Redis
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Conectamos a Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
pubsub = redis_client.pubsub()

# Nos suscribimos ÚNICAMENTE al canal de texto de Whisper
pubsub.subscribe("text_stream")
print("🎧 [ROBERTUITO] Escuchando el canal 'text_stream'...")

# 3. Bucle Principal de Escucha
try:
    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                # Extraemos el JSON crudo enviado por Whisper
                data = json.loads(message["data"])
                
                # 🛑 REGLA HEURÍSTICA: Ignorar transcripciones parciales
                # Si completed no existe o es False, lo descartamos para no perder tiempo de CPU
                if not data.get("completed", False):
                    continue
                
                # Extraemos el texto
                text = data.get("text", "").strip()
                if not text:
                    continue
                
                # 🧠 INFERENCIA: Evaluamos la agresividad del texto
                result = analyzer.predict(text)
                
                # El modelo 'hate_speech' de pysentimiento devuelve probabilidades para:
                # hateful, targeted, y aggressive. Tomaremos la probabilidad de 'aggressive'.
                # result.probas es un diccionario con estas probabilidades.
                # lexical_score = result.probas.get("aggressive", 0.0)

                probs = result.probas                
                lexical_score = probs.get("NEG", 0.0)
                pos_score = probs.get("POS", 0.0)
                neu_score = probs.get("NEU", 0.0)
                
                print(f"📊 [SEMÁNTICA] [{data['session_id']}] NEG: {lexical_score:.4f} | POS: {pos_score:.4f} | NEU: {neu_score:.4f} | Texto: '{text}'")
                
                # 📤 CONTRATO DE SALIDA: Empaquetamos el resultado heredando los metadatos temporales
                output_payload = {
                    "session_id": data["session_id"],
                    "total_chunks": data.get("total_chunks", 0), # 👈 Heredamos la meta del ASR
                    "segment_id": data.get("segment_id", 1),
                    "text": text,
                    "start_time": data.get("start_time", 0.0),
                    "end_time": data.get("end_time", 0.0),
                    "lexical_score": round(lexical_score, 4),
                    # Agregamos las emociones como metadato sin romper el contrato base
                    "sentiment_detail": {
                        "NEG": round(lexical_score, 4),
                        "POS": round(pos_score, 4),
                        "NEU": round(neu_score, 4)
                    }
                }
                
                # Publicamos el veredicto en el canal exclusivo de semántica [cite: 32]
                redis_client.publish("lexical_scores", json.dumps(output_payload))
                
            except json.JSONDecodeError:
                print("⚠️ [ERROR] Paquete recibido no es un JSON válido.")
            except KeyError as e:
                print(f"⚠️ [ERROR] Falta una llave obligatoria en el contrato de datos: {e}")
            except Exception as e:
                print(f"⚠️ [ERROR] Excepción inesperada en la inferencia: {e}")

except KeyboardInterrupt:
    print("🛑 [ROBERTUITO] Apagando de forma segura...")
finally:
    pubsub.close()
    redis_client.close()
