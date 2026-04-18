import os
import json
import base64
import numpy as np
import redis
import torch
from transformers import Wav2Vec2FeatureExtractor, AutoModelForAudioClassification

print("⏳ [WAV2VEC] Inicializando Oído Emocional...")

# 1. Detección de Hardware
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🖥️ [HARDWARE] Wav2Vec ejecutándose en: {device.upper()}")

# 2. Carga del Modelo (Específico para Emociones - SUPERB Benchmark)
model_name = "superb/wav2vec2-base-superb-er"
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
model = AutoModelForAudioClassification.from_pretrained(model_name).to(device)
print("✅ [WAV2VEC] Modelo acústico cargado y listo.")


# 3. Configuración de Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis_broker")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
pubsub = redis_client.pubsub()
pubsub.subscribe("audio_stream")
print("🎧 [WAV2VEC] Escuchando el canal 'audio_stream'...")

def process_audio(audio_b64):
    # Decodificar y convertir a array de numpy
    audio_bytes = base64.b64decode(audio_b64)
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    
    # Preparar para el modelo (16kHz es el estándar esperado)
    inputs = feature_extractor(audio_np, sampling_rate=16000, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        logits = model(**inputs).logits
    
    # Obtener probabilidades (Softmax)
    scores = torch.nn.functional.softmax(logits, dim=-1)
    
    # El modelo 'ehcalabres' tiene etiquetas como: angry, calm, disgust, fear, happy, neutral, sad, surprise
    # Mapearemos 'angry' (enojo) y 'fear' (tensión) como nuestro puntaje de agresividad acústica
    labels = model.config.id2label
    probs = {labels[i]: scores[0][i].item() for i in range(len(labels))}
    
    # Calculamos el acoustic_score basándonos en 'angry'
    #return probs.get("ang", 0.0)
    return probs

# 4. Bucle Principal
try:
    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                data = json.loads(message["data"])
                
                # REGLA: Wav2Vec analiza bloques de audio, no espera a 'completed'
                # ya que trabaja en paralelo con Whisper [cite: 35]
                audio_b64 = data.get("audio_b64")
                if not audio_b64:
                    continue
                
                # 1. Recibimos el diccionario completo con las 4 emociones
                emotions_dict = process_audio(audio_b64)
                
                # 2. Extraemos el enojo para nuestra variable principal
                acoustic_score = emotions_dict.get("ang", 0.0)
                
                # 📤 CONTRATO DE SALIDA ENRIQUECIDO
                output_payload = {
                    "session_id": data["session_id"],
                    "chunk_id": data.get("chunk_id"),       # 👈 Propagamos ID
                    "total_chunks": data.get("total_chunks", 0), # 👈 Propagamos Meta
                    "timestamp": data["timestamp"], 
                    "acoustic_score": round(float(acoustic_score), 4),
                    # Agregamos las 4 emociones como metadatos adicionales sin romper el contrato base
                    "emotions_detail": {k: round(float(v), 4) for k, v in emotions_dict.items()} 
                }
                
                redis_client.publish("acoustic_scores", json.dumps(output_payload))
                
                # 👇 NUEVA TELEMETRÍA MULTI-EMOCIÓN
                neu = emotions_dict.get("neu", 0.0)
                hap = emotions_dict.get("hap", 0.0)
                sad = emotions_dict.get("sad", 0.0)
                
                print(f"📊 [ACÚSTICA] [{data['session_id']}] Enojo: {acoustic_score:.4f} | Neutral: {neu:.4f} | Feliz: {hap:.4f} | Triste: {sad:.4f}")
                
                if acoustic_score > 0.5:
                    print(f"🔊 [ACÚSTICO] ¡Alerta! Tensión detectada: {acoustic_score:.4f}")
                
            except Exception as e:
                print(f"⚠️ [ERROR] Error procesando acústica: {e}")

except KeyboardInterrupt:
    print("🛑 [WAV2VEC] Apagando...")
finally:
    pubsub.close()
    redis_client.close()