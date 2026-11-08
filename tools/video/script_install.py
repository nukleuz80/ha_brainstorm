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
                      "In fünf Minuten von HACS bis zur ersten Idee"),
                "say": "In diesem Video installierst du Brainstorm Hub. In wenigen Minuten geht "
                       "es von HACS bis zur ersten Idee im Dashboard.",
            },
        ],
    },
    {
        "title": "Voraussetzungen",
        "scenes": [
            {
                "v": ("bullets", "Das brauchst du", [
                    ("🏠", "<b>Home Assistant 2026.10</b> oder neuer"),
                    ("📦", "<b>HACS</b>, den Community Store für Home Assistant"),
                    ("🗣️", "Optional: <b>Alexa Media Player</b> für die Spracheingabe mit Alexa"),
                    ("🔒", "Kein Konto, kein Passwort: Brainstorm verbindet sich mit keinem fremden Dienst"),
                ], "HACS fehlt noch? Die Anleitung steht auf hacs.xyz."),
                "say": "Du brauchst Home Assistant ab Version 2026 Punkt 10 und HACS. Für Alexa "
                       "kommt optional die Integration Alexa Media Player dazu. Ein Konto oder "
                       "Passwort brauchst du nicht, Brainstorm verbindet sich mit keinem "
                       "fremden Dienst.",
            },
        ],
    },
    {
        "title": "HACS: Repository hinzufügen",
        "scenes": [
            {
                "v": ("ha", "Benutzerdefinierte Repositories", [
                    ("Repository", "https://github.com/nukleuz80/ha_brainstorm", True, ""),
                    ("Typ", "Integration", True, ""),
                ], "HACS ➔ Drei-Punkte-Menü oben rechts ➔ Benutzerdefinierte Repositories",
                   "Hinzufügen"),
                "say": "Öffne HACS und klicke oben rechts auf die drei Punkte, dann auf "
                       "Benutzerdefinierte Repositories. Trage die Adresse "
                       "github.com/nukleuz80/ha_brainstorm ein, wähle als Typ Integration und "
                       "klicke auf Hinzufügen.",
                "speak": "Öffne HACS und klicke oben rechts auf die drei Punkte, dann auf "
                         "Benutzerdefinierte Repositories. Trage die Adresse github punkt com "
                         "Schrägstrich nukleuz80 Schrägstrich ha underscore brainstorm ein, wähle "
                         "als Typ Integration und klicke auf Hinzufügen.",
            },
            {
                "v": ("bullets", "Noch schneller: der My-Button", [
                    ("🔗", "In der README auf <b>„Open in HACS“</b> klicken"),
                    ("🏠", "Deine Home Assistant-Adresse bestätigen"),
                    ("✅", "HACS öffnet Brainstorm Hub direkt"),
                ], "Die Adresse steht oben in der README auf GitHub."),
                "say": "Noch schneller geht es mit dem Knopf Open in HACS in der README. Er "
                       "öffnet Brainstorm direkt in deinem Home Assistant.",
            },
        ],
    },
    {
        "title": "Herunterladen",
        "scenes": [
            {
                "v": ("ha", "Brainstorm Hub", [
                    ("Version", "v1.7.22 (neueste)", True, "HACS bietet immer das neueste Release an"),
                    ("Kategorie", "Integration", False, ""),
                ], "HACS ➔ Brainstorm Hub suchen ➔ Herunterladen", "Herunterladen"),
                "say": "Suche in HACS nach Brainstorm Hub, öffne den Eintrag und klicke unten "
                       "rechts auf Herunterladen. HACS bietet dir immer das neueste Release an.",
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
                ], "HACS zeigt nach dem Download auch selbst einen Hinweis zum Neustart."),
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
                    ("🔔", "HACS meldet neue Versionen unter <b>Einstellungen</b>"),
                    ("⬇️", "<b>Aktualisieren</b> klicken, danach neu starten"),
                    ("📜", "Was neu ist, steht im <b>Changelog</b> der README"),
                    ("🧰", "Ohne HACS: Release laden, <code>custom_components/brainstorm</code> nach <code>/config/custom_components/</code> kopieren"),
                ], "Deine Ideen bleiben bei jedem Update erhalten."),
                "say": "Neue Versionen meldet HACS unter Einstellungen. Ein Klick auf "
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
