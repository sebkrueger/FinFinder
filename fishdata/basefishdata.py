import pandas as pd

# Daten für 10 Fische (5 Süßwasser, 5 Salzwasser)
fische = [
    {
        "Name": "Aal",
        "Lebensraum": "Süßwasser",
        "Futter": "Raubfisch",
        "Flossenformen": "zusammenhängende Rücken-, Schwanz- und Afterflosse",
        "Farbe und besondere Farbmerkmale": "dunkler Rücken, heller Bauch",
        "Größen (cm)": "40-150",
        "Augenfarbe": "silbrig",
        "Schuppen": "klein, eingebettet",
        "Form": "schlank, schlangenförmig"
    },
    {
        "Name": "Hecht",
        "Lebensraum": "Süßwasser",
        "Futter": "Raubfisch",
        "Flossenformen": "bauchständig, weit hinten",
        "Farbe und besondere Farbmerkmale": "grünlich mit hellen Flecken",
        "Größen (cm)": "40-130",
        "Augenfarbe": "gelblich",
        "Schuppen": "klein, fest",
        "Form": "torpedoförmig"
    },
    {
        "Name": "Karpfen",
        "Lebensraum": "Süßwasser",
        "Futter": "Friedfisch",
        "Flossenformen": "bauchständig",
        "Farbe und besondere Farbmerkmale": "goldbraun, oft dunkler Rücken",
        "Größen (cm)": "30-100",
        "Augenfarbe": "braun",
        "Schuppen": "groß, rund",
        "Form": "breit, rundlich"
    },
    {
        "Name": "Barsch",
        "Lebensraum": "Süßwasser",
        "Futter": "Raubfisch",
        "Flossenformen": "zwei Rückenflossen, erste stachelig",
        "Farbe und besondere Farbmerkmale": "grünlich mit dunklen Querstreifen",
        "Größen (cm)": "15-50",
        "Augenfarbe": "gelb-orange",
        "Schuppen": "rau, mittlere Größe",
        "Form": "kompakt, leicht torpedoförmig"
    },
    {
        "Name": "Zander",
        "Lebensraum": "Süßwasser",
        "Futter": "Raubfisch",
        "Flossenformen": "zwei getrennte Rückenflossen",
        "Farbe und besondere Farbmerkmale": "grau-silbrig mit dunklen Streifen",
        "Größen (cm)": "40-100",
        "Augenfarbe": "glasig",
        "Schuppen": "klein, rau",
        "Form": "langgestreckt, torpedoförmig"
    },
    {
        "Name": "Dorsch (Kabeljau)",
        "Lebensraum": "Salzwasser",
        "Futter": "Raubfisch",
        "Flossenformen": "drei Rückenflossen, zwei Afterflossen",
        "Farbe und besondere Farbmerkmale": "braun mit hellen Flecken",
        "Größen (cm)": "40-150",
        "Augenfarbe": "dunkel",
        "Schuppen": "klein, glatt",
        "Form": "kräftig, torpedoförmig"
    },
    {
        "Name": "Hering",
        "Lebensraum": "Salzwasser",
        "Futter": "Friedfisch",
        "Flossenformen": "bauchständig",
        "Farbe und besondere Farbmerkmale": "silbrig, blau-grüner Rücken",
        "Größen (cm)": "20-38",
        "Augenfarbe": "schwarz",
        "Schuppen": "klein, leicht abfallend",
        "Form": "schlank, seitlich abgeflacht"
    },
    {
        "Name": "Makrele",
        "Lebensraum": "Salzwasser",
        "Futter": "Raubfisch",
        "Flossenformen": "zwei Rückenflossen, mehrere kleine Flössel",
        "Farbe und besondere Farbmerkmale": "blau-grün mit dunklen Streifen",
        "Größen (cm)": "30-60",
        "Augenfarbe": "dunkel",
        "Schuppen": "winzig, fast schuppenlos",
        "Form": "stromlinienförmig, torpedoförmig"
    },
    {
        "Name": "Scholle",
        "Lebensraum": "Salzwasser",
        "Futter": "Friedfisch",
        "Flossenformen": "langer, durchgehender Flossensaum",
        "Farbe und besondere Farbmerkmale": "braun mit orange-roten Punkten",
        "Größen (cm)": "30-70",
        "Augenfarbe": "gelblich",
        "Schuppen": "klein, rau",
        "Form": "flach, asymmetrisch"
    },
    {
        "Name": "Seelachs (Köhler)",
        "Lebensraum": "Salzwasser",
        "Futter": "Raubfisch",
        "Flossenformen": "drei Rückenflossen, zwei Afterflossen",
        "Farbe und besondere Farbmerkmale": "dunkelgrau bis schwarz",
        "Größen (cm)": "50-120",
        "Augenfarbe": "dunkel",
        "Schuppen": "klein, glatt",
        "Form": "schlank, torpedoförmig"
    }
]

# In DataFrame umwandeln
df = pd.DataFrame(fische)

# Datei anzeigen
import ace_tools as tools; tools.display_dataframe_to_user(name="Fischarten Nord- und Ostsee", dataframe=df)

# Als CSV-Datei speichern
csv_path = "/mnt/data/Fischarten_Nord_Ostsee.csv"
df.to_csv(csv_path, index=False)

csv_path
