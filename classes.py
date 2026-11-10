class Geschenk:
    def __init__(self, geschenk_id, name, gewicht, kategorie, geschenk_statues, zugewiesener_elf, benoetigte_zeit):
        self.geschenk_id = geschenk_id
        self.name = name
        self.gewicht = gewicht
        self.kategorie = kategorie
        self.geschenk_statues = geschenk_statues
        self.zugewiesener_elf = zugewiesener_elf
        self.benoetigte_zeit = benoetigte_zeit

    def geschenke_zuweisung(self, zugewiesener_elf):
        self.zugewiesener_elf = zugewiesener_elf
        self.aktualisiere_geschenk_statues("zugewiesen")

    def aktualisiere_geschenk_statues(self, neuer_status):
        self.geschenk_statues = neuer_status

class Elf:
    def __init__(self, elf_id, name, Fachgebiet, anzahl_produzierter_geschenke, aktuelles_geschenk, elf_statues):
        self.elf_id = elf_id
        self.name = name
        self.Fachgebiet = Fachgebiet
        self.anzahl_produzierter_geschenke = anzahl_produzierter_geschenke
        self.aktuelles_geschenk = aktuelles_geschenk
        self.elf_statues = elf_statues

    def ist_beschaeftigt(self):
        return self.aktuelles_geschenk is not None

    def aktualisiere_elf_statues(self, neuer_status):
        self.elf_statues = neuer_status

    def berechnung_bauzeit(self):
        if not self.ist_beschaeftigt():
            return 0
        return self.aktuelles_geschenk.benoetigte_zeit
    