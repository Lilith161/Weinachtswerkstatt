import json
import random
import time
import calendar
import classes

def lade_daten_aus_json(dateipfad):
    """Lädt Elfen- und Geschenkedaten aus einer JSON-Datei."""
    with open(dateipfad, "r", encoding="utf-8") as f:
        daten = json.load(f)
    return daten

def parse_gewicht(gewicht_str):
    """Wandelt einen String wie '2.5kg' oder '1,5 kg' in ein Float um."""
    rein = gewicht_str.lower().replace("kg", "").strip().replace(",", ".")
    return float(rein)

def parse_zeit(zeit_str):
    """Wandelt einen String wie '24h' oder '13 h' in ein Float um."""
    rein = zeit_str.lower().replace("h", "").strip().replace(",", ".")
    return float(rein)

def hole_kalender_datum(tag):
    """Gibt das formatierte Datum für den Dezember 2026 zurück."""
    wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    wochentag_idx = calendar.weekday(2026, 12, tag)
    return f"{wochentage[wochentag_idx]}, {tag}. Dezember 2026"

def get_weekday_by_date(tag):
    """Gibt das formatierte Datum für den Dezember 2026 zurück."""
    wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    wochentag_idx = calendar.weekday(2026, 12, tag)
    return wochentage[wochentag_idx]

def simuliere_tagesablauf(spiel):
    """Führt einen Tagesschritt aus: Elfen arbeiten, verpacken und laden."""
    arbeitsstunden_pro_tag = 8.0  # 8 Stunden Schicht pro Tag

    # 1. Freien Elfen neue Geschenke zuweisen
    for elf in spiel.elfen:
        if not elf.ist_beschaeftigt():
            freies_geschenk = next(
                (g for g in spiel.geschenke if g.geschenk_status == "nicht zugewiesen"),
                None
            )
            if freies_geschenk is not None:
                elf.aktuelles_geschenk = freies_geschenk
                freies_geschenk.geschenk_zuweisung(elf)  # Übergibt das Elf-Objekt
                
                # Bauzeit berechnen (inkl. Fachgebiets-Bonus)
                angepasste_zeit = elf.berechnung_bauzeit()
                freies_geschenk.fertigungszeit = angepasste_zeit
                freies_geschenk.aktualisiere_geschenk_status("in Produktion")
                elf.aktualisiere_elf_status(f"Baut {freies_geschenk.name}")

    # 2. Elfen arbeiten an ihren Geschenken
    for elf in spiel.elfen:
        if elf.ist_beschaeftigt():
            g = elf.aktuelles_geschenk
            g.fertigungszeit -= arbeitsstunden_pro_tag
            
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

    # 4. Auslieferung prüfen (z. B. wenn Schlitten voll ist, am Ende oder keine Arbeit mehr da ist)
    noch_in_arbeit = any(
        g.geschenk_status in ["nicht zugewiesen", "zugewiesen", "in Produktion"]
        for g in spiel.geschenke
    )

    if spiel.schlitten.geladene_geschenke:
        if (
            not noch_in_arbeit
            or spiel.aktueller_tag == spiel.max_tag
            or spiel.schlitten.aktuelles_gewicht >= spiel.schlitten.max_gewicht
            or len(spiel.schlitten.geladene_geschenke) >= 5
        ):
            for g in spiel.schlitten.geladene_geschenke:
                g.aktualisiere_geschenk_status("ausgeliefert")
            spiel.schlitten.starte_auslieferung()

def main():
    # JSON-Daten laden
    daten = hole_daten = lade_daten_aus_json("elfen_geschenke.json")
    
    # Elfen initialisieren (mit classes.Elf)
    elfen = []
    for e_data in daten["elfen"]:
        elf = classes.elf(
            elf_id=e_data["elf_id"],
            name=e_data["name"],
            fachgebiet=e_data["fachgebiet"].lower(),
            anzahl_produzierter_geschenke=0,
            aktuelles_geschenk=None,
            elf_status="bereit"
        )
        elfen.append(elf)
        
    # Geschenke initialisieren (wahlweise alle oder per random.sample)
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
            fertigungszeit=parse_zeit(g_data["fertigungszeit"])
        )
        geschenke.append(geschenk)
        
    # Schlitten und Spielinstanz erstellen
    schlitten = classes.schlitten(max_gewicht=20.0, aktuelles_gewicht=0.0, geladene_geschenke=[])
    
    spiel = classes.spiel(
        aktueller_tag=1,
        max_tag=24,
        geschenke=geschenke,
        elfen=elfen,
        schlitten=schlitten,
        spielstatus="gestartet"
    )
    spiel.initialisiere_spiel()
    
    print("--- SANTA'S WEIHNACHTSWERKSTATT-MANAGER ---")
    print(f"Spiel gestartet! Tag {spiel.aktueller_tag} von {spiel.max_tag}.\n")

    # Hauptschleife über die Spieltage (1 bis 24)
    # array table contents [array cont1[], array cont2]
    while spiel.spielstatus not in ["beendet", "Gewonnen"]:
        # UI anzeigen
        zeige_benutzeroberfläche(spiel)

        # Siegprüfung
        if all(g.geschenk_status == "ausgeliefert" for g in spiel.geschenke):
            spiel.spielstatus = "Gewonnen"
            print(f"\nGEWONNEN! Alle Geschenke wurden bis zum {hole_kalender_datum(spiel.aktueller_tag)} ausgeliefert.")
            break

            # Niederlagenprüfung: Maximale Tage erreicht
            if spiel.aktueller_tag >= spiel.max_tag:
                spiel.spielstatus = "beendet"
                print("\nZEIT ABGELAUFEN: Nicht alle Geschenke konnten rechtzeitig ausgeliefert werden.")
                break

            # content array add []
            spiel.aktueller_tag += 1
            time.sleep(1.0)

    #auserhalb der while schleife
    # x = Prettytable
    # x.fieldnames = [...]
    # foreach cont_array
    #   x.add_row(foreach_obj)
    # print(x)
if __name__ == "__main__":
    main()