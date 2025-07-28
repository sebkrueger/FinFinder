# FinFinder

URL of this repository: https://github.com/sebkrueger/FinFinder

**FinFinder** is a language-based chatbot designed to identify and classify fish species found in German waters — 
including both the North Sea and Baltic Sea, as well as inland freshwater habitats. 

The aim is to provide users with a natural language interface to help determine fish species or at 
least categorize them taxonomically.

This project is a **demo application** exploring the integration of various AI and interface technologies.

A first prototype (`FirstPrototype.py`) can be found in the root directory of this repository. 
It features a simple Streamlit-based user interface that allows interaction with the agent via text input.

There will be some test files and tryout of text2speech and speech2text in mainfolder.
There is some test with the langgraph_agent that turns out as a dead-end.

The final version of a running agent will you find in file `FinFinderV3.py`.
---

## 🚀 Installation & Getting Started

Insert into the .env your key for ChatGPT-API and config values based on the .env.template file.

Install all dependencies:   
`pip install scikit-learn`   
`pip install openai`

start the app and use it in the browser:   
`streamlit run FinFinderV3.py`


---

## 🧠 Technologies Used

The project currently uses the following technologies:

- **Streamlit** – Web UI framework for prototyping interactive apps
- **OpenAI GPT models** – Base for natural language processing and fish identification logic
- **text-embedding-3-small** - Convert Userinput and data into embeddings for semantic search
- **cosine_similarity** - Calculate similarity between embeddings for semantic search
- **Coqui** - Neural network for text-to-speech conversion
- **whisper** - Neural network for speech-to-text conversion
- **LangGraph** only for some tests

---

## 📁 Project Structure

```plaintext
FinFinder/
├── FirstPrototype.py                                    # Streamlit-based text input prototype
├── presentation/                                        # Contains pitch deck and future final presentation
│   ├── Chat Fin Finder Pitch 2025-05-15.pdf             # Initial project pitch
│   └── Chat Fin Finder Final 2025-05-15.pdf             # Chat Fin Finder final presentation          
├── README.md                                            # Project description (this file)
├── fishdata                                             # Test scripts to load data form external sources
└── FinFinderV3.py                                       # Streamlit-based text input working agent
