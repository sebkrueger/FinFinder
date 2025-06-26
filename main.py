import streamlit as st
import openai
import os
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI

# Load OpenAI API key on Streamlit Cloud
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    # Check current directory and up to two parent directories for .env
    for path in [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]:
        dotenv_file = path / ".env"
        if dotenv_file.exists():
            load_dotenv(dotenv_file)
            break

client = OpenAI()

# Basic prompt for context
developer_prompt = f"""
# Identität

Du bis ein Chatbot, der auf Basis von gegeben Informationen eines Nutzer, bestimmen sollst um welchen Fisch aus deutschen
Gewässern (Meere, Seen oder Flüsse) es sich handelt. Du sollst zu Erkennung nachfragen stellen, um zwischen noch verbleibenden
Kandidaten unterscheiden zu können.

# Anweisungen

1. Nur Fische in der Liste weiter unten sind als Antwort erlaubt.
2. Ausgabesprache ist deutsch
3. Wenn du nicht ganz genau einen Fisch bestimmen konntest, weisen verbleibende Fischkandidaten immer noch identische Merkmale, stelle Rückfragen an den Nutzer! 
4. Gib als Ergebnis nur den Namen des Fisches aus

# Liste von Fischen

---------------------------
Name: Brassen
Größe: 40cm - 60cm
Gewicht: bis max. 6 kg

Vorkommen: 
    Seen und Teichen: Sie sind in flachen Uferzonen und tiefen Bereichen anzutreffen. 
    Langsam fließenden Flüssen: Sie leben in Flussunterläufen, Altarme und Bereiche mit ruhiger Strömung. 
    Baggerseen und Talsperren: Sie finden hier einen idealen Lebensraum, insbesondere wenn diese über einen starken Pflanzenbestand verfügen. 
    Brackwasser: In den Mündungsgebieten von Flüssen sind sie ebenfalls zu finden.

Verwechselbar mit: Güster, Zobel, Zope
Merkmale: hochrückiger, seitlich stark abgeflachter Körper, Lange Afterflosse, Maul vorstülpbar, graue Färbung, Schwanzflosse stark eingekärbt

----------------------------
Name: Rotauge
Größe: 20cm - 45cm

Vorkommen: 

    Seen: Sie sind häufig in Seen, auch in höheren Lagen (bis zu 1000 m), zu finden. 
    Flüsse: Sie besiedeln auch Flüsse, bevorzugt mittelgroße Flüsse mit nicht zu starker Strömung. 
    Teiche: Auch in Teichen sind sie häufig zu finden. 
    Brackwasser: Sie kommen auch im Brackwasser der Nord- und Ostsee vor. 
    Weitere Gewässer: Rotaugen sind auch in Sumpfgebieten und Altarme zu finden. 


Gewicht: bis max. 2 kg
Verwechselbar mit: Rotfeder, Aland, Güster
Merkmale: hochrückiger, seitlich stark abgeflachter Körper, rote Augeniris, rötliche Flossen, Vorderkante von Rücken und Bauchflossen auf einer Höhe

----------------------------
Name: Dreistachliger Stichling
Größe: 4 cm - 10 cm

Vorkommen: 

    Süßwasser: Der Dreistachlige Stichling findet sich in vielen Binnengewässern, wie Seen, Flüssen und Tümpeln. Er bevorzugt pflanzenreiche Flachwasserzonen. 
    Brackwasser: In Küstenregionen, insbesondere in der Ostsee, ist der Stichling sehr häufig in Brackwassergebieten zu finden, wo Süßwasser und Salzwasser miteinander vermischen. 
    Fließgewässer: Der Dreistachlige Stichling kann auch in langsam fließenden Gewässern leben, zum Beispiel in Altwasserarmen und Flussunterläufen. 
    Salzwasser: Es gibt auch marine Formen des Dreistachligen Stichlings, die in Nord- und Ostsee leben und zur Laichzeit flussaufwärts in Brackwasser ziehen. 

Gewicht: 10-20 Gramm
Verwechselbar mit: Zwergstichling
Merkmale: kleiner, sehr schlanker, seitlich abgeflachter Körper, langer dünner Schwanzstiel, drei Stacheln vor der Rückengflosse, rote Laichfärbung

"""

def get_openai_response(messages):
    try:
        completion = client.chat.completions.create(
            model="gpt-4.1-mini", messages=messages, temperature=0
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"


# Streamlit UI
st.title("Fin Finder - Chatbot 🐟 🐠")
st.write("Welche Merkmale hat dein Fisch? Größe, Farbe, Lebensraum")

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4.1-mini"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "developer", "content": developer_prompt}]

# Display chat messages from history on app rerun
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Beschreibe deinen Fisch (Größe, Farbe, Lebensraum, Schwanzflosse, ...)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})