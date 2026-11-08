"""Storyboard: privacy, sharing and the backlog for coding AIs (German)."""
from __future__ import annotations

from pron import SPOKEN

TITLE = "Brainstorm Hub: Privatsphäre, Freigaben & KI-Backlog"
OUT_NAME = "brainstorm-privatsphaere"
# README sections this video covers, check them on every release
COVERS = ["Privatsphäre & Freigaben", "Brainstorm als Aufgabenliste für Coding-KIs",
          "Brainstorm › Privatsphäre & Benutzer", "Brainstorm › Echos & Apps zuordnen"]

PATH = "Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub ➔ Konfigurieren"

CHAPTERS: list[dict] = [
    {
        "title": "Privatsphäre",
        "scenes": [
            {
                "v": ("title", "Privatsphäre, Freigaben & KI-Backlog", "Jedem seine Liste, gemeinsam wo es passt"),
                "say": "Im Haushalt teilen sich oft mehrere Personen einen Home Assistant. In diesem "
                       "Video zeige ich dir, wie jeder seine eigenen Einträge bekommt, wie du gezielt "
                       "teilst und wie eine Coding-KI wie Claude Code nur ihre Aufgaben sieht.",
            },
        ],
    },
    {
        "title": "Einschalten",
        "scenes": [
            {
                "v": ("switches", "Brainstorm › Privatsphäre & Benutzer", [
                    ("Einträge privat halten", True, True,
                     "Jede Person sieht nur ihre eigenen Einträge und was mit ihr geteilt wurde"),
                    ("Hauptbenutzer", "Jan", True, "Besitzt alle vorhandenen Einträge"),
                    ("Weiter in Markdown-Dateien exportieren", False, False,
                     "Diese Dateien wären für alle mit Zugriff auf den Config-Ordner lesbar"),
                    ("Diese Benutzer für Freigaben anbieten", "Jan, Lenja, Claude", False,
                     "Blendet technische Konten wie MQTT aus"),
                ], PATH + " ➔ Privatsphäre & Benutzer", "Ausgeschaltet sehen alle Benutzer alle Einträge."),
                "say": "Standardmäßig sehen alle alles. Unter Privatsphäre und Benutzer schaltest du "
                       "Einträge privat halten ein und wählst einen Hauptbenutzer. Ihm gehören alle "
                       "Einträge, die es schon gibt. Ab dann gehört jeder neue Eintrag der Person, "
                       "die ihn anlegt.",
            },
        ],
    },
    {
        "title": "Freigeben",
        "scenes": [
            {
                "v": ("grid", "Gezielt teilen", [
                    ("👆", "Ein Eintrag", "Lange drücken ➔ 👥 Freigeben"),
                    ("📂", "Eine Kategorie", "Kategorie wählen ➔ 👥 freigeben, gilt auch für spätere Einträge"),
                    ("☑️", "Mehrere Einträge", "Auswählen, dann auf einmal erledigen, verschieben, freigeben"),
                    ("👀", "Ansehen", "Nur lesen"),
                    ("✏️", "Bearbeiten", "Ändern und abhaken"),
                    ("🔑", "Besitzer", "Löschen und Weitergeben bleiben bei dir"),
                ], "Freigeben geht pro Person oder für alle Benutzer."),
                "say": "Teilen kannst du einen einzelnen Eintrag, eine ganze Kategorie oder mehrere "
                       "Einträge auf einmal. Pro Person wählst du Ansehen oder Bearbeiten. Löschen "
                       "und Weitergeben bleiben immer beim Besitzer.",
            },
            {
                "v": ("bullets", "In fremde Listen schreiben", [
                    ("🛒", "Lenja gibt dir die Kategorie <b>Einkauf</b> mit <i>Bearbeiten</i> frei"),
                    ("➕", "Was du dort einträgst, landet in <b>ihrer</b> Liste und gehört ihr"),
                    ("✍️", "Ein Abzeichen zeigt, <b>wer es eingetragen hat</b>, mit Bild der Person"),
                ], "Eine Freigabe für alle Benutzer zählt dafür nicht."),
                "say": "Gibt dir jemand eine Kategorie persönlich zum Bearbeiten frei, landen deine "
                       "neuen Einträge in seiner Liste. Ein kleines Abzeichen mit Namen oder Bild "
                       "zeigt dann, wer den Eintrag geschrieben hat.",
            },
        ],
    },
    {
        "title": "Echos Personen zuordnen",
        "scenes": [
            {
                "v": ("switches", "Brainstorm › Echos & Apps zuordnen", [
                    ("Echo oder Alexa-App", "Echo Kinderzimmer", True, "Du kannst auch einen Namen eintippen"),
                    ("Person", "Lenja", True, "Leer lassen, um die Zuordnung zu entfernen"),
                ], PATH + " ➔ Echos & Apps Personen zuordnen",
                    "Home Assistant erkennt keine Stimmen, und im Raum hören alle mit."),
                "say": "Auch Echos und Alexa-Apps lassen sich Personen zuordnen. Was am Echo im "
                       "Kinderzimmer gesagt wird, gehört dann Lenja, und Alexa liest dort nur ihre "
                       "Einträge vor. Stimmen erkennt Home Assistant allerdings nicht.",
            },
        ],
    },
    {
        "title": "Was Privatsphäre nicht kann",
        "scenes": [
            {
                "v": ("bullets", "Ehrlich gesagt", [
                    ("🛡️", "<b>Administratoren</b> und alle mit Dateizugriff können weiter alles lesen"),
                    ("📋", "Die <b>To-do-Listen</b> von Home Assistant zeigen nur, was für alle freigegeben ist"),
                    ("📝", "Alte <b>Markdown-Exporte</b> bleiben liegen, neue nur mit deiner Erlaubnis"),
                ], "Privatsphäre in Brainstorm schützt vor Neugier, nicht vor Administratoren."),
                "say": "Wichtig zu wissen: Administratoren und alle mit Zugriff auf die Dateien "
                       "können weiterhin alles lesen. Die To-do-Listen von Home Assistant zeigen "
                       "deshalb nur, was für alle freigegeben ist.",
            },
        ],
    },
    {
        "title": "Backlog für Coding-KIs",
        "scenes": [
            {
                "v": ("grid", "Eine Kategorie als Aufgabenliste für die KI", [
                    ("🗣️", "Sammeln", "Aufgaben per Alexa, Karte oder Assist"),
                    ("🔌", "Lesen", "Die KI liest sie über einen MCP-Server für Home Assistant"),
                    ("🔧", "In Arbeit", "Abzeichen mit dem Namen der KI"),
                    ("✅", "Abhaken", "Mit Ergebnis-Notiz: was umgesetzt wurde"),
                    ("👀", "Nur freigegeben", "Alles andere bleibt für die KI unsichtbar"),
                    ("🛑", "Deine Entscheidung", "Löschen, Freigaben und Einstellungen bleiben bei dir"),
                ], "Beispiel: Claude Code mit ha-mcp."),
                "say": "Brainstorm eignet sich sogar als Aufgabenliste für Coding-KIs wie Claude "
                       "Code. Du sammelst Aufgaben per Stimme, die KI liest sie über einen MCP-Server, "
                       "setzt sie um und hakt sie mit einer Ergebnis-Notiz ab.",
            },
            {
                "v": ("bullets", "Einrichten in fünf Schritten", [
                    ("1", "Unter <b>Einstellungen ➔ Personen</b> einen Benutzer für die KI anlegen, z. B. <i>Claude</i>"),
                    ("2", "Als dieser Benutzer ein <b>langlebiges Zugriffstoken</b> erstellen, damit den MCP-Server verbinden"),
                    ("3", "<b>Privatsphäre einschalten</b>, Backlog-Kategorie für die KI freigeben"),
                    ("4", "Skill <code>brainstorm-backlog</code> aus <code>examples/claude-code</code> kopieren"),
                    ("5", "In <code>CLAUDE.md</code> die Kategorie nennen"),
                ], "Ansehen zum Lesen, Bearbeiten, wenn die KI abhaken darf."),
                "say": "Lege dafür einen eigenen Benutzer für die KI an und erstelle als dieser "
                       "Benutzer ein Token für den MCP-Server. Schalte die Privatsphäre ein und gib "
                       "nur die Backlog-Kategorie frei. Den passenden Skill für Claude Code findest "
                       "du im Ordner examples.",
            },
            {
                "v": ("shot", "crop_done.png", 330, [
                    ("🔧", "<b>In Arbeit</b> zeigt, woran die KI gerade sitzt"),
                    ("📌", "Die <b>Ergebnis-Notiz</b> sagt, was daraus wurde"),
                    ("↩️", "Erledigtes lässt sich <b>wiederherstellen</b>"),
                ], "So siehst du ohne Nachfragen, was die KI erledigt hat."),
                "say": "Auf der Karte siehst du dann, woran die KI gerade arbeitet, und nach dem "
                       "Abhaken in der Ergebnis-Notiz, was daraus geworden ist.",
            },
        ],
    },
    {
        "title": "Viel Spaß",
        "scenes": [
            {
                "v": ("bullets", "Kurz zusammengefasst", [
                    ("🔒", "Privatsphäre einschalten, Hauptbenutzer wählen"),
                    ("👥", "Einträge und Kategorien gezielt freigeben"),
                    ("🗣️", "Echos Personen zuordnen"),
                    ("🤖", "Eigener Benutzer für die KI, nur das Backlog freigeben"),
                ], "Anleitung: README ➔ Privatsphäre & Freigaben"),
                "say": "Das war die Privatsphäre in Brainstorm. Alle Details findest du in der "
                       "Anleitung auf GitHub. Viel Spaß!",
            },
        ],
    },
]
