import streamlit as st
import pandas as pd
import openai
import os
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

# Setup
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ Kein OpenAI API Key gefunden.")
    st.stop()

client = openai.Client(api_key=api_key)

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

@st.cache_data
def load_data():
    df = pd.read_csv("fishdata/finfinderbasedata.csv")
    df["Beschreibung"] = df.apply(lambda row: f"""
        Lebensraum: {row['Lebensraum']}, 
        Futter: {row['Futter']}, 
        Flossenform: {row['Flossenformen']}, 
        Farbe: {row['Farbe und besondere Farbmerkmale']}, 
        Augenfarbe: {row['Augenfarbe']}, 
        Schuppen: {row['Schuppen']}, 
        Form: {row['Form']}
    """, axis=1)
    return df

@st.cache_data
def generate_embeddings(df):
    embeddings = []
    for beschreibung in df["Beschreibung"]:
        response = client.embeddings.create(
            input=beschreibung,
            model="text-embedding-3-small"
        )
        embeddings.append(response.data[0].embedding)
    df["embedding"] = embeddings
    return df

# Daten vorbereiten
data = generate_embeddings(load_data())

# App-State
if "step" not in st.session_state:
    st.session_state.step = 0
if "antworten" not in st.session_state:
    st.session_state.antworten = {}
if "unsicher" not in st.session_state:
    st.session_state.unsicher = False

# UI
st.title("🐟 FinFinder – V3")

st.markdown("Beantworte ein paar Fragen zum Fisch. Wenn du dir unsicher bist, hilft dir GPT weiter. Am Ende findest du deinen Fische.")

# Reset
if st.button("🔄 Neue Bestimmung starten"):
    st.session_state.step = 0
    st.session_state.antworten = {}
    st.session_state.unsicher = False
    st.rerun()

# Hauptlogik: geführte Auswahl
if st.session_state.step < len(MERKMALE):
    merkmal = MERKMALE[st.session_state.step]
    options = data[merkmal].dropna().unique().tolist()
    if "Ich bin nicht sicher" not in options:
        options.append("Ich bin nicht sicher")

    st.markdown(f"### ❓ {merkmal}")
    frage_prompt = f"""
    Stelle eine einfache Frage an einen Laien zur Erkennung des Merkmals '{merkmal}' 
    basierend auf den möglichen Optionen: {options[:-1]}.
    Füge am Ende immer die Option 'Ich bin nicht sicher' hinzu.
    """
    frage = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Du bist ein hilfsbereiter Fischbestimmungs-Assistent."},
            {"role": "user", "content": frage_prompt}
        ]
    ).choices[0].message.content.strip()
    st.markdown(frage)

    antwort = st.radio("Wähle eine Option:", options, key=f"antwort_{merkmal}")

    if st.button("➡️ Weiter", key=f"weiter_{merkmal}"):
        if antwort == "Ich bin nicht sicher":
            st.session_state.unsicher = True
            st.rerun()
        else:
            st.session_state.antworten[merkmal] = antwort
            st.session_state.step += 1
            st.session_state.unsicher = False
            st.rerun()

    if st.session_state.unsicher:
        hilfe_prompt = f"""
        Ein Nutzer ist unsicher beim Fisch-Merkmal '{merkmal}'.
        Erkläre einfach mit Beispielen und Vergleichen die Unterschiede der Optionen: {options[:-1]}.
        Antworte so, dass er danach entscheiden kann.
        """
        hilfe = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": "Du bist ein geduldiger Fisch-Experte, der Anfängern hilft, "
                                "Fischmerkmale zu verstehen um eine Einordnung des Merkmals passend zu dem "
                                "Fisch vorzunehmen. Halt dich hierbei kurz und beachte immer, dass es sich um "
                                "Fische und Gewässer handelt, die in Deutschland auch vorkommen."},
                {"role": "user", "content": hilfe_prompt}
            ]
        ).choices[0].message.content.strip()

        st.info(hilfe)
        neue_antwort = st.radio("Wähle jetzt erneut:", options[:-1], key=f"erneut_{merkmal}")
        if st.button("✅ Antwort bestätigen", key=f"confirm_{merkmal}"):
            st.session_state.antworten[merkmal] = neue_antwort
            st.session_state.step += 1
            st.session_state.unsicher = False
            st.rerun()

# Wenn fertig: Embedding-Vergleich starten
elif st.session_state.step >= len(MERKMALE):
    st.success("✅ Danke! Ich analysiere deine Angaben und finde die ähnlichsten Fische...")

    # Erstelle Beschreibung aus Antworten
    beschreibung = ", ".join([f"{merkmal}: {antwort}" for merkmal, antwort in st.session_state.antworten.items()])

    # User-Embedding
    response = client.embeddings.create(
        input=beschreibung,
        model="text-embedding-3-small"
    )
    user_embedding = response.data[0].embedding

    # Ähnlichkeit berechnen
    data["similarity"] = data["embedding"].apply(
        lambda x: cosine_similarity([x], [user_embedding])[0][0]
    )

    top_matches = data.sort_values("similarity", ascending=False).head(3)

    st.markdown("### 🎯 Am besten passende Fische:")

    for _, row in top_matches.iterrows():
        st.markdown(f"#### 🐟 {row.get('Name', 'Unbekannter Fisch')}")
        st.markdown(f"**Beschreibung:** {row['Beschreibung']}")
        st.markdown(f"**Ähnlichkeit:** {row['similarity']:.2f}")

        erklär_prompt = f"""
        Ein Nutzer hat diese Beschreibung eines Fisches gegeben: {beschreibung}
        Ein möglicher Treffer ist: {row['Beschreibung']}
        Warum passt dieser Fisch gut zur Nutzerbeschreibung?
        """
        erklärung = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein Fisch-Experte für Anfänger. Erkläre kurz und verständlich."},
                {"role": "user", "content": erklär_prompt}
            ]
        ).choices[0].message.content.strip()

        st.info(erklärung)
