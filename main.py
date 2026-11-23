import json
import random
import time
import calendar
import threading
import classes
from prettytable import PrettyTable
import msvcrt
import os

lock = threading.Lock()

def lade_daten_aus_json(dateipfad):
    """Lädt Elfen- und Geschenkedaten aus einer JSON-Datei."""
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

def get_weekday_by_date(tag):
    wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    wochentag_idx = calendar.weekday(2026, 12, tag)
    return wochentage[wochentag_idx]

def zeige_benutzeroberfläche(spiel):
    """Erstellt die Konsolen-UI mit PrettyTable."""
    print("\n" + "=" * 65)
    print(f"|{'SANTAS WEIHNACHTSWERKSTATT-MANAGER 2026':^63}|")
    print("-" * 65)
    datum_str = hole_kalender_datum(spiel.aktueller_tag)
    print(f"| Aktueller Spieltag: Tag {spiel.aktueller_tag} von {spiel.max_tag} ({datum_str})".ljust(64) + "|")
    print(f"| System-Status: {spiel.spielstatus}".ljust(64) + "|")
    print("=" * 65)
    
    # --- 1. WUNSCHLISTE ---
    print("\n[ WUNSCHLISTE ]")
    tabelle_wunschliste = PrettyTable()
    tabelle_wunschliste.fieldnames = ["ID", "Wunschliste", "Gewicht", "Kategorie", "Status", "Elf"]
    tabelle_wunschliste.align["Wunschliste"] = "l"
    tabelle_wunschliste.align["Kategorie"] = "l"
    tabelle_wunschliste.align["Status"] = "l"
    
    for g in spiel.geschenke:
        if hasattr(g.zugewiesener_elf, 'name') and g.zugewiesener_elf:
            elf_name = g.zugewiesener_elf.name
        elif g.zugewiesener_elf:
            elf_name = str(g.zugewiesener_elf)
        else:
            elf_name = "-"
            
        tabelle_wunschliste.add_row([
            g.geschenk_id,
            g.name,
            f"{g.gewicht:.1f} kg",
            g.kategorie,
            g.geschenk_status,
            elf_name
        ])
    print(tabelle_wunschliste)

    # --- 2. ELFEN-STATUS ---
    print("\n[ ELFEN-STATUS ]")
    tabelle_elfen = PrettyTable()
    tabelle_elfen.fieldnames = ["Elf-Name", "Fachgebiet", "Status", "Fertig"]
    tabelle_elfen.align["Elf-Name"] = "l"
    tabelle_elfen.align["Fachgebiet"] = "l"
    tabelle_elfen.align["Status"] = "l"
    
    for e in spiel.elfen:
        tabelle_elfen.add_row([
            e.name,
            e.fachgebiet,
            e.elf_status,
            e.anzahl_produzierter_geschenke
        ])
    print(tabelle_elfen)

    # --- 3. SCHLITTEN-STATUS ---
    print("-" * 50)
    print("SCHLITTEN-STATUS")
    print(f"Ladung: {spiel.schlitten.aktuelles_gewicht:.1f} / {spiel.schlitten.max_gewicht} kg  |  Verladene Geschenke: {len(spiel.schlitten.geladene_geschenke)}")
    print("-" * 50)
    
    # --- 4. STEUERUNGSLEISTE ---
    print("\n[STEUERUNG] (1) Normal [1 Min/Tag] | (2) Pause | (3) Schnell [5 Sek/Tag] | (4) Beenden")

def simuliere_tagesablauf(spiel):
    """Führt einen Tagesschritt aus: Elfen arbeiten, verpacken und laden."""
    arbeitsstunden_pro_tag = 8.0

    for elf in spiel.elfen:
        if not elf.ist_beschaeftigt():
            freies_geschenk = next(
                (g for g in spiel.geschenke if g.geschenk_status == "nicht zugewiesen"),
                None
            )
            if freies_geschenk is not None:
                elf.aktuelles_geschenk = freies_geschenk
                freies_geschenk.geschenk_zuweisung(elf)
                
                angepasste_zeit = elf.berechnung_bauzeit()
                freies_geschenk.fertigungszeit = angepasste_zeit
                freies_geschenk.aktualisiere_geschenk_status("in Produktion")
                elf.aktualisiere_elf_status(f"Baut {freies_geschenk.name}")

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

    for g in spiel.geschenke:
        if g.geschenk_status == "Verpackt":
            if spiel.schlitten.lade_geschenk(g):
                g.aktualisiere_geschenk_status("verladen")

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

def automatischer_ablauf(spiel):
    global modus
    """Hintergrund-Thread, der die Simulation abhängig vom Status steuert (Normal, Schnell, Pause)."""
    while spiel.spielstatus not in ["beendet", "Gewonnen"]:
        with lock:
            if spiel.spielstatus == "pausiert":
                pausiert = True
            else:
                pausiert = False

        if pausiert:
            time.sleep(0.1)
            continue

        # Wochentag prüfen
        wochentag = get_weekday_by_date(spiel.aktueller_tag)
        if wochentag in ["Samstag", "Sonntag"]:
            with lock:
                spiel.spielstatus = f"Wochenende ({wochentag}) - Die Elfen haben frei"
        else:
            with lock:
                spiel.spielstatus = f"Laeuft ({wochentag})"
            simuliere_tagesablauf(spiel)

        # Siegprüfung
        if all(g.geschenk_status == "ausgeliefert" for g in spiel.geschenke):
            with lock:
                spiel.spielstatus = "Gewonnen"
                break

        # Niederlagenprüfung
        with lock:
            if spiel.aktueller_tag >= spiel.max_tag:
                spiel.spielstatus = "beendet"
                break

        with lock:
            if modus == "(schnell)":
                wartezeit = 5.0
            else:
                wartezeit = 60.0

        verstrichen = 0.0
        while verstrichen < wartezeit:
            with lock:
                if spiel.spielstatus == "pausiert":
                    pausiert = True
                else:
                    pausiert = False
                    aktuelle_wartezeit = 5.0 if modus == "(schnell)" else 60.0

            if pausiert:
                time.sleep(0.1)
                continue
            if spiel.spielstatus in ["beendet", "Gewonnen"]:
                break
            if wartezeit != aktuelle_wartezeit:
                break
            
            time.sleep(0.5)
            verstrichen += 0.5

        with lock:
            if spiel.spielstatus not in ["pausiert", "beendet", "Gewonnen"]:
                spiel.aktueller_tag += 1

letzter_tag = None
letzter_status = None
modus = "(Normal)"

def main():
    daten = lade_daten_aus_json("elfen_geschenke.json")
    
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
    simulations_thread = threading.Thread(target=automatischer_ablauf, args=(spiel,), daemon=True)
    simulations_thread.start()
    
    global letzter_tag
    global letzter_status
    global modus
    # Hauptschleife für die interaktive Konsolensteuerung
    while spiel.spielstatus not in ["beendet", "Gewonnen"]:
        with lock:
            if spiel.aktueller_tag != letzter_tag or spiel.spielstatus != letzter_status:
                os.system("cls")
                zeige_benutzeroberfläche(spiel)
                letzter_tag = spiel.aktueller_tag
                letzter_status = spiel.spielstatus 

            if msvcrt.kbhit() == True:
                taste = msvcrt.getwch()

                try:
                    wahl_int = int(taste)
                    
                    if wahl_int == 1:
                        modus = "(Normal)"
                        spiel.spielstatus = "Laeuft (Normal)"
                        letzter_status = None
                        print("\n[INFO] Normaler Modus aktiv: 1 Tag = 1 Minute.")
                    elif wahl_int == 2:
                        spiel.spielstatus = "pausiert"
                        letzter_status = None
                        print("\n[INFO] Spiel pausiert! Die Zeit ist eingefroren.")
                    elif wahl_int == 3:
                        modus = "(schnell)"
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

    zeige_benutzeroberfläche(spiel)
    if spiel.spielstatus == "Gewonnen":
        print(f"\nGEWONNEN! Alle Geschenke wurden bis zum {hole_kalender_datum(spiel.aktueller_tag)} ausgeliefert!")
    elif spiel.spielstatus == "beendet" and spiel.aktueller_tag >= spiel.max_tag:
        print("\nZEIT ABGELAUFEN: Nicht alle Geschenke konnten rechtzeitig ausgeliefert werden.")

if __name__ == "__main__":
    main()