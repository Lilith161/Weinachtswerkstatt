import json
import random
import time
import threading
import calendar
import classes

def lade_daten_aus_json(dateipfad):
# laden der Elfen, geschenke 
    with open(dateipfad, "r", encoding="utf-8") as f:
        daten = json.load(f)
    return daten

def parse_gewicht(gewicht_str):
# ändert "2,5kg" zu float "2.5"
    rein = gewicht_str.lower().replace("kg", "").strip().replace(",", ".")
    return float(rein)

def parse_zeit(zeit_str):
# ändert "24h" zu float "24.0"
    rein = zeit_str.lower().replace("h", "").strip().replace(",", ".")
    return float(rein)

def hole_kalender_datum(tag):
# Kalender (Jahre, Monate, tage)
    wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    wochentag_idx = calendar.weekday(2026, 12, tag)
    return f"{wochentage[wochentag_idx]}, {tag}. Dezember 2026"

def main():
# json Daten laden
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
        
# Geschenke aus der json laden
    geschenke_roh = daten["geschenke"]
    ausgewaehlte_roh = random.sample(geschenke_roh, min(10, len(geschenke_roh)))
    
    geschenke = []
    for g_data in ausgewaehlte_roh:
        g_id = int(g_data["geschenk_id"])
        name = g_data["name"]
        kategorie = g_data["kategorie"].lower()
        fertigungszeit = parse_zeit(g_data["fertigungszeit"])
        gewicht = parse_gewicht(g_data["gewicht"])
        
        geschenk = geschenk(
            geschenk_id=g_id,
            name=name,
            gewicht=gewicht,
            kategorie=kategorie,
            geschenk_status="nicht zugewiesen",
            zugewiesener_elf=None,
            fertigungszeit=fertigungszeit
        )
        geschenke.append(geschenk)
        
# Schlitten erstellen max Gewicht 20kg
    schlitten = schlitten(max_gewicht=20.0, aktuelles_gewicht=0.0, geladene_geschenke=[])
    
# Spiel-Instanz erstellen 
    spiel = spiel(
        aktueller_tag=1,
        max_tag=24,
        geschenke=geschenke,
        elfen=elfen,
        schlitten=schlitten,
        spielstatus="laeuft"
    )
    spiel.initialisiere_spiel()
    spiel.spielstatus = "laeuft"  # Direkt auf Start setzen

def simuliere_tagesablauf(spiel):
    arbeitsstunden_pro_tag = 8.0

# Freien Elfen Geschenke zuweisen und die Produktion starten
    for elf in spiel.elfen:
        if not elf.ist_beschaeftigt():
            freies_geschenk = next(
                (g for g in spiel.geschenke if g.geschenk_status == "nicht zugewiesen"),
                None,
            )
            if freies_geschenk is not None:
                elf.aktuelles_geschenk = freies_geschenk
                freies_geschenk.geschenk_zuweisung(elf.name)
                freies_geschenk.fertigungszeit = elf.berechnung_bauzeit()
                freies_geschenk.aktualisiere_geschenk_status("in Produktion")
                elf.aktualisiere_elf_status(f"Baut {freies_geschenk.name}")

# Elfen arbeiten an Geschenken
    for elf in spiel.elfen:
        if elf.ist_beschaeftigt():
            g = elf.aktuelles_geschenk
            g.fertigungszeit -= arbeitsstunden_pro_tag
            if g.fertigungszeit <= 0:
                g.fertigungszeit = 0
                g.aktualisiere_geschenk_status("verpackt")
                elf.anzahl_produzierter_geschenke += 1
                elf.aktuelles_geschenk = None
                elf.aktualisiere_elf_status("bereit")

# Fertige Geschenke laden
    for g in spiel.geschenke:
        if g.geschenk_status == "verpackt":
            if spiel.schlitten.lade_geschenk(g):
                g.aktualisiere_geschenk_status("verladen")

# Auslieferung prüfen
    noch_in_arbeit = any(
        g.geschenk_status in ["nicht zugewiesen", "zugewiesen", "in Produktion"]
        for g in spiel.geschenke
    )

    if spiel.schlitten.geladene_geschenke:
        if (
            not noch_in_arbeit
            or spiel.aktueller_tag == spiel.max_tag
            or len(spiel.schlitten.geladene_geschenke) >= 5
        ):
            for g in spiel.schlitten.geladene_geschenke:
                g.aktualisiere_geschenk_status("ausgeliefert")
            spiel.schlitten.starte_auslieferung()


# Automatischer Ablauf
    def automatischer_lauf():
        while spiel.spielstatus not in ["beendet", "Gewonnen"]:
            if spiel.spielstatus == "laeuft":
                simuliere_tagesablauf()
                
                # Sieg oder niederlage
                if all(g.geschenk_status == "ausgeliefert" for g in spiel.geschenke):
                    spiel.spielstatus = "Gewonnen"
                    print(f"\n GEWONNEN Alle Geschenke wurden bis zum {hole_kalender_datum(spiel.aktueller_tag)} ausgeliefert")
                    break
                    
                if spiel.aktueller_tag >= spiel.max_tag:
                    spiel.pruefe_spielende()
                    print("\n ZEIT ABGELAUFEN! Nicht alle Geschenke konnten rechtzeitig ausgeliefert werden.")
                    break
                    
                spiel.aktueller_tag += 1
                time.sleep(1.5)  # 1.5 Sekunden Pause zwischen denn tagen