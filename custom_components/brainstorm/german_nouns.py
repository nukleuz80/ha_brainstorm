"""Common German nouns of everyday notes, used to capitalize spoken text."""
from __future__ import annotations

# Only words that are nouns nearly every time. Words that are just as often a verb
# or an adjective ('essen', 'leben', 'weg', 'kosten') are left out on purpose.
GERMAN_NOUNS: frozenset[str] = frozenset(
    """
    abfall abfluss abo abrechnung absage adapter adresse akku akte aktie alarm album
    allergie ampel amt ananas angebot anhänger anleitung anmeldung anruf anschluss
    anschrift antrag antwort anwalt anzeige anzug apfel apotheke app apps arbeit
    arbeitsplatte arzt ast aufgabe aufkleber aufzug auge ausflug ausweis auto autos
    autobahn
    baby bäcker bäckerei bad badewanne badezimmer bahn bahnhof balkon ball banane
    bank batterie batterien bauch baum bäume baumarkt beamer becher beet behörde beleg
    beleuchtung benzin berg bericht besen besuch bett bettwäsche bewegungsmelder
    bewerbung bibliothek bier bild bildschirm birne blatt blech blume blumen
    blumenerde bohrer bohrmaschine boiler boot brief briefkasten briefmarke brille
    brot brötchen bruder brücke brunnen buch bücher bügeleisen büro bürste bus butter
    café chef computer creme
    dach dachboden dachrinne datei daten datenbank decke deckel dichtung dienst dose
    drucker dübel dünger dusche
    ehefrau ehemann ei eier eimer einfahrt eingang einkauf einkaufsliste einladung
    einstellung eis elektriker eltern email ende enkel entwurf erde erinnerung
    ersatzteil essig etage
    fahrrad fahrschule fahrzeug familie farbe fassade feier feiertag fehler feld
    fenster ferien fernbedienung fernseher feuer feuerlöscher feuerwehr filter firma
    fisch flasche flaschen fleisch fliese fliesen flug flughafen flur fluss flyer
    foto fotos frage freund freundin friseur frühstück führerschein funktion futter
    gabel garage garantie garten gartenhaus gas gast gäste gebühr geburtstag gemüse
    gerät geräte gericht geschäft geschenk geschirr geschirrspüler geschwister gesicht
    gespräch getränk getränke gewächshaus gießkanne gitarre glas glühbirne gras grill
    grundschule gurke gürtel gutschein
    haar haare hafen hähnchen haken halle handschuhe handtuch handwerker handy haus
    hausarzt hausaufgaben haustür hecke heckenschere hefe heft heizkörper heizung hemd
    herd herbst hilfe himmel hochbeet hof holz homepage hose hotel hund hunde
    idee impfung impfpass inspektion internet
    jacke jahr joghurt
    kabel kaffee kaffeemaschine kalender kamera kamin kanzlei karte karten kartoffel
    kartoffeln karton käse kasse kasten katze kaution keller kerze kette kind kinder
    kindergarten kino kirche kissen kiste kisten kita klavier kleid kleidung klempner
    klingel klingelton klinik klo kochtopf koffer kollege kollegin kompost konto
    kopf kopfhörer korb krankenhaus krankenkasse krippe küche kuchen kühlschrank kunde
    kündigung kürbis kürbisse
    ladegerät ladekabel lager lampe lampen laptop laub laubsauger lautsprecher
    lebensmittel lehrer lehrerin leiter leitung licht lieferung liste listen löffel
    lüfter lüftung
    mähroboter mail mails maler mama mantel markt maschine material matratze mauer
    mehl meldung messer miete milch minute mikrofon mittagessen möbel modem monitor
    motor mücke müll mülltonne museum musik mütze
    nachbar nachbarin nachricht nagel nägel name nudeln netz netzteil netzwerk notar
    notiz nudel nummer
    obst ofen öl ölwechsel oma onkel opa ordner ort
    paket papa papier parkplatz partner party pass passwort pfanne pfeffer pflanze
    pflaster pflege pflegedienst pizza platte platz pool post postkarte praxis preis
    programm projekt prüfung pumpe putzmittel
    quittung
    rad radio rahmen rasen rasenmäher rasierer rat raum rauchmelder rechnung
    rechner regal regen regenrinne reifen reinigung reis reise reisepass reparatur
    report restaurant restmüll rezept rohr rolle rollladen roller rose rosen router
    rucksack
    saft sahne salat salbe salz samen sand sauna schalter schere schild schlafzimmer
    schloss schlüssel schornstein schrank schraube schraubenzieher
    schreibtisch schublade schuh schuhe schule schüler schulranzen schuppen schwester
    see seife seite sekt sensor server sessel sicherung sieb skript skill socke
    socken sofa solaranlage sommer sonne sonnenschirm spiegel spiel spielzeug
    spielplatz sportverein spülmaschine spülmittel stadt stall staubsauger steckdose
    stecker stein steuer steuererklärung stift stock strauch straße strom stromzähler
    stuhl stunde suppe supermarkt
    tablet tablette tabletten tag tanke tankstelle tante tapete tasche tasse tastatur
    taxi tee teich teller teppich termin terrasse thermostat ticket tier tierarzt
    tisch tochter toilette tomate tomaten ton tonne topf tor torte treppe trockner
    tür türen türklingel türschloss tüte tüv
    uhr uhren umzug unfall unkraut unterlagen unterschrift update urlaub
    vase vater verein vereinbarung vermieter vertrag versicherung videos vorhang
    vorschlag vorsorge
    waage wagen wald wand wäsche wäscheständer waschmaschine wasser wasserhahn
    webseite website wecker weihnachten wein werkstatt werkzeug wetter wiese wlan
    wochenende wohnung wohnzimmer wolle wurst
    zahl zahnarzt zahnbürste zahnpasta zange zaun zeit zeitung zelt zentrale zettel
    ziel zimmer zitrone zucker zug zwiebel zwiebeln
    """.split()
)

# Plurals with 'n' that are at least as often the verb ('blumen pflanzen')
AMBIGUOUS_PLURALS: frozenset[str] = frozenset(
    {
        "bitten", "duschen", "fragen", "pflanzen", "pflegen", "pumpen", "reisen",
        "schrauben", "bürsten", "feiern", "farben", "melden", "enden", "listen",
        "seiten", "zahlen",
    }
)
