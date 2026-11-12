import json
import random
import time
import calendar
from classes import Geschenk, Elf, Schlitten, Spiel

def lade_daten_aus_json(dateipfad):
# lädt elfen, geschenk dateien aus json 
    with open(dateipfad, "r", encoding="utf-8") as f:
        daten = json.load(f)
    return daten

def parse_gewicht(gewicht_str):
# ändert string "2.5kg" zu float 2.5
    rein = gewicht_str.lower().replace("kg", "").strip().replace(",", ".")
    return float(rein)

def parse_zeit(zeit_str):
# ändert string "24h" zu float 24.0
    rein = zeit_str.lower().replace("h", "").strip().replace(",", ".")
    return float(rein)

def hole_kalender_datum(tag):
# Dezember 2026 Tage von 1 bis 24
    wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
# Kalender (jahre, monat, tag) -> wochentag als index
    wochentag_idx = calendar.weekday(2026, 12, tag)
    return f"{wochentage[wochentag_idx]}, {tag}. Dezember 2026"

def main():
# json Daten laden
    daten = lade_daten_aus_json("elfen_geschenke.json")
    
# Elfen initialisieren
    elfen = []
    for e_data in daten["elfen"]:
        elf = Elf(
            elf_id=e_data["elf_id"],
            name=e_data["name"],
            fachgebiet=e_data["fachgebiet"].lower(),
            anzahl_produzierter_geschenke=0,
            aktuelles_geschenk=None,
            elf_status="bereit"
        )
        elfen.append(elf)
        
# geschenke aus json Liste auswählen
    geschenke_roh = daten["geschenke"]
    ausgewaehlte_roh = random.sample(geschenke_roh, min(15, len(geschenke_roh)))
    
    geschenke = []
    for g_data in ausgewaehlte_roh:
        g_id = int(g_data["geschenk_id"])
        name = g_data["name"]
        kategorie = g_data["kategorie"].lower()
        fertigungszeit = parse_zeit(g_data["fertigungszeit"])
        gewicht = parse_gewicht(g_data["gewicht"])
        
        geschenk = Geschenk(
            geschenk_id=g_id,
            name=name,
            gewicht=gewicht,
            kategorie=kategorie,
            geschenk_status="nicht zugewiesen",
            zugewiesener_elf=None,
            fertigungszeit=fertigungszeit
        )
        geschenke.append(geschenk)
        
# Schlitten erstellen (Maximalgewicht z. B. 35.0 kg)[cite: 6]
    schlitten = Schlitten(max_gewicht=35.0, aktuelles_gewicht=0.0, geladene_geschenke=[])
    
# Spiel-Instanz erstellen
    spiel = Spiel(
        aktueller_tag=1,
        max_tag=24,
        geschenke=geschenke,
        elfen=elfen,
        schlitten=schlitten,
        spielstatus="gestoppt"
    )
    spiel.initialisiere_spiel()

def simuliere_tagesablauf():
# führt den Tagesablauf aus, indem Elfen Geschenke produzieren und der Schlitten beladen wird
    arbeitsstunden_pro_tag = 8.0    # 8 Stunden pro Tag

# Freien elfen geschenke zuweisen und Produktion starten
    for elf in Spiel.elfen:
        if not elf.ist.beschaeftigt() and Spiel.geschenke:
            freies_geschenk = next((g for g in Spiel.geschenke if g.geschenk_status == "nicht zugewiesen"), None)
            if freies_geschenk:
                elf.aktuelles_geschenk = freies_geschenk
                freies_geschenk.geschenk.zuweisung(elf.name)

                angepasste_zeit = elf.berechne_angepasste_fertigungszeit()
                freies_geschenk.fertigungszeit = angepasste_zeit
                elf.aktualisiere_elf_status(f"Baut {freies_geschenk.name}")

# Elfen arbeiten an geschenken
    for elf in Spiel.elfen:
        if elf.ist.beschaeftigt():
            g = elf.aktuelles_geschenk
            if g.fertigungszeit <= 0:
                g.fertigungszeit = 0
                g.aktualisiere_geschenk_status("Verpackt")
                elf.anzahl_produzierter_geschenke += 1
                elf.aktuelles_geschenk = None
                elf.aktualisiere_elf_status("Bereit")

# Fertige geschenke Laden
    for g in Spiel.geschenke:
        if g in Spiel.status == "Verpakt":
            if Spiel.schlitten.lade_geschenk(g):
                g.aktualisiere_geschenk_status("verladen")

# Auslieferung Prüfen
noch_in_arbeit = any(g.geschenk_status in ["nicht zugeiesen", "zugewiesen", "in Produktion"] for g in Spiel.geschenke)

if len(Spiel.schlitten.geladene_geschenke) > 0:
    if not noch_in_arbeit or Spiel.aktueller_tag == Spiel.max_tag or len(Spiel.schlitten.geladene_geschenke) >= 5:
        for g in Spiel.schlietten.geladene_geschenke:
            g.aktualisiere_geschenk_status("ausgeliefert")
        Spiel.schlitten.starte_auslieferung()

# Hintergrund Thread für denn Automatischen ablauf
def automatischer_ablauf():
    while Spiel.status not in ["beendet", "Gewonnen"]:
        if Spiel.status == "laeufend":
            simuliere_tagesablauf()

# Sieg oder Niederlage
            if all(g.geschenk_status == "ausgeliefert" for g in Spiel.geschenke):
                Spiel.spielstatus = "Gewonnen"
                print(
                    f"\nGewonnen! Alle Geschenke wurden bis zum "
                    f"{hole_kalender_datum(Spiel.aktueller_tag)} ausgeliefert."
                )
                break

            if Spiel.aktueller_tag >= Spiel.max_tag:
                print("\nZEIT ABGELAUFEN: Nicht alle Geschenke konnten rechtzeitig ausgeliefert werden.")
                break

            Spiel.aktueller_tag += 1
            time.sleep(1.5)

        elif Spiel.spielstatus == "Schnelldurchlauf":
            simuliere_tagesablauf()
            