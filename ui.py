from prettytable import PrettyTable
import tage_zeit_doku

def zeige_benutzeroberfläche(spiel):
    """Erstellt die Konsolen-UI mit PrettyTable."""
    print("\n" + "=" * 65)
    print(f"|{'SANTAS WEIHNACHTSWERKSTATT-MANAGER 2026':^63}|")
    print("-" * 65)
    datum_str = tage_zeit_doku.hole_kalender_datum(spiel.aktueller_tag)
    print(f"| Aktueller Spieltag: Tag {spiel.aktueller_tag} von {spiel.max_tag} ({datum_str})".ljust(64) + "|")
    print(f"| System-Status: {spiel.spielstatus}".ljust(64) + "|")
    print("=" * 65)
    
    # --- 1. WUNSCHLISTE ---
    print("\n[ WUNSCHLISTE ]")
    tabelle_wunschliste = PrettyTable()
    tabelle_wunschliste.fieldnames = ["ID", "Wunschliste", "Gewicht", "Kategorie", "Status", "Elf"]
    tabelle_wunschliste.align["Wunschliste"] = "1"
    tabelle_wunschliste.align["Kategorie"] = "1"
    tabelle_wunschliste.align["Status"] = "1"
    
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
    if spiel.spielstatus == "pausiert":
        print("\n[STEUERUNG] (1) Normal [1 Min/Tag] | (2) Pause | (3) Schnell [5 Sek/Tag] | (4) Beenden | (V) Vergangene Tage")
    else:
        print("\n[STEUERUNG] (1) Normal [1 Min/Tag] | (2) Pause | (3) Schnell [5 Sek/Tag] | (4) Beenden")