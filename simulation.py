import tage_zeit
import random

def simuliere_tagesablauf(spiel):
    """Führt einen Tagesschritt aus: Elfen arbeiten, verpacken und laden."""
    arbeitsstunden_pro_tag = 8.0
    ereignisse = []
    elf_bereits_krank_diesen_tag = False

    # Elfen-Krankheit
    for elf in spiel.elfen:
        if elf.krankheits_tage_rest > 0:
            elf.krankheits_tage_rest -= 1
            if elf.krankheits_tage_rest == 0:
                elf.aktualisiere_elf_status("bereit")
                ereignis = f"{elf.name} ist wieder gesund und bereit für die Arbeit."
                ereignisse.append(ereignis)
                print(f"\n [GESUND] {ereignis}")
            continue

        if elf.elf_status == "krank" and elf.krankheits_tage_rest == 0:
            elf.aktualisiere_elf_status("bereit")

        if not elf_bereits_krank_diesen_tag and elf.elf_status != "krank":
            # Wahrscheinlichkeit, dass der Elf krank wird (15%)
            if random.random() < 0.10:
                elf_bereits_krank_diesen_tag = True
                elf.aktualisiere_elf_status("krank")

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

                krankheitsereignis = (
                    f"{elf.name} ist krank geworden und fällt {ausfall_tage} Tag(e) aus."
                )
                if elf.ist_beschaeftigt():
                    g = elf.aktuelles_geschenk
                    g.zugewiesener_elf = None
                    g.aktualisiere_geschenk_status("nicht zugewiesen")
                    elf.aktuelles_geschenk = None
                    krankheitsereignis += f" {g.name} wurde zurückgegeben."
                ereignisse.append(krankheitsereignis)

    # Gesunde freie Elfen erhalten ein neues Geschenk.
    for elf in spiel.elfen:
        if elf.elf_status != "krank" and not elf.ist_beschaeftigt():
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
                ereignisse.append(f"{g.name} wurde verpackt.")
                elf.anzahl_produzierter_geschenke += 1
                elf.aktuelles_geschenk = None
                elf.aktualisiere_elf_status("bereit")

    # U-Haft: Die verbleibende Haftzeit wird um einen Arbeitstag reduziert.
    if spiel.u_haft_stunden_rest > 0:
        haftstunden_vor_tag = spiel.u_haft_stunden_rest
        print(f"\n [U-HAFT] Der Weihnachtsmann sitzt im Knast und die Auslieferung ist Blockiert! Noch {spiel.u_haft_stunden_rest}Haft.")
        spiel.u_haft_stunden_rest -= arbeitsstunden_pro_tag
        if spiel.u_haft_stunden_rest < 0:
            spiel.u_haft_stunden_rest = 0.0
        ereignisse.append(
            f"U-Haft aktiv: {haftstunden_vor_tag:g} Stunden vor dem Arbeitstag, "
            f"{spiel.u_haft_stunden_rest:g} Stunden verbleibend."
        )
        tage_zeit.speichere_tagesprotokoll(spiel, ereignisse)
        return

    # Schlitten laden und ausliefern nur wenn nicht in U-haft
    for g in spiel.geschenke:
        if g.geschenk_status == "Verpackt":
            if spiel.schlitten.lade_geschenk(g):
                g.aktualisiere_geschenk_status("verladen")
                ereignisse.append(f"{g.name} wurde auf den Schlitten verladen.")

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
                ereignisse.append(f"{g.name} wurde ausgeliefert.")

            spiel.schlitten.starte_auslieferung()

    # chancen auf ein zweiten strafzettel
    if spiel.strafzettel_tag is not None and spiel.strafzettel_ignoriert:
        vergangene_tage = spiel.aktueller_tag - spiel.strafzettel_tag

        if vergangene_tage == 1:
            print(f"\n Polizei bittet den Weihnachtsmann, den Strafzettel zu zahlen...")
            ereignisse.append("Die Polizei fordert den Weihnachtsmann auf, den Strafzettel zu bezahlen.")
            if random.choice([True, False]):
                print("Er zahlt. Alles erledigt!")
                ereignisse.append("Der Weihnachtsmann hat den Strafzettel bezahlt.")
                spiel.strafzettel_tag = None
                spiel.strafzettel_ignoriert = False
            else:
                print("Er weigert sich zu zahlen!")
                ereignisse.append("Der Weihnachtsmann weigert sich, den Strafzettel zu bezahlen.")
    
        elif vergangene_tage >= 2:
            erwischt = random.choice([True, False])
            
            if erwischt:
                # Je nachdem wie viele Tage vergangen sind, gibt es unterschiedlich lange U-Haft
                        # 2 tage
                if vergangene_tage == 2:
                    print(f"\n der Weihnachtsmann wurde von der Polizei erwischt und ist in Haft gelandet für 16 Stunden")
                    spiel.u_haft_stunden_rest = 16.0
                    ereignisse.append("Der Weihnachtsmann wurde erwischt und zu 16 Stunden U-Haft verurteilt.")
                        # 3 tage
                elif vergangene_tage == 3:
                    print(f"\n der Weihnachtsmann wurde von der Polizei erwischt und ist in Haft gelandet für 2 Tage")
                    spiel.u_haft_stunden_rest = 24.0
                    ereignisse.append("Der Weihnachtsmann wurde erwischt und zu 24 Stunden U-Haft verurteilt.")
                else:   # 4 oder mehr Tage
                    print(f"\n der Weihnachtsmann wurde von der Polizei erwischt und ist in Haft gelandet für 2 Tage 8 stunden")
                    spiel.u_haft_stunden_rest = 32.0
                    ereignisse.append("Der Weihnachtsmann wurde erwischt und zu 32 Stunden U-Haft verurteilt.")
                
                # Strafzettel ist damit beglichen/abgegolten
                spiel.strafzettel_tag = None
                spiel.strafzettel_ignoriert = False
            else:
                ereignisse.append("Der Weihnachtsmann wurde nicht erwischt.")
                if vergangene_tage in [2, 3]:
                    print("Glück gehabt, Der Weihnachtsman wurde nicht erwischt. Dafür erhöht sich die strafe")
                    ereignisse.append("Die Strafe für den ignorierten Strafzettel erhöht sich.")
                elif vergangene_tage == 4:
                    print("Glück gehabt, Der Weihanchtsmann wurde noch nicht erwischt. Die höhe der Strafe wird ab hier nicht mehr steigen")
                    ereignisse.append("Die Strafe steigt nicht weiter, obwohl der Strafzettel noch offen ist.")
                else:
                    print("Schon Wieder Glück gehabt bald wird der Weinahchtsmann ein Schwerverbrecher!")
                    ereignisse.append("Der Weihnachtsmann wurde erneut nicht erwischt.")

    tage_zeit.speichere_tagesprotokoll(spiel, ereignisse)