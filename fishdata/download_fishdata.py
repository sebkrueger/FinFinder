import requests
import pandas as pd
from tqdm import tqdm

# Funktion: Daten aus FishBase REST API holen
def fetch_data(endpoint, params=None):
    base_url = "http://fishbase.ropensci.org/"
    url = f"{base_url}{endpoint}"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Fehler bei {endpoint}")
        return []

# Schritt 1: Alle Fische, die in Deutschland vorkommen (Nord- & Ostsee)
occurrences = fetch_data("occurrence", params={"Country": "Germany"})
species_list = list({entry["Species"] for entry in occurrences if entry.get("Species")})

print(f"{len(species_list)} Arten in deutschen Gewässern gefunden.")

# Schritt 2: Hole Daten aus verschiedenen Tabellen
species_data = []
for sp in tqdm(species_list, desc="Lade FishBase-Daten"):
    sp_clean = sp.replace(" ", "%20")
    s_data = fetch_data(f"species/{sp_clean}")
    m_data = fetch_data(f"morphdat/{sp_clean}")
    e_data = fetch_data(f"ecology/{sp_clean}")
    c_data = fetch_data(f"comnames/{sp_clean}")

    # Deutsche Namen filtern
    german_name = next((c["ComName"] for c in c_data if c["Language"] == "German"), None)

    row = {
        "ScientificName": sp,
        "GermanName": german_name,
        "MaxLength": s_data[0]["Length"] if s_data else None,
        "MouthForm": m_data[0]["MouthPosition"] if m_data else None,
        "DorsalFins": m_data[0].get("Dorsalsoft", None) if m_data else None,
        "FeedingType": e_data[0].get("FoodTroph", None) if e_data else None,
        "Environment": s_data[0].get("Fresh", "") + s_data[0].get("Brack", "") + s_data[0].get("Saltwater", "")
    }
    species_data.append(row)

# Schritt 3: Speichern
df = pd.DataFrame(species_data)
df.to_csv("nord_ostsee_fische_fishbase.csv", index=False)
print("✅ CSV gespeichert als 'nord_ostsee_fische_fishbase.csv'")
