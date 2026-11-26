import json
import random
import time
import threading
import classes
import msvcrt
import os
import tage_zeit_doku
import ui
import ablauf
from synchronisierung import lock

def lade_daten_aus_json(dateipfad):
    """Lädt Elfen- und Geschenkedaten aus einer JSON-Datei."""
    with open(dateipfad, "r", encoding="utf-8") as f:
        daten = json.load(f)
    return daten

def parse_gewicht(gewicht_str):
    rein = gewicht_str.lower().replace("kg", "").strip().replace(",", ".")
    return float(rein)

letzter_tag = None
letzter_status = None

def main():
    ablauf.modus = "(Normal)"
    daten = lade_daten_aus_json("elfen_geschenke.json")
    
    elfen_roh = daten["elfen"]
    arbeiter_roh = random.sample(elfen_roh, min(3, len(elfen_roh)))
    
    elfen = []
    for e_data in arbeiter_roh:
        elf = classes.elf(
            elf_id=e_data["elf_id"],
            name=e_data["name"],
            fachgebiet=e_data["fachgebiet"].lower(),
            anzahl_produzierter_geschenke=0,
            aktuelles_geschenk=None,
            elf_status="bereit"
        )
        elfen.append(elf)
        
    geschenke_roh = daten["geschenke"]
    ausgewaehlte_roh = random.sample(geschenke_roh, min(15, len(geschenke_roh)))
    
    geschenke = []
    for g_data in ausgewaehlte_roh:
        geschenk = classes.geschenk(
            geschenk_id=int(g_data["geschenk_id"]),
            name=g_data["name"],
            gewicht=parse_gewicht(g_data["gewicht"]),
            kategorie=g_data["kategorie"].lower(),
            geschenk_status="nicht zugewiesen",
            zugewiesener_elf=None,
            fertigungszeit=tage_zeit_doku.parse_zeit(g_data["fertigungszeit"])
        )
        geschenke.append(geschenk)
        
    schlitten = classes.schlitten(max_gewicht=20.0, aktuelles_gewicht=0.0, geladene_geschenke=[])
    
    spiel = classes.spiel(
        aktueller_tag=1,
        max_tag=24,
        geschenke=geschenke,
        elfen=elfen,
        schlitten=schlitten,
        spielstatus="Bereit"
    )
    spiel.initialisiere_spiel()

    # Starte den automatischen Ablauf in einem Hintergrund-Thread
    simulations_thread = threading.Thread(target=ablauf.automatischer_ablauf, args=(spiel,), daemon=True)
    simulations_thread.start()
    
    global letzter_tag
    global letzter_status
    # Hauptschleife für die interaktive Konsolensteuerung
    while spiel.spielstatus not in ["beendet", "Gewonnen"]:
        with lock:
            if spiel.aktueller_tag != letzter_tag or spiel.spielstatus != letzter_status:
                os.system("cls")
                ui.zeige_benutzeroberfläche(spiel)
                letzter_tag = spiel.aktueller_tag
                letzter_status = spiel.spielstatus 

            if msvcrt.kbhit() == True:
                taste = msvcrt.getwch()

                if spiel.spielstatus == "pausiert" and taste.lower() == "v":
                    tage_zeit_doku.tagesprotokoll_anzeigen(spiel)
                    letzter_status = None
                    continue

                try:
                    wahl_int = int(taste)
                    
                    if wahl_int == 1:
                        ablauf.modus = "(Normal)"
                        spiel.spielstatus = "Laeuft (Normal)"
                        letzter_status = None
                        print("\n[INFO] Normaler Modus aktiv: 1 Tag = 1 Minute.")
                    elif wahl_int == 2:
                        spiel.spielstatus = "pausiert"
                        letzter_status = None
                        print("\n[INFO] Spiel pausiert! Die Zeit ist eingefroren.")
                    elif wahl_int == 3:
                        ablauf.modus = "(schnell)"
                        spiel.spielstatus = "Laeuft (schnell)"
                        print("\n[INFO] Schnelldurchlauf aktiv: 1 Tag = 5 Sekunden.")
                        letzter_status = None
                    elif wahl_int == 4:
                        spiel.spielstatus = "beendet"
                        print("\nProgramm wurde beendet. Frohe Weihnachten!")
                        break
                    else:
                        print("\n[FEHLER] Bitte wähle eine Zahl zwischen 1 und 4!")
                    
                    time.sleep(0.8)
                except ValueError:
                    print("\n[FEHLER] Ungültige Eingabe! Bitte gib nur Ziffern von 1 bis 4 ein.")
                    time.sleep(1.0)
                
    time.sleep(0.5)

    # Abschlussmeldung bei Sieg oder Niederlage

    ui.zeige_benutzeroberfläche(spiel)
    if spiel.spielstatus == "Gewonnen":

        print(f"\nGEWONNEN! Alle Geschenke wurden bis zum {tage_zeit_doku.hole_kalender_datum(spiel.aktueller_tag)} ausgeliefert!")
        tage_zeit_doku.tagprot_anz(spiel)


    elif spiel.spielstatus == "beendet" and spiel.aktueller_tag >= spiel.max_tag:
        print("\nZEIT ABGELAUFEN: Nicht alle Geschenke konnten rechtzeitig ausgeliefert werden.")
        tage_zeit_doku.tagprot_anz(spiel)

if __name__ == "__main__":
    main()