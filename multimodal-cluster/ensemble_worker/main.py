import os
import json
import redis
import time
import threading
from collections import deque

print("🧠 [ENSAMBLE] Inicializando Director de Orquesta Multimodal (Motor Heurístico)...ART_")

# 👇 NUEVO: CONFIGURACIÓN DE LA MATRIZ DE TENSIÓN
WEIGHT_TENSION = 0.30   # 30% de peso a la alteración de la voz
WEIGHT_TEXT = 0.70      # 70% de peso a la gravedad de las palabras
THRESHOLD_AGGRESSIVE = 0.56 

print(f"⚖️ [ENSAMBLE] Pesos configurados -> Tensión Voz: {WEIGHT_TENSION*100}% | Texto: {WEIGHT_TEXT*100}%")

REDIS_HOST = os.getenv("REDIS_HOST", "redis_broker")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
pubsub = redis_client.pubsub()

pubsub.subscribe("acoustic_scores", "lexical_scores")
print("🎧 [ENSAMBLE] Escuchando canales 'acoustic_scores' y 'lexical_scores'... =)")

acoustic_buffer = {} # session_id: { chunk_id: emotions_dict }

def process_fusion(lexical_data):
    """Función que corre en un hilo paralelo por cada frase detectada"""
    session_id = lexical_data.get("session_id")
    total_expected = lexical_data.get("total_chunks", 0) # 👈 NUEVA META

    # 👇 EXTRACCIÓN Y DEFINICIÓN SEGURA DE VARIABLES SEMÁNTICAS 👇
    sentiment_detail = lexical_data.get("sentiment_detail", {})
    # Definimos explícitamente las variables para que estén disponibles en todo el scope del hilo
    texto_neg = float(sentiment_detail.get("NEG", lexical_data.get("lexical_score", 0.0)))
    texto_neu = float(sentiment_detail.get("NEU", 0.0))
    texto_pos = float(sentiment_detail.get("POS", 0.0))
    # 👆 FIN DE LA DEFINICIÓN SEGURA 👆

    print(f"⏳ [ENSAMBLE] [{session_id}] Esperando integridad: {total_expected} segmentos.")
    
    max_retries = 60
    for intento in range(max_retries):
        history = acoustic_buffer.get(session_id, {})
        # Validamos integridad por conteo de llaves únicas
        if len(history) >= total_expected and total_expected > 0:
            print(f"✅ [ENSAMBLE] [{session_id}] Integridad completa ({len(history)}/{total_expected})")
            break
        time.sleep(0.2)

    valid_scores = list(history.values()) # Convertimos dict a lista para promediar igual que antes
        
    # 👇 NUEVO: Promediamos las 4 dimensiones acústicas en lugar de un solo número
    avg_emotions = {"ang": 0.0, "sad": 0.0, "hap": 0.0, "neu": 0.0}
    if valid_scores:
        for em in valid_scores:
            avg_emotions["ang"] += em.get("ang", 0.0)
            avg_emotions["sad"] += em.get("sad", 0.0)
            avg_emotions["hap"] += em.get("hap", 0.0)
            avg_emotions["neu"] += em.get("neu", 0.0)
        
        num_scores = len(valid_scores)
        avg_emotions = {k: v / num_scores for k, v in avg_emotions.items()}
        print(f"✅ [ENSAMBLE] Acústica emparejada para '{session_id}'.")
    else:
        print(f"⚠️ [ENSAMBLE] Tiempo agotado para '{session_id}'. Asumiendo voz en calma.")
        avg_emotions["neu"] = 1.0 # Asumimos voz neutral si no llega nada

    # =======================================================
    #  LA SUPER-HEURÍSTICA MULTIMODAL
    # =======================================================
    is_sarcastic = False
    tension_acustica = 0.0
    final_score = 0.0
    
    voz_ang = avg_emotions["ang"]
    voz_sad = avg_emotions["sad"]
    voz_hap = avg_emotions["hap"]
    voz_neu = avg_emotions["neu"]

    # CAPA 1: DETECTOR DE SARCASMO (BURLA)
    # Se activa si hay palabras tóxicas (>40%) dichas con un tono inusualmente feliz/burlón (>20%)
    if texto_neg > 0.40 and voz_hap > 0.20:
        is_sarcastic = True
        tension_acustica = voz_hap # Usamos la "risa/burla" como el medidor de tensión
        final_score = max(0.65, texto_neg) # Garantizamos que cruce el umbral de peligro
        
    else:
        # CAPA 2: MATRIZ DE TENSIÓN ACÚSTICA (SINTONIZACIÓN FINA)
        # Multiplicamos por 1.8 para que la ira y tristeza penalicen con mayor fuerza
        tension_acustica = (voz_ang + voz_sad) * 1.8
        
        # Bonus si la voz claramente perdió la calma
        if voz_neu < 0.60:
            tension_acustica += 0.15 
            
        tension_acustica = min(tension_acustica, 1.0) # Topamos en 100%
        
        # FUSIÓN FINAL: Texto + Tensión
        final_score = (tension_acustica * WEIGHT_TENSION) + (texto_neg * WEIGHT_TEXT)
        
        # CAPA 3: OVERRIDE POR ATAQUE DE IRA
        # Si el audio acústico es puro enojo, no le creemos a las palabras (ej. grita pero no dice groserías)
        if voz_ang > 0.55:
            final_score = max(final_score, 0.70)
            
    # =======================================================
    
    #  UMBRAL LIGERAMENTE REDUCIDO (De 0.60 a 0.56)
    # Esto salva a los Falsos Negativos pasivo-agresivos (TC05)
    THRESHOLD_AGGRESSIVE = 0.56
    is_aggressive = final_score >= THRESHOLD_AGGRESSIVE

    # =======================================================
    
    # 👇 NUEVO: CONTRATO DE SALIDA ENRIQUECIDO
    output_payload = {
        "session_id": session_id,
        "segment_id": lexical_data.get("segment_id", 1),
        "text": lexical_data.get("text", ""),
        "final_score": round(final_score, 4),
        "is_aggressive": is_aggressive,
        "metadata": {
            "is_sarcastic": is_sarcastic,
            "tension_acustica": round(tension_acustica, 4),
            "lexical_score": round(texto_neg, 4),
            
            # 1. Regla aplicada
            "applied_rule": "Sarcasmo" if is_sarcastic else "Pesos Estándar",
            
            # 2. Desglose Semántico (RoBERTuito)
            "sentiment_detail": {
                "NEG": round(texto_neg, 4),
                "NEU": round(texto_neu, 4),
                "POS": round(texto_pos, 4)
            },
            
            # 3. Desglose Acústico Traducido (Wav2Vec)
            "avg_emotion": {
                "enojo": round(voz_ang, 4),
                "triste": round(voz_sad, 4),
                "feliz": round(voz_hap, 4),
                "neutral": round(voz_neu, 4)
            }
        }
    }
    
    redis_client.publish("final_output", json.dumps(output_payload))
    
    if session_id in acoustic_buffer:
        del acoustic_buffer[session_id]
    
    # Telemetría Visual
    print(f"🎯 [ENSAMBLE FUSIÓN] '{output_payload['text']}'")
    if is_sarcastic:
        print(f"   🎭 SARCASMO DETECTADO -> FINAL: {final_score:.4f}")
    else:
        print(f"   -> Tensión Voz: {tension_acustica:.4f} | Texto (NEG): {texto_neg:.4f} | FINAL: {final_score:.4f}")
        
    if is_aggressive:
        print(f"   🚨 VEREDICTO: HOSTILIDAD DETECTADA")
    else:
        print(f"   ✅ VEREDICTO: SEGURO")

try:
    for message in pubsub.listen():
        if message["type"] == "message":
            channel = message["channel"]
            try:
                data = json.loads(message["data"])
                if channel == "acoustic_scores":
                    session_id = data.get("session_id")
                    cid = data.get("chunk_id") # 👈 Usamos el ID del segmento como llave
                    emotions = data.get("emotions_detail", {})
                    
                    if session_id and cid:
                        if session_id not in acoustic_buffer:
                            acoustic_buffer[session_id] = {} # 👈 Ahora es un dict
                        acoustic_buffer[session_id][cid] = emotions        
                elif channel == "lexical_scores":
                    threading.Thread(target=process_fusion, args=(data,)).start()
                    
            except Exception as e:
                print(f"⚠️ [ERROR] Ensamble: {e}")

except KeyboardInterrupt:
    print("🛑 [ENSAMBLE] Apagando...")
finally:
    pubsub.close()
    redis_client.close()