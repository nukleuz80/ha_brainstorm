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
                    ("🔍", "<b>Suche</b> beim Tippen, auch nach #Tags"),
                ], "Abhaken per Kreis, alles Weitere hinter den drei Punkten."),
                "say": "Die Listenkarte zeigt alles im Dashboard. Oben tippst du eine Blitz-Idee, "
                       "darunter filterst du nach Kategorien, und die Suche findet jede Notiz "
                       "schon beim Tippen, auch nach Tags. Ein Klick auf den Kreis hakt sie ab, "
                       "die drei Punkte öffnen alles Weitere.",
            },
            {
                "v": ("grid", "So viel, wie du brauchst", [
                    ("🌱", "Einsteiger", "Eingabe, Kategorien, Abhaken, Suche"),
                    ("🙂", "Normal", "Dazu Unterpunkte, Marker, Anhänge und Ansichten"),
                    ("🚀", "Profi", "Alle Felder und Funktionen"),
                    ("📱", "Pro Karte", "Das Küchentablet bleibt einfach"),
                    ("🔒", "Nichts geht verloren", "Gesetzte Werte bleiben sichtbar"),
                    ("➕", "Mehr Felder …", "Zeigt im Dialog trotzdem alles"),
                ], "Einstellbar unter Konfigurieren, Allgemeine Einstellungen."),
                "say": "Wie viel die Karten zeigen, bestimmst du selbst. Einsteiger sehen nur das "
                       "Wichtigste. Die Stufe Normal bringt Unterpunkte, Marker und Ansichten, "
                       "und Profi zeigt alles. Jede Karte kann ihre eigene Stufe haben, etwa ein einfaches "
                       "Küchentablet.",
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
                "v": ("shot", "crop_mmprojekte.png", 450, [
                    ("🧠", "Alle Ideen als <b>Gedankenlandkarte</b>"),
                    ("⭐", "<b>Marker</b>, Fortschritt und <b>Nummerierung</b> 1., 1.1"),
                    ("🔗", "<b>Querverbindungen</b> und Sprechblasen"),
                    ("🎯", "<b>Fokus</b> auf einen einzelnen Zweig"),
                ], "Jede Notiz: ✓ Erledigt, 🌿 Unteridee, ✏️ Bearbeiten, ⋯ für den Rest."),
                "say": "Die Mindmap zeigt deine Ideen als Gedankenlandkarte. Unteraufgaben "
                       "hängen als Äste an ihrer Idee und lassen sich nummerieren. Marker wie "
                       "Stern oder Fragezeichen, Querverbindungen und Callouts machen sie "
                       "übersichtlich, und der Fokus zeigt nur einen Zweig.",
            },
            {
                "v": ("shot", "crop_kanban.png", 450, [
                    ("◎", "<b>Rund um die Mitte</b>, Baum oder Organigramm"),
                    ("☰", "<b>Gliederung</b> wie in einem Outliner"),
                    ("▥", "<b>Kanban</b>: offen, in Arbeit, wartet, erledigt"),
                    ("📅", "<b>Zeitleiste</b> und Eisenhower-Matrix"),
                ], "Ein Knopf unten rechts schaltet die Ansicht um."),
                "say": "Dieselben Notizen gibt es in sieben Ansichten: rund um die Mitte, als "
                       "Baum, Organigramm oder Gliederung, als Kanban nach Status, als "
                       "Zeitleiste nach Fälligkeit oder als Eisenhower-Matrix.",
            },
            {
                "v": ("grid", "Noch mehr auf der Mindmap", [
                    ("🔍", "Suchen & Filtern", "Nach Priorität, Markern, Tags und Fälligkeit"),
                    ("🎨", "Regeln", "Alles Dringende rot, #garten grün mit Stern"),
                    ("▶️", "Präsentieren", "Vollbild, Notiz für Notiz"),
                    ("⚡", "Brainstorm-Modus", "Mit Timer, jedes Enter eine Notiz"),
                    ("📄", "Export", "Bild, PDF, Markdown, OPML und FreeMind"),
                    ("✨", "KI-Hilfe", "Fasst Äste zusammen, ordnet zu, baut ganze Maps"),
                ], "Vorlagen wie SWOT-Analyse oder Packliste fügen fertige Zweige ein."),
                "say": "Dazu kommen Suchen und Filtern, Regeln, die passende Notizen einfärben, "
                       "ein Präsentationsmodus und ein Brainstorm-Modus mit Timer. Exportieren "
                       "kannst du als Bild, PDF, Markdown, OPML oder FreeMind, und die KI fasst "
                       "einen ganzen Ast in ein paar Sätzen zusammen.",
            },
        ],
    },
    {
        "title": "Gemeinsam & mit KI",
        "scenes": [
            {
                "v": ("shot", "crop_social.png", 450, [
                    ("🗳️", "<b>Abstimmen</b> mit Stimmen pro Person, auch verdeckt"),
                    ("❤️", "<b>Reaktionen</b> wie Herz, Daumen oder Wichtig"),
                    ("🗺️", "<b>Minimap</b> zeigt, wo du gerade auf der Mindmap bist"),
                    ("🏆", "Nach der Runde nach <b>Stimmen sortieren</b>"),
                ], "Abstimmung starten: 🗳️ unten rechts oder die Taste V."),
                "say": "Brainstorm ist auch für die ganze Familie gemacht. Startet eine Abstimmung, "
                       "verteilt jeder seine Stimmen auf die besten Ideen, auf Wunsch verdeckt. "
                       "Mit Reaktionen wie Herz oder Daumen zeigst du schnell, was dir gefällt. "
                       "Auf großen Karten hilft dir die Minimap.",
            },
            {
                "v": ("shot", "crop_comments.png", 450, [
                    ("💬", "<b>Kommentare</b> an jeder Notiz, auch in der Listenkarte"),
                    ("📣", "<b>@Name</b> erwähnt eine Person"),
                    ("📱", "Erwähnte bekommen eine <b>Benachrichtigung</b>"),
                    ("🔒", "Nur wer die Notiz sehen darf, wird benachrichtigt"),
                ], "Die Sprechblase an der Notiz zeigt, wie viele Kommentare es gibt."),
                "say": "An jeder Notiz könnt ihr diskutieren. Erwähnst du jemanden mit dem Klammeraffen "
                       "und seinem Namen, bekommt diese Person eine Benachrichtigung aufs Handy, aber nur, wenn sie "
                       "die Notiz auch sehen darf.",
            },
            {
                "v": ("shot", "crop_aimap.png", 450, [
                    ("✨", "<b>Map aus Thema</b>: ein Stichwort oder ein langer Text"),
                    ("🌳", "Die KI baut bis zu <b>drei Ebenen</b>"),
                    ("☑️", "Vor dem Übernehmen <b>auswählen und umbenennen</b>"),
                    ("🔁", "<b>Neue Vorschläge</b>, wenn es noch nicht passt"),
                ], "Braucht eine KI in Home Assistant, zum Beispiel über AI Task."),
                "say": "Und wenn dir der Anfang fehlt: Gib der KI ein Thema wie Sommerfest im "
                       "Garten planen, und sie entwirft eine ganze Mindmap. Du hakst ab, was du "
                       "nicht willst, änderst Texte und übernimmst den Rest mit einem Klick.",
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
                    ("🔁", "Wiederkehrend", "Täglich, wöchentlich, monatlich: abgehakt kommt sie wieder"),
                    ("🌙", "Ruhezeit", "Nachts bleibt alles still"),
                ], "Auf Wunsch auch als echte Alexa-Erinnerung oder im Kalender."),
                "say": "Hat eine Notiz einen Termin, erinnert Brainstorm dich: per Alexa-Ansage, "
                       "per Benachrichtigung aufs Handy, oder wenn du an einem Ort ankommst. "
                       "Wiederkehrende Aufgaben kommen nach dem Abhaken von selbst wieder, "
                       "und nachts bleibt alles still.",
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
                    ("1", "In <b>HACS</b> nach <b>Brainstorm Hub</b> suchen und installieren"),
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
