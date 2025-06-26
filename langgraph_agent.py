from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional

import os
from dotenv import load_dotenv

load_dotenv()

# 1. State Definition
class FishState(TypedDict):
    environment: Optional[str]
    catch_info: Optional[str]
    dimensions: Optional[str]
    fins: Optional[str]
    color_and_features: Optional[str]
    final_result: Optional[str]

# 2. LLM Initialisierung
llm = ChatOpenAI(model="gpt-4", temperature=0.3)

# 3. Einzelne Knoten (Steps)
def ask_environment(state):
    msg = "Bitte beschreibe die Umgebung, in der du den Fisch gefunden hast  z.B. Ort, Gewässertyp, Tiefe."
    return {"environment": input(msg)}  # oder LLM-gestützt

def ask_catch_info(state):
    msg = "Bitte gib Informationen zum Fang z.B. mit welchen Köder oder Angeltyp du den Fang hattest."
    return {"catch_info": input(msg)}

def ask_dimensions(state):
    msg = "Wie groß ist der Fisch? Länge, Breite, ggf. Gewicht?"
    return {"dimensions": input(msg)}

def ask_fins(state):
    msg = "Beschreibe die Flossenstellung und Anzahl der Flossen."
    return {"fins": input(msg)}

def ask_color_features(state):
    msg = "Welche Farben, Muster oder besonderen Merkmale hat der Fisch?"
    return {"color_and_features": input(msg)}

def identify_fish(state):
    prompt = f"""
Du bist ein Fisch-Experte. Bestimme anhand folgender Daten die Fischart:

Umgebung: {state['environment']}
Fanginfo: {state['catch_info']}
Maße: {state['dimensions']}
Flossen: {state['fins']}
Merkmale: {state['color_and_features']}
"""
    response = llm([HumanMessage(content=prompt)])
    return {"final_result": response.content}

# 4. Graph definieren
builder = StateGraph(FishState)

builder.add_node("step_environment", ask_environment)
builder.add_node("step_catch_info", ask_catch_info)
builder.add_node("step_dimensions", ask_dimensions)
builder.add_node("step_fins", ask_fins)
builder.add_node("step_color_and_features", ask_color_features)
builder.add_node("step_identify", identify_fish)

# Verbindungen definieren
builder.set_entry_point("step_environment")
builder.add_edge("step_environment", "step_catch_info")
builder.add_edge("step_catch_info", "step_dimensions")
builder.add_edge("step_dimensions", "step_fins")
builder.add_edge("step_fins", "step_color_and_features")
builder.add_edge("step_color_and_features", "step_identify")
builder.add_edge("step_identify", END)

# 5. Graph bauen
graph = builder.compile()


# Initial empty state
initial_state: FishState = {
    "environment": None,
    "catch_info": None,
    "dimensions": None,
    "fins": None,
    "color_and_features": None,
    "final_result": None
}

result = graph.invoke(initial_state)
print("Identifizierter Fisch:")
print(result["final_result"])