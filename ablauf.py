import tage_zeit_doku
import time
import simulation
from synchronisierung import lock

modus = "(Normal)"

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
        wochentag = tage_zeit_doku.get_weekday_by_date(spiel.aktueller_tag)
        if wochentag in ["Samstag", "Sonntag"]:
            with lock:
                spiel.spielstatus = f"Wochenende ({wochentag}) - Die Elfen haben frei"
            tage_zeit_doku.speichere_tagesprotokoll(
                spiel,
                [f"Wochenende ({wochentag}) - Die Elfen haben frei."]
            )
        else:
            with lock:
                spiel.spielstatus = f"Laeuft ({wochentag})"
            simulation.simuliere_tagesablauf(spiel)

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
                wartezeit = 1.0
            else:
                wartezeit = 10.0

        verstrichen = 0.0
        while verstrichen < wartezeit:
            with lock:
                if spiel.spielstatus == "pausiert":
                    pausiert = True
                else:
                    pausiert = False
                    aktuelle_wartezeit = 1.0 if modus == "(schnell)" else 10.0

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