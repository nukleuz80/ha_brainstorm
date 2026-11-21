"""Storyboard: installing Brainstorm Hub (German)."""
from __future__ import annotations

from pron import SPOKEN  # noqa: F401  (used by build.py)

TITLE = "Brainstorm Hub installieren"
OUT_NAME = "brainstorm-installation"
# README sections this video covers, check them on every release
COVERS = ["Installation", "Konfiguration", "Dashboard Cards einbinden"]

CHAPTERS: list[dict] = [
    {
        "title": "Einleitung",
        "scenes": [
            {
                "v": ("title", "Brainstorm Hub installieren",
                      "In fünf Minuten vom Marketplace bis zur ersten Idee"),
                "say": "In diesem Video installierst du Brainstorm Hub. In wenigen Minuten geht "
                       "es von der Installation bis zur ersten Idee im Dashboard.",
            },
        ],
    },
    {
        "title": "Voraussetzungen",
        "scenes": [
            {
                "v": ("bullets", "Das brauchst du", [
                    ("🏠", "<b>Home Assistant 2026.10</b> oder neuer"),
                    ("📦", "Den <b>Marketplace</b> unter Einstellungen, eingebaut ab 2026.11"),
                    ("🗣️", "Optional: <b>Alexa Media Player</b> für die Spracheingabe mit Alexa"),
                    ("🔒", "Kein Konto, kein Passwort: Brainstorm verbindet sich mit keinem fremden Dienst"),
                ], "Unter 2026.10 installierst du über HACS, die Schritte sind fast gleich."),
                "say": "Du brauchst Home Assistant ab Version 2026 Punkt 10. Installiert wird in "
                       "den Einstellungen über den Marketplace. Für Alexa "
                       "kommt optional die Integration Alexa Media Player dazu. Ein Konto oder "
                       "Passwort brauchst du nicht, Brainstorm verbindet sich mit keinem "
                       "fremden Dienst.",
            },
        ],
    },
    {
        "title": "Marketplace öffnen",
        "scenes": [
            {
                "v": ("menu", "Einstellungen", [
                    ("Geräte & Dienste", False),
                    ("Automationen & Szenen", False),
                    ("Apps", False),
                    ("Marketplace", True),
                    ("Dashboards", False),
                ], "Einstellungen ➔ Marketplace ➔ Durchstöbern",
                   "Brainstorm Hub steht in der Standardliste, ein eigenes Repository brauchst du nicht."),
                "say": "Öffne die Einstellungen und tippe auf Marketplace. Wechsle unten zu "
                       "Durchstöbern und suche nach Brainstorm Hub. Es steht in der Standardliste, "
                       "du musst also kein Repository hinzufügen.",
            },
        ],
    },
    {
        "title": "Installieren",
        "scenes": [
            {
                "v": ("ha", "Brainstorm Hub", [
                    ("Status", "Nicht installiert", False, "Die neueste Version steht zur Installation bereit"),
                    ("Typ", "Integration", False, "Von der Community erstellt, Quellcode auf GitHub"),
                ], "Marketplace ➔ Durchstöbern ➔ Brainstorm Hub", "Installieren"),
                "say": "Öffne den Eintrag und tippe auf Installieren. Du bekommst immer die "
                       "neueste Version. Eine ältere wählst du bei Bedarf über das "
                       "Drei-Punkte-Menü.",
            },
        ],
    },
    {
        "title": "Neustart",
        "scenes": [
            {
                "v": ("bullets", "Home Assistant neu starten", [
                    ("🔁", "Einstellungen ➔ System ➔ oben rechts <b>Neu starten</b>"),
                    ("🧩", "Erst danach kennt Home Assistant die Integration"),
                    ("🎴", "Die <b>Karten kommen mit</b>: kein Kopieren, kein Ressourcen-Eintrag"),
                ], "Danach findest du Brainstorm Hub unter Geräte & Dienste."),
                "say": "Starte Home Assistant jetzt neu, unter Einstellungen, System, Neu starten. "
                       "Die Karten kommen mit der Integration. Du musst nichts kopieren und "
                       "keine Ressource eintragen.",
            },
        ],
    },
    {
        "title": "Integration hinzufügen",
        "scenes": [
            {
                "v": ("ha", "Integration hinzufügen", [
                    ("Suche", "Brainstorm", True, ""),
                    ("Ergebnis", "💡 Brainstorm Hub", True, ""),
                ], "Einstellungen ➔ Geräte & Dienste ➔ Integration hinzufügen", "Auswählen"),
                "say": "Öffne Einstellungen, Geräte und Dienste, und klicke unten rechts auf "
                       "Integration hinzufügen. Suche nach Brainstorm und wähle Brainstorm Hub.",
            },
        ],
    },
    {
        "title": "Ersteinrichtung",
        "scenes": [
            {
                "v": ("ha", "Brainstorm Hub einrichten", [
                    ("Kategorien ohne Notizen (0) ausblenden", "an", False,
                     "Blendet leere Kategorien auf den Karten aus"),
                    ("Ideen automatisch als Markdown-Dateien exportieren", "aus", True,
                     "Pro Kategorie eine Datei, z. B. für Obsidian"),
                    ("Dateipfad für Markdown-Dateien", "/config/brainstorm", False, ""),
                ], "Keine Einstellung ist Pflicht – die Vorgaben passen für alle", "Absenden"),
                "say": "Die Ersteinrichtung fragt nur drei Dinge: ob leere Kategorien versteckt "
                       "werden, und ob Brainstorm deine Ideen als Markdown-Dateien exportiert. "
                       "Nichts davon ist Pflicht. Klicke einfach auf Absenden.",
            },
        ],
    },
    {
        "title": "Karte ins Dashboard",
        "scenes": [
            {
                "v": ("shot", "crop_list.png", 450, [
                    ("✏️", "Dashboard ➔ <b>Bearbeiten</b>"),
                    ("➕", "<b>Karte hinzufügen</b> und nach „Brainstorm“ suchen"),
                    ("🎴", "<b>Brainstorm Card</b> auswählen und speichern"),
                    ("⚙️", "Optionen im Karten-Editor, z. B. Titel und Farben"),
                ], "Im Karten-Editor siehst du gleich eine Vorschau."),
                "say": "Öffne dein Dashboard, klicke auf Bearbeiten und dann auf Karte "
                       "hinzufügen. Suche nach Brainstorm und wähle die Brainstorm Card. Schon "
                       "hast du die Listenkarte mit Schnelleingabe und Kategorien.",
            },
            {
                "v": ("yaml", "Oder per YAML", "type: custom:brainstorm-card\ntitle: Brainstorm Hub",
                      "Alle Kartenoptionen stehen in der Anleitung."),
                "say": "Wer lieber YAML schreibt, braucht nur zwei Zeilen: den Typ "
                       "custom:brainstorm-card und einen Titel.",
                "speak": "Wer lieber YAML schreibt, braucht nur zwei Zeilen: den Typ "
                         "custom brainstorm card, und einen Titel.",
            },
        ],
    },
    {
        "title": "Mindmap-Karte",
        "scenes": [
            {
                "v": ("shot", "crop_mindmapzoom.png", 450, [
                    ("🧠", "<b>Brainstorm Mindmap Card</b> auf dieselbe Weise hinzufügen"),
                    ("🖥️", "Ideal als <b>Panel-Ansicht</b> auf Tablet oder Monitor"),
                    ("🎨", "Vorlagen: Standard, Klar, Skizze, Neon"),
                    ("⛶", "Vollbild per Knopf oben rechts"),
                ], "Die Listenkarte hat außerdem einen Mindmap-Knopf eingebaut."),
                "say": "Genauso fügst du die Mindmap-Karte hinzu. Sie wirkt am besten als "
                       "Panel-Ansicht auf einem Tablet oder Monitor. Vier Vorlagen bestimmen "
                       "das Aussehen.",
            },
        ],
    },
    {
        "title": "Die erste Idee",
        "scenes": [
            {
                "v": ("transform", "Garten: Baum schneiden", "Baum schneiden",
                      ["📂 Haus & Garten", "🟡 Mittel", "💻 Dashboard"],
                      "Ein Wort mit Doppelpunkt vorne wählt die Kategorie."),
                "say": "Zeit für die erste Idee. Tippe oben in die Karte: Garten, Doppelpunkt, "
                       "Baum schneiden, und drücke Enter. Brainstorm legt Baum schneiden in "
                       "der Kategorie Haus und Garten ab.",
            },
        ],
    },
    {
        "title": "Konfigurieren",
        "scenes": [
            {
                "v": ("grid", "Brainstorm Hub ➔ Konfigurieren", [
                    ("📁", "Kategorien", "Anlegen, umbenennen, sortieren"),
                    ("🎨", "Kategorie-Design", "Icon und Farbe pro Kategorie"),
                    ("⚙️", "Allgemein", "Standard-Kategorie, Text-Optimierung, Echos"),
                    ("🗣️", "Alexa", "Spracheingabe und eigener Skill"),
                    ("⏰", "Erinnerungen", "Kanäle, Ruhezeit, Briefing"),
                    ("👥", "Privatsphäre", "Besitzer und Freigaben"),
                ], "Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub ➔ Konfigurieren"),
                "say": "Alles Weitere stellst du unter Konfigurieren ein: Kategorien und ihre "
                       "Farben, die Text-Optimierung, Alexa, Erinnerungen und die Privatsphäre. "
                       "Die Vorgaben funktionieren aber schon so.",
            },
        ],
    },
    {
        "title": "Updates",
        "scenes": [
            {
                "v": ("bullets", "Immer aktuell bleiben", [
                    ("🔔", "Neue Versionen erscheinen als Update unter <b>Einstellungen</b>"),
                    ("⬇️", "<b>Aktualisieren</b> klicken, danach neu starten"),
                    ("📜", "Was neu ist, steht im <b>Changelog</b> der README"),
                    ("🧰", "Ohne Marketplace: Release laden, <code>custom_components/brainstorm</code> nach <code>/config/custom_components/</code> kopieren"),
                ], "Deine Ideen bleiben bei jedem Update erhalten."),
                "say": "Neue Versionen erscheinen als Update unter Einstellungen. Ein Klick auf "
                       "Aktualisieren und ein Neustart, fertig. Deine Ideen bleiben dabei "
                       "erhalten.",
            },
        ],
    },
    {
        "title": "Wie geht's weiter?",
        "scenes": [
            {
                "v": ("bullets", "Nächste Schritte", [
                    ("🎬", "Video: <b>Die wichtigsten Funktionen</b>"),
                    ("🗣️", "Video: <b>Eigener Alexa-Skill</b>"),
                    ("📘", "<b>Anleitung mit Beispielen</b> im Ordner docs"),
                    ("💬", "Fragen und Ideen als <b>Issue auf GitHub</b>"),
                ], "github.com/nukleuz80/ha_brainstorm"),
                "say": "Das war's! Wie es weitergeht, zeigen die Videos zu den wichtigsten "
                       "Funktionen und zum eigenen Alexa-Skill. Viel Spaß mit Brainstorm!",
            },
        ],
    },
]
