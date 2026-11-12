import classes
import json
import time
import random

def lade_daten():
    with open("elfen_geschenke.json", "r", encoding="utf-8") as file:
        elfen_geschenke = json.load(file)

    elfen_objekte = []
    for e in elfen_geschenke["elfen"]:
        neuer_elf = classes.Elf(
            elf_id = e ["elf_id"],
            name = e ["name"],
            fachgebiet = e ["fachgebiet"],
            anzahl_produzierter_geschenke = 0,
            aktuelles_geschenk = None,
            elf_status = "bereit"
        )
        elfen_objekte.append(neuer_elf)

    geschenke_objekte = []
    for g in elfen_geschenke["geschenke"]:
        zeit_str = g["fertigungszeit"].replace(" h", "").strip()
        fertigungszeit_int = int(zeit_str)
        gewicht_str = g["gewicht"].replace(" kg", "").replace(",", ".").strip()
        gewicht_float = float(gewicht_str)

        neues_geschenk = classes.Geschenk(
            geschenk_id = g["geschenk_id"],
            name = g["name"],
            kategorie = g["kategorie"],
            geschenk_status = "nicht zugewisen",
            zugewiesener_elf = None,
            fertigungszeit = fertigungszeit_int
        )
        geschenke_objekte.append(neues_geschenk)
    
    return elfen_objekte, geschenke_objekte


if __name__ == "__main__":
    alle_elfen, alle_geschenke = lade_daten()
    santas_schlitten = classes.Schlitten(max_gewicht=20.0, aktuelles_gewicht=0.0, geladene_geschenke=[])
    
    spiel = classes.Spiel(
        aktueller_tag=1,
        max_tag=24,
        geschenke=alle_geschenke,
        elfen=alle_elfen,
        schlitten=santas_schlitten,
        spielstatus="gestartet"
    )
    
    spiel.initialisiere_spiel()

    print("--- SANTA'S WEIHNACHTSWERKSTATT-MANAGER ---")
    print(f"Spiel gestartet! Tag {spiel.aktueller_tag} von {spiel.max_tag}.")