import streamlit as st
import whisper
import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile

# Titel
st.title("🎤 Whisper Speech-to-Text (lokal)")
st.write("Sprich ins Mikrofon – Whisper transkribiert den Text offline.")

# Whisper-Modell laden (cache für Performance)
@st.cache_resource
def load_model():
    return whisper.load_model("base")  # Alternativen: tiny, small, medium, large

model = load_model()

# Config how long to record
duration = st.slider("Aufnahmedauer (Sekunden)", 3, 20, 5)

if st.button("🎙️ Aufnahme starten"):
    st.info("Aufnahme läuft...")
    fs = 16000  # Whisper bevorzugt 16 kHz
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()

    # Save as local temp wave file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        scipy.io.wavfile.write(f.name, fs, (audio * 32767).astype(np.int16))
        audio_path = f.name

    st.success("✅ Aufnahme abgeschlossen. Transkribiere...")

    # transcribe audio with whisper
    result = model.transcribe(audio_path, language="de")  # language is optional it will autodetect
    st.subheader("📝 Transkribierter Text:")
    st.text_area("Ergebnis:", result["text"])
