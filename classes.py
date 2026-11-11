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
        return self.aktuelles_geschenk is not None

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

    def lade_geschenk(self, geschenk):
        if self.pruefe_gewichtslimit(geschenk):
            self.geladene_geschenke.append(geschenk)
            self.aktuelles_gewicht += geschenk.gewicht
            return True
        else:
            return False

    def starte_auslieferung(self):
        if self.aktuelles_gewicht > 0:
            self.geladene_geschenke.clear()
            self.aktuelles_gewicht = 0
            return True
        else:
            return False
        
class Spiel:
    def __init__(self, aktueller_tag, max_tag, geschenke, elfen, schlitten, spielstatus):
        self.aktueller_tag = aktueller_tag
        self.max_tag = max_tag
        self.geschenke = geschenke
        self.elfen = elfen
        self.schlitten = schlitten
        self.spielstatus = spielstatus

    def initialisiere_spiel(self):
        self.aktueller_tag = 1
        self.spielstatus = "gestartet"
        for elf in self.elfen:
            elf.aktuelles_geschenk = None
            elf.elf_statues = "bereit"
        for geschenk in self.geschenke:
            geschenk.zugewiesener_elf = None
            geschenk.geschenk_statues = "nicht zugewiesen"

    def starte_spiel(self):
        self.initialisiere_spiel()
        while self.aktueller_tag <= self.max_tag:
            self.verarbeite_tag()
            self.aktueller_tag += 1
            self.spielstatus = "in Bearbeitung"

    def stoppe_spiel(self):
        self.spielstatus = "gestoppt"

    def beende_spiel(self):
        self.spielstatus = "beendet"

    def puefe_spielende(self):
        if self.aktueller_tag > self.max_tag:
            self.beende_spiel()
            return True
        return False

    def schnelldurchlauf(self):
        self.spielstatus = "Schnelldurchlauf"
        while self.spielstatus == "Schnelldurchlauf":
            self.fuhre_tagesablauf_aus() 
            if self.pruefe_spielende():
                break
