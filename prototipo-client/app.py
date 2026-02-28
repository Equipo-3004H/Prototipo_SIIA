import streamlit as st

st.header("Monitoreo y detección de lenguaje agresivo", divider=True) 

audio_value = st.audio_input("De click para empezar a grabar.")

if audio_value:
    st.audio(audio_value)