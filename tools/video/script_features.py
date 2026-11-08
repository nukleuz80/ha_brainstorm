"""Storyboard: Brainstorm Hub feature overview (German)."""
from __future__ import annotations

from pron import SPOKEN  # noqa: F401  (used by build.py)

TITLE = "Brainstorm Hub: Die wichtigsten Funktionen"
OUT_NAME = "brainstorm-features"
# README sections this video covers, check them on every release
COVERS = ["Highlights & Features", "Erinnerungen & Benachrichtigungen", "Privatsphäre & Freigaben", "Sprachsteuerung"]

CHAPTERS: list[dict] = [
    {
        "title": "Was ist Brainstorm?",
        "scenes": [
            {
                "v": ("shot", "crop_list.png", 450, [
                    ("💡", "Ideen, Aufgaben und Einkäufe <b>an einem Ort</b> in Home Assistant"),
                    ("🗣️", "Erfassen per <b>Stimme</b>, Karte oder Handy"),
                    ("🧠", "Brainstorm <b>sortiert selbst</b>: Kategorie, Priorität, Termin"),
                    ("🔒", "Läuft lokal, deine Daten bleiben bei dir"),
                ], "Eine Integration für Home Assistant, installierbar über HACS."),
                "say": "Das ist Brainstorm Hub. Brainstorm sammelt deine Ideen, Aufgaben und "
                       "Einkäufe an einem Ort in Home Assistant. Du sagst oder tippst einfach, "
                       "was dir einfällt, und Brainstorm sortiert es selbst ein.",
            },
        ],
    },
    {
        "title": "Erfassen per Stimme",
        "scenes": [
            {
                "v": ("grid", "Überall, wo du gerade bist", [
                    ("🗣️", "Alexa", "„Alexa, sage Brainstorm notiere Kellerlicht dimmen“"),
                    ("✨", "Assist", "„Notiere Backup der Datenbank erstellen“"),
                    ("🍎", "Siri", "Kurzbefehl, Action-Taste oder Rückseite antippen"),
                    ("🎙️", "Mikrofon", "Direkt in der Karte sprechen"),
                    ("🤖", "KI-Assistent", "„Die Hecke ist geschnitten“ hakt ab"),
                    ("⌨️", "Blitz-Idee", "Tippen und Enter, fertig"),
                ], "Jeder Eintrag merkt sich, woher er kam – bis zum einzelnen Echo."),
                "say": "Erfassen geht überall: mit Alexa am Echo, mit Assist, mit Siri auf dem "
                       "iPhone, über das Mikrofon in der Karte oder mit einem KI-Assistenten. "
                       "Jeder Eintrag merkt sich, woher er kam, bis zum einzelnen Echo.",
            },
        ],
    },
    {
        "title": "Versteht ganze Sätze",
        "scenes": [
            {
                "v": ("transform", "ich muss morgen unbedingt den Arzt anrufen", "Arzt anrufen",
                      ["⏰ Morgen 9:00", "🔴 Hoch", "📂 Alltag"],
                      "Füllwörter raus, Termin und Priorität erkannt."),
                "say": "Brainstorm versteht ganze Sätze. Aus: ich muss morgen unbedingt den Arzt "
                       "anrufen, wird: Arzt anrufen. Mit Termin morgen früh und hoher Priorität.",
            },
            {
                "v": ("transform", "dringend Garten: Rasenmäher reparieren", "Rasenmäher reparieren",
                      ["🔥 Dringend", "📂 Haus & Garten"],
                      "Kategorien erkennt Brainstorm an Stichwörtern wie Garten, Heizung oder Lampe."),
                "say": "Signalwörter wie dringend oder wichtig setzen die Priorität, und "
                       "Stichwörter wie Garten wählen die passende Kategorie.",
            },
        ],
    },
    {
        "title": "Die Listenkarte",
        "scenes": [
            {
                "v": ("shot", "crop_list.png", 450, [
                    ("⚡", "<b>Blitz-Idee</b> oben eintippen"),
                    ("🏷️", "<b>Kategorien</b> als Filter mit Zähler"),
                    ("🎨", "<b>Prioritäten</b> in Farbe, ein Klick schaltet weiter"),
                    ("🗣️", "<b>Herkunft</b> und Zeit an jedem Eintrag"),
                ], "Abhaken per Kreis, Sortieren per Ziehen, Bearbeiten per Stift."),
                "say": "Die Listenkarte zeigt alles im Dashboard. Oben tippst du eine Blitz-Idee, "
                       "darunter filterst du nach Kategorien. Jede Notiz zeigt Priorität, "
                       "Termin und Herkunft. Ein Klick auf den Kreis hakt sie ab.",
            },
        ],
    },
    {
        "title": "Unteraufgaben & Details",
        "scenes": [
            {
                "v": ("shot", "crop_projekte.png", 450, [
                    ("🌿", "<b>Unteraufgaben</b> direkt unter der Hauptaufgabe"),
                    ("✨", "Die <b>KI schlägt Unteraufgaben vor</b>, du wählst aus"),
                    ("📝", "<b>Beschreibung</b> mit Links und etwas Markdown"),
                    ("📎", "<b>Anhänge</b>: Fotos, PDFs, Screenshots"),
                ], "Lange Listen lassen sich einklappen."),
                "say": "Große Vorhaben teilst du in Unteraufgaben. Mit einer KI in Home Assistant "
                       "schlägt der Stern-Knopf passende Schritte vor. Dazu kommen eine "
                       "Beschreibung mit Links und Anhänge wie Fotos oder P D Fs.",
            },
        ],
    },
    {
        "title": "Die Mindmap",
        "scenes": [
            {
                "v": ("shot", "crop_mindmapzoom.png", 450, [
                    ("🧠", "Alle Ideen als <b>Gedankenlandkarte</b>"),
                    ("🖐️", "Verschieben, zoomen, <b>Zweige einklappen</b>"),
                    ("⌨️", "<b>Tastatur</b>: Tab, Enter, Strg+Z"),
                    ("🖼️", "Vorlagen, zehn Formen, <b>Bild-Export</b>"),
                ], "Dringende Notizen pulsieren wie ein kleines Feuer."),
                "say": "Die Mindmap zeigt deine Ideen als Gedankenlandkarte. Unteraufgaben "
                       "hängen als Äste an ihrer Idee. Du verschiebst und zoomst mit Maus oder "
                       "Finger, und mit Vorlagen und Formen exportierst du das Ganze als Bild.",
            },
        ],
    },
    {
        "title": "Erinnerungen",
        "scenes": [
            {
                "v": ("grid", "Brainstorm denkt mit", [
                    ("⏰", "Termine", "„erinnere mich morgen um 8 an den Müll“"),
                    ("🔊", "Alexa-Ansage", "Der Echo sagt es an, das Handy folgt bei Bedarf"),
                    ("📱", "Benachrichtigung", "Mit Knöpfen für Erledigt und Später"),
                    ("🏠", "Orte", "„wenn ich bei Edeka bin, an die Milch“"),
                    ("☀️", "Briefing", "Täglich ein kurzer Überblick, dazu ein Wochenrückblick"),
                    ("🌙", "Ruhezeit", "Nachts bleibt alles still"),
                ], "Auf Wunsch auch als echte Alexa-Erinnerung oder im Kalender."),
                "say": "Hat eine Notiz einen Termin, erinnert Brainstorm dich: per Alexa-Ansage, "
                       "per Benachrichtigung aufs Handy, oder wenn du an einem Ort ankommst. "
                       "Dazu gibt es ein tägliches Briefing und eine Ruhezeit für die Nacht.",
            },
        ],
    },
    {
        "title": "Alexa-Skill & Echo Show",
        "scenes": [
            {
                "v": ("speech", [
                    ("du", "Alexa, sage Brainstorm Ansage Einkauf."),
                    ("alexa", "In Einkauf: Milch und Duschgel."),
                    ("du", "Alexa, sage Brainstorm erledigt Milch."),
                ], "Mit eigenem Skill: ein Satz, eine Antwort"),
                "say": "Mit deinem eigenen Alexa-Skill antwortet Alexa mit genau einem Satz. Du "
                       "lässt dir Listen vorlesen und hakst per Stimme ab. Ein Echo Show zeigt "
                       "die Listen sogar zum Antippen. Wie das geht, zeigt ein eigenes Video.",
            },
        ],
    },
    {
        "title": "Erledigt & Ergebnis",
        "scenes": [
            {
                "v": ("shot", "crop_done.png", 330, [
                    ("✅", "Erledigtes bleibt sichtbar und lässt sich <b>wiederherstellen</b>"),
                    ("📌", "<b>Ergebnis-Notiz</b>: was daraus geworden ist"),
                    ("🔧", "<b>In Arbeit</b>-Abzeichen mit Namen"),
                    ("🤖", "Ideal als <b>Backlog für Coding-KIs</b> wie Claude Code"),
                ], "Auf Wunsch räumt Brainstorm Erledigtes nach einer Anzahl Tage selbst auf."),
                "say": "Erledigtes bleibt sichtbar und lässt sich wiederherstellen. Eine "
                       "Ergebnis-Notiz zeigt, was daraus geworden ist. So eignet sich eine "
                       "Kategorie sogar als Aufgabenliste für Coding-KIs wie Claude Code.",
            },
        ],
    },
    {
        "title": "Verbunden mit allem",
        "scenes": [
            {
                "v": ("grid", "Passt zu deinem Smarthome", [
                    ("📋", "To-do-Listen", "Jede Kategorie ist eine echte To-do-Liste in Home Assistant"),
                    ("🛒", "Bring!", "Einkaufslisten in beide Richtungen"),
                    ("🔁", "Gekoppelte Listen", "Google Tasks, Todoist und andere"),
                    ("📝", "Markdown", "Export für Obsidian und Co."),
                    ("💾", "JSON", "Sichern und auf ein anderes System umziehen"),
                    ("🧩", "Automationen", "Dienste, Ereignisse und ein Sensor"),
                ], "Alles nach den Richtlinien von Home Assistant gebaut."),
                "say": "Jede Kategorie ist eine echte To-do-Liste in Home Assistant. Brainstorm "
                       "spricht mit Bring, Google Tasks und Todoist, exportiert nach Markdown "
                       "und bietet Dienste und Ereignisse für deine Automationen.",
            },
        ],
    },
    {
        "title": "Privatsphäre & Freigaben",
        "scenes": [
            {
                "v": ("bullets", "Jedem das Seine", [
                    ("👤", "Jeder Eintrag gehört der Person, die ihn angelegt hat"),
                    ("👥", "<b>Freigeben</b> pro Eintrag oder Kategorie: Ansehen oder Bearbeiten"),
                    ("🗣️", "<b>Echos Personen zuordnen</b>: vorgelesen wird nur das Eigene"),
                    ("☑️", "Mehrere Einträge auf einmal erledigen, verschieben, freigeben"),
                ], "Ausgeschaltet sehen alle Benutzer alle Einträge."),
                "say": "Für die Familie gibt es Privatsphäre: Jeder Eintrag gehört seiner Person "
                       "und lässt sich gezielt freigeben. Ordnest du Echos Personen zu, liest "
                       "Alexa jedem nur seine eigenen Einträge vor.",
            },
        ],
    },
    {
        "title": "Loslegen",
        "scenes": [
            {
                "v": ("bullets", "In drei Schritten startklar", [
                    ("1", "In <b>HACS</b> das Repository <code>nukleuz80/ha_brainstorm</code> hinzufügen und installieren"),
                    ("2", "Home Assistant neu starten, Integration <b>Brainstorm Hub</b> hinzufügen"),
                    ("3", "Karte <b>Brainstorm Card</b> ins Dashboard ziehen – fertig"),
                ], "Anleitung und Videos: github.com/nukleuz80/ha_brainstorm"),
                "say": "Installiert ist Brainstorm in wenigen Minuten über HACS. Danach fügst du "
                       "die Integration hinzu und ziehst die Karte ins Dashboard. Die Anleitung "
                       "findest du auf GitHub. Viel Spaß mit deinen Ideen!",
            },
        ],
    },
]
