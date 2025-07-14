import streamlit as st
import pandas as pd
import openai
import os

from dotenv import load_dotenv

load_dotenv()

# Load OpenAI API key on Streamlit Cloud
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ Kein OpenAI API Key gefunden. Bitte setze die Umgebungsvariable OPENAI_API_KEY.")
    st.stop()

client = openai.Client(api_key=api_key)

# CSV laden
@st.cache_data
def load_data():
    return pd.read_csv("fishdata/finfinderbasedata.csv")

data = load_data()

# Alle Merkmale, die wir abfragen wollen
MERKMALE = [
    "Lebensraum",
    "Futter",
    "Flossenformen",
    "Farbe und besondere Farbmerkmale",
    "Augenfarbe",
    "Schuppen",
    "Form"
]

# Fachbegriffe einfach erklärt (kann erweitert werden)
ERKLAERUNGEN = {
    "bauchständig": "Die Bauchflossen sitzen unter dem Bauch.",
    "torpedoförmig": "Der Körper ist lang und spindelförmig wie ein Torpedo.",
    "oberständig": "Das Maul zeigt schräg nach oben.",
    "unterständig": "Das Maul zeigt nach unten.",
    "endständig": "Das Maul ist vorne am Kopf und zeigt gerade nach vorne."
}

# GPT-4: Frage generieren lassen
def frage_mit_llm(merkmal, werte):
    prompt = f"""
    Du hilfst einem Laien, einen Fisch zu bestimmen. Erkenne das Merkmal \"{merkmal}\".
    Formuliere eine klare, einfach verständliche Frage dazu und gib die folgenden Optionen als Auswahlmöglichkeiten:
    {werte}
    Gib die Frage in einer Zeile zurück.
    
    Gib bitte auch eine Auswahl zurück, die der Nutzer auswählen kann, wenn er nicht sicher ist, 
    damit du dann hilfe anbieten kannst um die Frage doch beantworten zu können.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Du bist ein hilfsbereiter Fischbestimmungs-Assistent "
                                          "für Fischen in deutschen Gewässern."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# Session State initialisieren
if "filtered_data" not in st.session_state:
    st.session_state.filtered_data = data.copy()
if "step" not in st.session_state:
    st.session_state.step = 0

# Titel
st.title("🐟 FinFinder – Finde deinen Fisch")
st.markdown("""
Diese App hilft dir dabei, Fische der Nord- und Ostsee zu bestimmen.
Beantworte Fragen zu Merkmalen deines beobachteten Fisches, und der Agent grenzt die Auswahl ein.
""")

# Neue Bestimmung starten
if st.button("🔄 Neue Bestimmung starten"):
    st.session_state.filtered_data = data.copy()
    st.session_state.step = 0
    st.rerun()

# Wenn nur noch ein Fisch übrig ist
if len(st.session_state.filtered_data) == 1:
    st.success("✅ Ich bin mir sehr sicher: Es handelt sich um diesen Fisch:")
    st.write(st.session_state.filtered_data.iloc[0])
    st.stop()

# Wenn kein Fisch übrig ist
if len(st.session_state.filtered_data) == 0:
    st.error("❌ Leider passt kein Fisch mehr zu deinen Angaben.")
    st.stop()

# Nächste Frage stellen
if st.session_state.step < len(MERKMALE):
    merkmal = MERKMALE[st.session_state.step]
    options = st.session_state.filtered_data[merkmal].dropna().unique().tolist()
    options.append("Ich bin nicht sicher")

    # GPT-4 formuliert die Frage
    frage = frage_mit_llm(merkmal, options)

    st.subheader(f"Frage {st.session_state.step + 1}")
    st.markdown(frage)

    with st.expander("Was bedeutet das?"):
        for begriff, erklaerung in ERKLAERUNGEN.items():
            if begriff.lower() in merkmal.lower():
                st.markdown(f"**{begriff}**: {erklaerung}")

    antwort = st.radio("Wähle die passende Option:", options)

    if st.button("Antwort bestätigen"):
        if antwort == "Ich bin nicht sicher":
            st.warning("Kein Problem – ich helfe dir weiter, das Merkmal besser zu verstehen!")

            hilfe_prompt = f"""
            Der Nutzer ist sich beim Merkmal '{merkmal}' unsicher. Gib eine einfache, interaktive Erklärung,
            die hilft, sich zu entscheiden. Nutze Beispiele, Bilder (symbolisch), Vergleiche oder Fragen.
            Mache es so, dass der Nutzer danach nochmal eine fundierte Wahl treffen kann. 
            Optionen: {options[:-1]}
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

            st.markdown("💬 **Interaktive Hilfe:**")
            st.info(hilfe_response.choices[0].message.content.strip())

            st.stop()  # Nutzer soll nach Hilfe nochmal bewusst wählen
        else:
            st.session_state.filtered_data = st.session_state.filtered_data[
                st.session_state.filtered_data[merkmal] == antwort
                ]
            st.session_state.step += 1
            st.rerun()

else:
    st.info("🔍 Keine weiteren Merkmale mehr – hier ist die eingegrenzte Auswahl:")
    st.dataframe(st.session_state.filtered_data)
