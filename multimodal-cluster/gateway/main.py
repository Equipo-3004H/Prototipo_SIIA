import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import redis.asyncio as redis

app = FastAPI(title="Multimodal Gateway")

# Conexión a Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# ---------------------------------------------------------
# LÓGICA DE ESTADO (El "Mapa" del Gateway)
# ---------------------------------------------------------
# Guardaremos las conexiones activas: { client_id: WebSocket }
active_connections: Dict[str, WebSocket] = {}

# Guardaremos qué session_id pertenece a qué client_id: { session_id: client_id }
# Esto permite que cuando el Ensamble termine un session_id, sepamos a qué tubería mandarlo.
session_map: Dict[str, str] = {}

@app.get("/")
async def health_check():
    return {"status": "Gateway Activo", "fase": "2 - Refactorizado"}

# ---------------------------------------------------------
# EL OÍDO CENTRAL (Escucha a Redis todo el tiempo)
# ---------------------------------------------------------
async def central_redis_listener():
    """Esta tarea corre en segundo plano desde que arranca el servidor.
       Escucha TODOS los canales y enruta los mensajes al cliente correcto."""
    pubsub = redis_client.pubsub()
    
    # Escuchamos los canales donde los workers escupen resultados
    await pubsub.subscribe("text_stream", "final_output")
    print("👂 [GATEWAY] Oído central encendido. Escuchando a los workers...")
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    session_id = data.get("session_id")
                    
                    if session_id and session_id in session_map:
                        # Buscamos a quién le pertenece este paquete
                        owner_client_id = session_map[session_id]
                        
                        # Si el dueño sigue conectado, se lo mandamos por su websocket
                        if owner_client_id in active_connections:
                            ws = active_connections[owner_client_id]
                            await ws.send_text(json.dumps(data))
                            
                            # Si el mensaje viene del ensamble (es el veredicto final),
                            # limpiamos el session_map para evitar fugas de memoria.
                            if message["channel"] == "final_output" and data.get("final_score") is not None:
                                print(f"🧹 [GATEWAY] Limpiando sesión completada: {session_id}")
                                del session_map[session_id]
                                
                except json.JSONDecodeError:
                    pass # Ignoramos mensajes corruptos de redis
                except Exception as e:
                     print(f"⚠️ Error al enrutar mensaje de Redis: {e}")
                     
    except asyncio.CancelledError:
        print("🛑 [GATEWAY] Oído central apagado.")
    finally:
        await pubsub.unsubscribe("text_stream", "final_output")

# Arrancamos el oyente central al iniciar FastAPI
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(central_redis_listener())

# ---------------------------------------------------------
# LA TUBERÍA (Endpoints de conexión de los usuarios)
# ---------------------------------------------------------
# Fíjate que ahora la URL pide el {client_id}, NO el session_id
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    
    # Guardamos el WebSocket en el registro de conexiones
    active_connections[client_id] = websocket
    print(f"🟢 [NUEVO USUARIO] Conectado: {client_id}")
    
    try:
        while True:
            # 1. Recibir datos del Frontend
            data = await websocket.receive_text()
            
            try:
                payload = json.loads(data)
                session_id = payload.get("session_id")
                
                if session_id:
                    # 2. El "Registro": Anotamos que este session_id es de este usuario
                    if session_id not in session_map:
                         session_map[session_id] = client_id
                         print(f"📝 [REGISTRO] Sesión {session_id} asignada a -> {client_id}")
                
                # 3. Publicar el audio en Redis para que Whisper lo atrape
                await redis_client.publish("audio_stream", json.dumps(payload))
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Formato inválido"}))

    except WebSocketDisconnect:
        print(f"🔴 [DESCONEXIÓN] Usuario se fue: {client_id}")
        # Limpieza cuando el usuario cierra la pestaña
        if client_id in active_connections:
            del active_connections[client_id]
            
        # Limpiamos todas las sesiones que le pertenecían a ese usuario para no dejar basura
        sessions_to_delete = [s_id for s_id, c_id in session_map.items() if c_id == client_id]
        for s_id in sessions_to_delete:
             del session_map[s_id]