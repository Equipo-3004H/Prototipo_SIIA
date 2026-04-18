import os
import json
import base64
import numpy as np
import redis
import ctranslate2  # Usamos la librería nativa de Faster-Whisper para la detección de hardware
from faster_whisper import WhisperModel

REDIS_HOST = os.getenv("REDIS_HOST", "redis_broker")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# 👇 NUEVO: Detección ultra-ligera de Hardware sin usar PyTorch
if ctranslate2.get_cuda_device_count() > 0:
    hardware_device = "cuda"
    comp_type = "float16" # Máxima velocidad en GPU
else:
    hardware_device = "cpu"
    comp_type = "int8"    # Máxima compresión para sobrevivir en CPU

print(f"🖥️ [HARDWARE] ASR Worker ejecutándose en: {hardware_device.upper()} con precisión {comp_type}")
print("🧠 Cargando modelo Whisper... Esto puede tardar un minuto la primera vez.")

# Usamos el modelo "small" (rápido y preciso).
# Cargamos el modelo inyectando las variables dinámicas
model = WhisperModel("small", device=hardware_device, compute_type=comp_type)

print("✅ Modelo cargado exitosamente en memoria.")

pubsub = redis_client.pubsub()
pubsub.subscribe("audio_stream")

print("🎧 ASR Worker escuchando audio en tiempo real...")

for message in pubsub.listen():
    if message["type"] == "message":
        try:
            payload = json.loads(message["data"])
            b64_audio = payload.get("audio_b64")
            session_id = payload.get("session_id", "unknown")

            if b64_audio:
                # 1. Decodificar Base64 a bytes binarios (Int16)
                audio_bytes = base64.b64decode(b64_audio)
                
                # 2. Convertir a Array Numérico (Whisper requiere Float32 entre -1.0 y 1.0)
                audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
                audio_float32 = audio_int16.astype(np.float32) / 32768.0

                # 3. Inferencia (Magia de IA)
                segments, info = model.transcribe(
						  audio_float32, 
						  beam_size=1, # Disminuir los hilos de pensamiento, entre mas alto busca mas caminos de decisión.
						  language="es",
						  condition_on_previous_text=False, # Evita que se quede en bucle repitiendo palabras
						  no_speech_threshold=0.4, # Tolerancia al silencio para VAD. Probabilidad de que sea ruido, default es 0.6 mas bajo es mas estricto
						  temperature=0.0, # Prohibe que el modelo adivine
						  vad_filter=True, # Activa el VAD del propio modelo de Fast-Whisper
						  vad_parameters=dict(
						  	threshold=0.5, # Exige el 50% de probabilidad de que sea voz, default es 0.3.
						  	min_speech_duration_ms=250 #Ignora ruidos cortos, golpes al micrófono o respiraciones fuertes. 
						  )
						  #initial_prompt="A continuación, una transcripción de voz:" #para resetar el contexto.
						  )
                text = "".join([segment.text for segment in segments]).strip()
                
                if text:
                    # Capturamos si el frontend dijo que era final o parcial (por defecto True por si acaso)
                    is_final_flag = payload.get("is_final", True) 
                    
                    # Imprimimos diferente en la consola para que tú lo notes
                    if is_final_flag:
                        print(f"✅ FINAL [{session_id}]: {text}")
                    else:
                        print(f"⏳ PARCIAL [{session_id}]: {text}")
                    
                    # 4. Publicar la respuesta en Redis incluyendo el flag

                    base_time = payload.get("timestamp", 0.0)

                    result_payload = {
                        "session_id": session_id,
                        "text": text,
                        "total_chunks": payload.get("total_chunks", 0), # 👈 Propagamos la meta

                        # -- LLAVES PARA EL FRONTEND (Legacy) --
                        "timestamp": base_time,
                        "is_final": is_final_flag, 

                        # -- LLAVES PARA ROBERTUITO (Contrato Fase 4) --
                        "completed": is_final_flag,             # RoBERTuito lee esto
                        "segment_id": 1,                        # Mock numérico
                        "start_time": base_time,                # Hereda el timestamp
                        "end_time": base_time + 1.0             # Estimación de ventana

                    }
                    redis_client.publish("text_stream", json.dumps(result_payload))
                    
        except Exception as e:
            print(f"❌ Error procesando audio: {e}")