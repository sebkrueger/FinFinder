# fisch_wizard.py
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()
llm = ChatOpenAI(model="gpt-4", temperature=0.3)

st.set_page_config(page_title="Fischbestimmung", page_icon="🐟")
st.title("🐟 Fischbestimmungs-Assistent")

# 🧠 Alle Schritte definieren
steps = [
    ("environment", "Beschreibe die Umgebung, in der du den Fisch gefunden hast (Ort, Gewässertyp, Tiefe, etc.)"),
    ("catch_info", "Wie wurde der Fisch gefangen? (Angeltyp, Köder, Technik)"),
    ("dimensions", "Wie groß ist der Fisch? (Länge, Gewicht, Breite, etc.)"),
    ("fins", "Beschreibe die Flossen: Anzahl, Form, Position"),
    ("color_and_features", "Welche Farben oder besonderen Merkmale hat der Fisch?")
]

# 🗂️ Session State initialisieren
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
    st.session_state.answers = {}
    st.session_state.dialog_history = []

# 🔁 Validierungsfunktion
def validate_input(step_name, user_input):
    prompt = f"""
Du hilfst einem Angler bei der Fischbeschreibung. Aktueller Schritt: "{step_name}".

Eingabe:
\"\"\"{user_input}\"\"\"

Beantworte:
1. Ist diese Beschreibung ausreichend für diesen Schritt? (Ja/Nein)
2. Wenn Nein, gib eine konkrete Rückfrage oder Verbesserungsvorschlag.

Antwortformat:
OK: Ja/Nein
Feedback: [konkrete Rückfrage]
"""
    result = llm([HumanMessage(content=prompt)]).content
    lines = result.splitlines()
    ok_line = next((l for l in lines if "OK:" in l), "")
    feedback_line = next((l for l in lines if "Feedback:" in l), "")
    ok = "ja" in ok_line.lower()
    feedback = feedback_line.replace("Feedback:", "").strip()
    return ok, feedback

# 🚦 Aktueller Schritt
step_key, step_prompt = steps[st.session_state.current_step]
st.header(f"Schritt {st.session_state.current_step + 1} von {len(steps)}")
st.subheader(step_prompt)

# Eingabefeld
user_reply = st.chat_input("Deine Beschreibung hier...")

# Zeige bisherigen Verlauf
for role, msg in st.session_state.dialog_history:
    with st.chat_message(role):
        st.markdown(msg)

# Bearbeite neue Eingabe
if user_reply:
    st.session_state.dialog_history.append(("user", user_reply))
    ok, feedback = validate_input(step_prompt, user_reply)
    if ok:
        st.session_state.answers[step_key] = user_reply
        st.session_state.dialog_history.append(("assistant", "✅ Danke, das reicht für diesen Schritt."))
        st.session_state.current_step += 1
        st.session_state.dialog_history = []  # Reset dialog for next step
    else:
        st.session_state.dialog_history.append(("assistant", f"❗ Unklar: {feedback}"))

# ⏭️ Skip-Button
if st.button("Schritt überspringen"):
    st.session_state.answers[step_key] = None
    st.session_state.dialog_history = []
    st.session_state.current_step += 1

# 🏁 Finale Ausgabe
if st.session_state.current_step >= len(steps):
    st.success("✅ Alle Schritte abgeschlossen!")
    st.subheader("🔍 Bestimme die Fischart...")

    full_prompt = "\n".join([
        f"{label}: {st.session_state.answers.get(key, 'Nicht angegeben')}"
        for key, label in steps
    ])

    identify_prompt = f"""
Du bist ein Fisch-Experte. Bestimme anhand folgender Daten die Fischart:

{full_prompt}
"""
    result = llm([HumanMessage(content=identify_prompt)])
    st.markdown("**Identifizierter Fisch:**")
    st.markdown(result.content)

    # Zurücksetzen
    if st.button("🔄 Neue Bestimmung starten"):
        st.session_state.current_step = 0
        st.session_state.answers = {}
        st.session_state.dialog_history = []
