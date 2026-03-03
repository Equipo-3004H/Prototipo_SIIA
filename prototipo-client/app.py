import av
import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration

st.header("Monitoreo y detección de lenguaje agresivo", divider=True) 

# Configuración de STUN/TURN para WebRTC en producción
rtc_configuration = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# Control de volumen para el audio
volume = st.slider("Volumen", 0.0, 2.0, 1.0, 0.1)

def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
    # Aplicar el control de volumen a los samples de audio
    samples = frame.to_ndarray()
    samples = (volume * samples).astype(samples.dtype)  # type: ignore

    # Crear un nuevo marco de audio con los samples modificados
    new_frame = av.AudioFrame.from_ndarray(samples, layout=frame.layout.name)
    new_frame.sample_rate = frame.sample_rate
    return new_frame

# Iniciar el streamer de audio con la función de callback para procesar los frames de audio
webrtc_streamer(
    key="audio",
    rtc_configuration=rtc_configuration,
    audio_frame_callback=audio_frame_callback,
    media_stream_constraints={"video": False, "audio": True},
)