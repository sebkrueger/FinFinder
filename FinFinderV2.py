import streamlit as st
import pandas as pd
import openai
import os
from dotenv import load_dotenv

# 🔐 Load API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ Kein OpenAI API Key gefunden. Bitte setze die Umgebungsvariable OPENAI_API_KEY.")
    st.stop()

client = openai.Client(api_key=api_key)

# 📦 Daten laden
@st.cache_data
def load_data():
    return pd.read_csv("fishdata/finfinderbasedata.csv")

data = load_data()

# 🎯 Merkmale definieren
MERKMALE = [
    "Lebensraum",
    "Futter",
    "Flossenformen",
    "Farbe und besondere Farbmerkmale",
    "Augenfarbe",
    "Schuppen",
    "Form"
]

ERKLAERUNGEN = {
    "bauchständig": "Die Bauchflossen sitzen unter dem Bauch.",
    "torpedoförmig": "Der Körper ist lang und spindelförmig wie ein Torpedo.",
    "oberständig": "Das Maul zeigt schräg nach oben.",
    "unterständig": "Das Maul zeigt nach unten.",
    "endständig": "Das Maul ist vorne am Kopf und zeigt gerade nach vorne."
}

# 🤖 GPT-Frage generieren
def frage_mit_llm(merkmal, werte):
    prompt = f"""
    Du hilfst einem Laien, einen Fisch zu bestimmen. Erkenne das Merkmal \"{merkmal}\".
    Formuliere eine klare, einfach verständliche Frage dazu und gib die folgenden Optionen als Auswahlmöglichkeiten:
    {werte}
    Gib auch eine zusätzliche Auswahl „Ich bin nicht sicher“, damit du Hilfe anbieten kannst.
    Gib die Frage bitte in einer Zeile zurück.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Du bist ein hilfsbereiter Fischbestimmungs-Assistent für Laien in deutschen Gewässern."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# 🧠 Session State initialisieren
if "filtered_data" not in st.session_state:
    st.session_state.filtered_data = data.copy()
if "step" not in st.session_state:
    st.session_state.step = 0
if "unsicher" not in st.session_state:
    st.session_state.unsicher = False

# 🐟 Titel
st.title("🐟 FinFinder – Finde deinen Fisch")
st.markdown("Diese App hilft dir, Fische der Nord- und Ostsee zu bestimmen. Beantworte Fragen, um die Auswahl einzugrenzen.")

# 🔁 Reset-Button
if st.button("🔄 Neue Bestimmung starten"):
    st.session_state.filtered_data = data.copy()
    st.session_state.step = 0
    st.session_state.unsicher = False
    st.rerun()

# ✅ Endzustände
if len(st.session_state.filtered_data) == 1:
    st.success("✅ Ich bin mir sehr sicher: Es handelt sich um diesen Fisch:")
    st.write(st.session_state.filtered_data.iloc[0])
    st.stop()

if len(st.session_state.filtered_data) == 0:
    st.error("❌ Leider passt kein Fisch mehr zu deinen Angaben.")
    st.stop()

# 🧭 Fragefluss
if st.session_state.step < len(MERKMALE):
    merkmal = MERKMALE[st.session_state.step]
    options = st.session_state.filtered_data[merkmal].dropna().unique().tolist()
    if "Ich bin nicht sicher" not in options:
        options.append("Ich bin nicht sicher")

    frage = frage_mit_llm(merkmal, options[:-1])  # ohne "nicht sicher" für die Formulierung

    st.markdown(f"### ❓ Frage {st.session_state.step + 1}")
    st.markdown(f"**{frage}**")

    with st.expander("ℹ️ Was bedeutet das?", expanded=False):
        for begriff, erklaerung in ERKLAERUNGEN.items():
            if begriff.lower() in merkmal.lower():
                st.markdown(f"**{begriff}**: {erklaerung}")

    # 👇 Nur wenn nicht in Unsicherheitsmodus
    if not st.session_state.unsicher:
        antwort = st.radio("Wähle die passende Option:", options, key=f"wahl_{merkmal}_{st.session_state.step}")
        if st.button("✅ Antwort bestätigen", key=f"confirm_{merkmal}_{st.session_state.step}"):
            if antwort == "Ich bin nicht sicher":
                st.session_state.unsicher = True
                st.rerun()
            else:
                st.session_state.filtered_data = st.session_state.filtered_data[
                    st.session_state.filtered_data[merkmal] == antwort
                ]
                st.session_state.step += 1
                st.session_state.unsicher = False
                st.rerun()

    # 💬 Hilfe anzeigen + erneute Auswahl
    if st.session_state.unsicher:
        st.warning("🤔 Kein Problem – ich helfe dir weiter, das Merkmal besser zu verstehen!")

        hilfe_prompt = f"""
        Ein Nutzer ist sich beim Merkmal '{merkmal}' unsicher. Gib eine einfache, interaktive Erklärung,
        damit er sich anschließend besser entscheiden kann. Nutze Vergleiche, Beispiele und einfache Sprache.
        Mögliche Optionen: {options[:-1]}
        """

        hilfe_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": "Du bist ein geduldiger Fisch-Experte, der Anfängern hilft, "
                                "Fischmerkmale zu verstehen um eine Einordnung des Merkmals passend zu dem "
                                "Fisch vorzunehmen. Halt dich hierbei kurz und beachte immer, dass es sich um "
                                "Fische und Gewässer handelt, die in Deutschland auch vorkommen."},
                {"role": "user", "content": hilfe_prompt}
            ]
        )

        st.markdown("### 💡 Interaktive Hilfe:")
        st.info(hilfe_response.choices[0].message.content.strip())

        st.markdown("### ✅ Und jetzt: Wähle nochmal")
        neue_antwort = st.radio("Was trifft am besten zu?", options[:-1], key=f"erneut_{merkmal}_{st.session_state.step}")
        if st.button("➡️ Bestätigen und fortfahren", key=f"erneut_confirm_{merkmal}_{st.session_state.step}"):
            st.session_state.filtered_data = st.session_state.filtered_data[
                st.session_state.filtered_data[merkmal] == neue_antwort
            ]
            st.session_state.step += 1
            st.session_state.unsicher = False
            st.rerun()
else:
    st.info("🔍 Keine weiteren Merkmale mehr – hier ist die eingegrenzte Auswahl:")
    st.dataframe(st.session_state.filtered_data)
