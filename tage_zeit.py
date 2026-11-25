import calendar
import msvcrt
import os


def tagesprotokoll_anzeigen(spiel):
    os.system("cls")
    if spiel.tagesprotokoll:
        for eintrag in spiel.tagesprotokoll:
            print(f"\nTag {eintrag['tag']} - {eintrag['datum']}")
            if eintrag["ereignisse"]:
                for ereignis in eintrag["ereignisse"]:
                    print(f"  - {ereignis}")
            else:
                print("  Keine besonderen Ereignisse.")
    else:
        print("Es gibt noch kein Tagesprotokoll.")

    print("\nBeliebige Taste drücken, um zum Spiel zurückzukehren.")
    msvcrt.getwch()
    letzter_status = None

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

def speichere_tagesprotokoll(spiel, ereignisse):
    tagesereignis = {
        "tag": spiel.aktueller_tag,
        "datum": hole_kalender_datum(spiel.aktueller_tag),
        "ereignisse": ereignisse
    }
    with lock:
        spiel.tagesprotokoll.append(tagesereignis)