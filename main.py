import json
import random
import time
import calendar
import classes

def lade_daten_aus_json(dateipfad):
    with open(dateipfad, "r", encoding="utf-8") as f:
        daten = json.load(f)
    return daten


def parse_gewicht(gewicht_str):
    rein = gewicht_str.lower().replace("kg", "").strip().replace(",", ".")
    return float(rein)

def parse_zeit(zeit_str):
    rein = zeit_str.lower().replace("h", "").strip().replace(",", ".")
    return float(rein)
    

def hole_kalender_datum(tag):
    wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    wochentag_idx = calendar.weekday(2026, 12, tag)
    return f"{wochentage[wochentag_idx]}, {tag}. Dezember 2026"

def simuliere_tagesablauf(spiel):
    """Führt einen Tagesschritt aus und greift sauber auf das spiel-Objekt zu."""
    
    # 1. Freien Elfen Geschenke zuweisen
    for elf in spiel.elfen:
        if not elf.ist_beschaeftigt():
            # Finde ein unzugewiesenes Geschenk
            freies_geschenk = next((g for g in spiel.geschenke if g.geschenk_status == "nicht zugewiesen"), None)
            if freies_geschenk:
                elf.aktuelles_geschenk = freies_geschenk
                freies_geschenk.geschenk_zuweisung(elf) # Übergibt das Elf-Objekt
                
                # Bauzeit berechnen (inkl. Fachgebiets-Bonus)
                angepasste_zeit = elf.berechnung_bauzeit()
                freies_geschenk.fertigungszeit = angepasste_zeit
                elf.aktualisiere_elf_status(f"Baut {freies_geschenk.name}")

    # 2. Elfen arbeiten an Geschenken (8 Stunden Schicht)
    arbeitsstunden = 8.0
    for elf in spiel.elfen:
        if elf.ist_beschaeftigt():
            g = elf.aktuelles_geschenk
            g.fertigungszeit -= arbeitsstunden # Reduziert die Bauzeit um die Arbeitsstunden
            
            if g.fertigungszeit <= 0:
                g.fertigungszeit = 0
                g.aktualisiere_geschenk_status("Verpackt")
                elf.anzahl_produzierter_geschenke += 1
                elf.aktuelles_geschenk = None
                elf.aktualisiere_elf_status("bereit")

    # 3. Fertige Geschenke in den Schlitten laden
    for g in spiel.geschenke:
        if g.geschenk_status == "Verpackt":
            if spiel.schlitten.lade_geschenk(g):
                g.aktualisiere_geschenk_status("verladen")

    # 4. Auslieferung prüfen (z.B. wenn Schlitten voll ist oder am Ende)
    noch_in_arbeit = any(g.geschenk_status in ["nicht zugewiesen", "zugewiesen", "In Produktion"] for g in spiel.geschenke)

    if len(spiel.schlitten.geladene_geschenke) > 0:
        if not noch_in_arbeit or spiel.aktueller_tag == spiel.max_tag or spiel.schlitten.aktuelles_gewicht >= spiel.schlitten.max_gewicht:
            for g in spiel.schlitten.geladene_geschenke:
                g.aktualisiere_geschenk_status("ausgeliefert")
            spiel.schlitten.starte_auslieferung()

def main():
    daten = lade_daten_aus_json("elfen_geschenke.json")
    
    # Elfen initialisieren
    elfen = []
    for e_data in daten["elfen"]:
        elf = elf(
            elf_id=e_data["elf_id"],
            name=e_data["name"],
            fachgebiet=e_data["fachgebiet"].lower(),
            anzahl_produzierter_geschenke=0,
            aktuelles_geschenk=None,
            elf_status="bereit"
        )
        elfen.append(elf)
        
    # Geschenke initialisieren (alle 15 aus der JSON)
    geschenke = []
    for g_data in daten["geschenke"]:
        geschenk = geschenk(
            geschenk_id=int(g_data["geschenk_id"]),
            name=g_data["name"],
            gewicht=parse_gewicht(g_data["gewicht"]),
            kategorie=g_data["kategorie"].lower(),
            geschenk_status="nicht zugewiesen",
            zugewiesener_elf=None,
            fertigungszeit=parse_zeit(g_data["fertigungszeit"])
        )
        geschenke.append(geschenk)
        
    schlitten = schlitten(max_gewicht=35.0, aktuelles_gewicht=0.0, geladene_geschenke=[])
    
    spiel = spiel(
        aktueller_tag=1,
        max_tag=24,
        geschenke=geschenke,
        elfen=elfen,
        schlitten=schlitten,
        spielstatus="gestartet"
    )
    spiel.initialisiere_spiel()
    
    print("--- SANTA'S WEIHNACHTSWERKSTATT-MANAGER ---")
    print(f"Spiel gestartet! Tag {spiel.aktueller_tag} von {spiel.max_tag}.")

    # Beispielhafter Ablauf über die Spieltage
    while spiel.spielstatus not in ["beendet", "Gewonnen"]:
        print(f"\n--- {hole_kalender_datum(spiel.aktueller_tag)} ---")
        simuliere_tagesablauf(spiel)

        # Siegprüfung
        if all(g.geschenk_status == "ausgeliefert" for g in spiel.geschenke):
            spiel.spielstatus = "Gewonnen"
            print(f"\nGewonnen! Alle Geschenke wurden bis zum {hole_kalender_datum(spiel.aktueller_tag)} ausgeliefert.")
            break

        # Niederlagenprüfung
        if spiel.aktueller_tag >= spiel.max_tag:
            spiel.spielstatus = "beendet"
            print("\nZEIT ABGELAUFEN: Nicht alle Geschenke konnten rechtzeitig ausgeliefert werden.")
            break

        spiel.aktueller_tag += 1
        time.sleep(1.0)

if __name__ == "__main__":
    main()
