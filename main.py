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
        zeit_str = g["fretigungszeit"].replace(" h", "").strip()
        fertigungszeit_int = int(zeit_str)
        gewicht_str = g["gewicht"].replace(" kg", "").replace(",", ".").strip()
        gewicht_float = float(gewicht_str)

