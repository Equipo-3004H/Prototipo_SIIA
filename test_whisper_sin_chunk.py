import os
import json
import time
import base64
import redis
import threading

# 1. Configuración
REDIS_HOST = "localhost"
REDIS_PORT = 6379
AUDIO_DIR = "./qa_audios_asr225"

print("👂 Iniciando Protocolo de QA: Inyector de Bloque Único y Telemetría")
print("-" * 100)

# 2. Conexión a Redis
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.ping()
    pubsub = r.pubsub()
    # ✅ Escuchamos los canales CORRECTOS
    # text_stream: donde publica Whisper (asr_worker)
    # final_output: donde publica el Ensamble (ensemble_worker)
    pubsub.subscribe("final_output", "text_stream") 
except Exception as e:
    print(f"❌ Error conectando a Redis: {e}")
    exit(1)

# 3. Base de Datos Temporal de Telemetría
qa_sessions = {}
report_data = []
report_lock = threading.Lock()

# 4. El "Motor" de Escucha (Corre en paralelo)
def escuchar_respuestas():
    global qa_sessions, report_data
    
    print("🎧 Escuchador de Veredictos Iniciado...")
    try:
        for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    channel = message["channel"]
                    session_id = data.get("session_id")
                    
                    if not session_id or session_id not in qa_sessions:
                        continue

                    # 4A. Whisper nos avisa que terminó el texto (Para Latencia de Transcripción)
                    # ✅ Whisper usa el canal 'text_stream' y manda la bandera 'completed'
                    if channel == "text_stream" and data.get("completed"):
                        if qa_sessions[session_id]["ts_transcripcion"] == 0:
                             qa_sessions[session_id]["ts_transcripcion"] = int(time.time() * 1000)
                             
                    # 4B. El Ensamble manda el veredicto final
                    # ✅ El Ensamble usa el canal 'final_output' y manda 'final_score'
                    if channel == "final_output" and "final_score" in data:
                        ts_ensamble = int(time.time() * 1000)
                        meta = data.get("metadata", {})
                        
                        # Armamos el Veredicto
                        veredicto = "SEGURO"
                        if data.get("is_aggressive"):
                            veredicto = "SARCASMO" if meta.get("is_sarcastic") else "HOSTILIDAD"

                        # Calculamos las latencias reales
                        ts_start = qa_sessions[session_id]["start_time"]
                        ts_trans = qa_sessions[session_id]["ts_transcripcion"] or ts_ensamble
                        
                        lat_trans = ts_trans - ts_start
                        lat_ens = ts_ensamble - ts_start

                        avg_emo = meta.get("avg_emotion", {})
                        sent_det = meta.get("sentiment_detail", {})

                        # Construimos el "Récord" asegurando tipos numéricos correctos
                        record = {
                            "archivo": qa_sessions[session_id]["file_name"],
                            "session_id": session_id,
                            "texto_transcrito": data.get("text", ""),
                            "riesgo_final": round(float(data.get("final_score", 0.0)), 4),
                            "veredicto": veredicto,
                            "tension_voz_usada": round(float(meta.get("tension_acustica", 0.0)), 4),
                            "negatividad_texto_usada": round(float(meta.get("lexical_score", 0.0)), 4),
                            "heuristica_aplicada": str(meta.get("applied_rule", "Desconocida")),
                            "roberta_NEG": round(float(sent_det.get("NEG", 0.0)), 4),
                            "roberta_NEU": round(float(sent_det.get("NEU", 0.0)), 4),
                            "roberta_POS": round(float(sent_det.get("POS", 0.0)), 4),
                            "wav2vec_enojo": round(float(avg_emo.get("enojo", 0.0)), 4),
                            "wav2vec_tristeza": round(float(avg_emo.get("triste", 0.0)), 4),
                            "wav2vec_felicidad": round(float(avg_emo.get("feliz", 0.0)), 4),
                            "wav2vec_neutral": round(float(avg_emo.get("neutral", 0.0)), 4),
                            "latencia_transcripcion_ms": lat_trans,
                            "latencia_ensamble_ms": lat_ens
                        }

                        with report_lock:
                            report_data.append(record)
                            print(f"✅ [{session_id}] Veredicto recibido: {veredicto} ({record['riesgo_final']})")
                        
                        # Marcamos como completado para destrabar el inyector
                        qa_sessions[session_id]["completado"] = True
                
                except Exception as inner_e:
                    print(f"⚠️ [ERROR INTERNO] No se pudo procesar el mensaje del canal {channel}: {inner_e}")
                    
    except Exception as e:
        print(f"❌ [ERROR FATAL] El escuchador de Redis ha fallado: {e}")

# Arrancamos el hilo de escucha
listener_thread = threading.Thread(target=escuchar_respuestas, daemon=True)
listener_thread.start()


# 5. La Lógica de Inyección (Bloque Único)
def procesar_audios():
    global qa_sessions

    if not os.path.exists(AUDIO_DIR):
        print(f"⚠️  Directorio {AUDIO_DIR} no encontrado.")
        return

    archivos_wav = [f for f in os.listdir(AUDIO_DIR) if f.endswith(".wav")]
    archivos_wav.sort()
    print(f"📂 Se encontraron {len(archivos_wav)} audios para procesar.")

    for archivo in archivos_wav:
        filepath = os.path.join(AUDIO_DIR, archivo)
        session_id = f"qa_{archivo.split('.')[0]}"
        
        print(f"\n🚀 Inyectando (Bloque Único): {archivo}...")
        
        qa_sessions[session_id] = {
            "file_name": archivo,
            "start_time": int(time.time() * 1000),
            "ts_transcripcion": 0,
            "completado": False
        }

        # Abrimos TODO el audio de golpe
        with open(filepath, "rb") as audio_file:
            audio_b64 = base64.b64encode(audio_file.read()).decode('utf-8')
            
        # Cumplimos el contrato de metadatos, declarando que es 1 solo bloque
        payload = {
            "session_id": session_id,
            "chunk_id": 1,
            "total_chunks": 1,
            "timestamp": time.time(),
            "is_final": True,
            "audio_b64": audio_b64
        }
        
        r.publish("audio_stream", json.dumps(payload))
        
        # Esperamos la respuesta antes de inyectar el siguiente
        timeout_seconds = 90
        start_wait = time.time()
        
        while not qa_sessions[session_id]["completado"]:
            if time.time() - start_wait > timeout_seconds:
                print(f"⚠️ Timeout en {archivo} ({timeout_seconds}s sin respuesta). Saltando...")
                break
            time.sleep(0.5)

    # 6. Generación del Archivo de Reporte
    print("\n" + "=" * 50)
    print("📡 Todos los audios inyectados. Generando Reporte...")
    generar_txt()

def generar_txt():
    if not report_data:
        print("⚠️ No hay datos para guardar en el reporte.")
        return
        
    filename = f"QA_Resultados_Python_Bloque_{int(time.time()*1000)}.txt"
    
    headers = [
        "archivo", "session_id", "texto_transcrito", "riesgo_final", "veredicto",
        "tension_voz_usada", "negatividad_texto_usada", "heuristica_aplicada",
        "roberta_NEG", "roberta_NEU", "roberta_POS", 
        "wav2vec_enojo", "wav2vec_tristeza", "wav2vec_felicidad", "wav2vec_neutral",
        "latencia_transcripcion_ms", "latencia_ensamble_ms"
    ]
    
    with open(filename, "w", encoding="utf-8") as f:
        # Escribir cabecera separada por Tabs (\t)
        f.write("\t".join(headers) + "\n")
        
        for rec in report_data:
            row = [str(rec.get(h, "")) for h in headers]
            f.write("\t".join(row) + "\n")
            
    print(f"✅ Reporte guardado exitosamente: {filename}")


if __name__ == "__main__":
    procesar_audios()