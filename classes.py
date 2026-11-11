class Geschenk:
    def __init__(self, geschenk_id, name, gewicht, kategorie, geschenk_statues, zugewiesener_elf, benoetigte_zeit):
        self.geschenk_id = geschenk_id
        self.name = name
        self.gewicht = gewicht
        self.kategorie = kategorie
        self.geschenk_statues = geschenk_statues
        self.zugewiesener_elf = zugewiesener_elf
        self.benoetigte_zeit = benoetigte_zeit

    def geschenk_zuweisung(self, zugewiesener_elf):
        self.zugewiesener_elf = zugewiesener_elf
        self.aktualisiere_geschenk_statues("zugewiesen")

    def aktualisiere_geschenk_statues(self, neuer_statues):
        self.geschenk_statues = neuer_statues

class Elf:
    def __init__(self, elf_id, name, Fachgebiet, anzahl_produzierter_geschenke, aktuelles_geschenk, elf_statues):
        self.elf_id = elf_id
        self.name = name 
        self.Fachgebiet = Fachgebiet 
        self.anzahl_produzierter_geschenke = anzahl_produzierter_geschenke 
        self.aktuelles_geschenk = aktuelles_geschenk 
        self.elf_statues = elf_statues

    def ist_beschaeftigt(self):
        return.self.aktuelles_geschenk is not None

    def aktualisiere_elf_statues(self, neuer_statues):
        self.elf_statues = neuer_statues

    def berechnung_bauzeit(self):
        if not self.ist_beschaeftigt():
            return 0
        return self.aktuelles_geschenk.benoetigte_zeit

class schlitten:
    def __init__(self, max_gewicht, aktuelles_gewicht, geladene_geschenke):
        self.max_gewicht = max_gewicht
        self.aktuelles_gewicht = aktuelles_gewicht
        self.geladene_geschenke = geladene_geschenke

    def pruefe_gewichtslimit(self, geschenk):
        if self.aktuelles_gewicht + geschenk.gewicht <= self.max_gewicht:
            return True
        else:
            return False