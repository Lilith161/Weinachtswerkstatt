# für komplikationen in classes ergänzung
import random #Wichtig
# Elfen krank
class elf:
    def __init__(self, elf_id, name, fachgebiet, anzahl_produzierter_geschenke, aktuelles_geschenk, elf_status):
        self.elf_id = elf_id
        self.name = name 
        self.fachgebiet = fachgebiet 
        self.anzahl_produzierter_geschenke = anzahl_produzierter_geschenke 
        self.aktuelles_geschenk = aktuelles_geschenk 
        self.elf_status = elf_status

        self.krankheits_tage_rest = 0       # gibt an wie viele tage der Elfe noch ausfällt

# Strafzettel
class spiel:
    def __init__(self, aktueller_tag, max_tag, geschenke, elfen, schlitten, spielstatus):
        self.aktueller_tag = aktueller_tag
        self.max_tag = max_tag
        self.geschenke = geschenke
        self.elfen = elfen
        self.schlitten = schlitten
        self.spielstatus = spielstatus

        self.strafzettel_tag = None
        self.strafzettel_ignoriert = False
        self.u_haft_stunden_rest = 0.0

# ergänzung fürs main
def simuliere_tagesablauf(spiel):
    arbeitsstunden_pro_tag = 8.0

    # Prüfung Krankheit
    for elf in spiel.elfen:
        # Wenn elf schon krank ist zählt zeit runter
        if elf.krankheits_tage_rest > 0:
            elf.krankheits_tage_rest -= 1
            if elf.krankheits_tage_rest == 0:
                elf.aktualisiere_elf_status("bereit")
                print(f"\n [GESUND] {elf.name} ist wieder gesund und bereit für die arbeit")
            continue

        # Wahrscheinlichkeit, dass der Elf krank wird (10%)
        if random.random() < 0.10:
            # Wahrscheinlichkeit, wie lange der Elf krank ist
            dauer_roll = random.random()
            ausfall_tage = 1

            if dauer_roll < 0.010:          # 1% chance für 5 Tage
                ausfall_tage = 5
            elif dauer_roll < 0.040:        # 4% chance für 4 Tage
                ausfall_tage = 4
            elif dauer_roll < 0.10:         # 10% chance für 3 Tage
                ausfall_tage = 3
            elif dauer_roll < 0.25:         # 25% chance für 2 Tage
                ausfall_tage = 2
            else:
                ausfall_tage = 1            # 60% chance für 1 Tag

            elf.krankheits_tage_rest = ausfall_tage
            print(
                f"\n [krankheit] Oh nein Elf {elf.name} ist krank geworden"
                f"und fällt {ausfall_tage} Tag(e) aus!"
            )

            # Falls der Elf gerade an einem Geschenk gearbeitet hat,
            # wird das Geschenk zurückgegeben.
            if elf.ist_beschaeftigt():
                g = elf.aktuelles_geschenk
                g.zugewiesener_elf = None
                g.aktualisiere_geschenk_status("nicht zugewiesen")
                elf.aktuelles_geschenk = None

            elf.aktualisiere_elf_status("krank")

    # U-Haft: Die verbleibende Haftzeit wird um einen Arbeitstag reduziert.
    if spiel.u_haft_stunden_rest > 0:
        print(f"\n [U-HAFT] Der Weihnachtsmann sitzt im Knast und die Auslieferung ist Blockiert! Noch {spiel.u_haft_stunden_rest}Haft.")
        spiel.u_haft_stunden_rest -= arbeitsstunden_pro_tag
        if spiel.u_haft_stunden_rest < 0:
            spiel.u_haft_stunden_rest = 0.0
        return

# Schlitten laden und ausliefern nur wenn nicht in U-haft
    for g in spiel.geschenke:
        if g.geschenk_status == "verpackt":
            if spiel.schlitten.lade_geschenke(g):
                g.aktualisiere_geschenk_status("verladen")

    noch_in_arbeit = any(
        g.geschenk_status in ["nicht zugewiesen", "zugewiesen", "in Produktion"]
        for g in spiel.geschenke
    )

    if spiel.geladene_geschenke:
        if (
            not noch_in_arbeit
            or spiel.aktueller_tag == spiel.max_tag
            or len(spiel.schlitten.geladene_geschenke) >= 5
        ):
            for g in spiel.schlitten.geladene_geschenke:
                g.aktualisiere_geschenk_status("ausgeliefert")

            spiel.schlitten.starte_auslieferung()

            # chancen auf ein zweiten strafzettel
            if spiel.strafzettel_tag is None and random.random() < 0.25:
                vergangene_tage = spiel.aktueller_tag

            if vergangene_tage == 1:
                print(f"\n Polizei bittet den Weihnachtsmann, den Strafzettel zu zahlen.")
            if random.choice([True, False]):
                print("💸 Er zahlt. Alles erledigt!")
                spiel.strafzettel_tag = None
                spiel.strafzettel_ignoriert = False
            else:
                print(" Er weigert sich zu zahlen und flüchtet!")
                
        elif vergangene_tage == 2:
            # Wenn er nach 2 Tagen erwischt wird
            print(f"\n Der Weihnachtsmann wird von der Polizei erwischt und Kommt für 16 stunden in Haft!")
            spiel.u_haft_stunden_rest = 16.0  
            spiel.strafzettel_tag = None
            spiel.strafzettel_ignoriert = False

        elif vergangene_tage == 3:
            # Wenn er nach 3 Tagen erwischt wird
            print(f"\n Der Weihnachtsmann wird von der Polizei erwischt und Kommt für 24 stunden in Haft!")
            spiel.u_haft_stunden_rest = 24.0  
            spiel.strafzettel_tag = None
            spiel.strafzettel_ignoriert = False

        elif vergangene_tage >= 4:
            # Wenn es 4 oder mehr Tage her ist
            print(f"\n Der Weihnachtsmann wird von der Polizei erwischt und Kommt für 32 stunden in Haft!")
            spiel.u_haft_stunden_rest = 32.0
            spiel.strafzettel_tag = None
            spiel.strafzettel_ignoriert = False