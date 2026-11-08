"""Storyboard: iPhone shortcut with Siri, Action button or Back Tap (German)."""
from __future__ import annotations

from pron import SPOKEN

TITLE = "Brainstorm Hub: Ideen per iPhone-Kurzbefehl"
OUT_NAME = "brainstorm-iphone"
# README sections this video covers, check them on every release
COVERS = ["3. iPhone: Kurzbefehl mit Siri, Action-Taste oder Rückseite"]

CHAPTERS: list[dict] = [
    {
        "title": "Kurzbefehl",
        "scenes": [
            {
                "v": ("title", "Ideen per iPhone-Kurzbefehl", "Auslösen, sprechen, fertig"),
                "say": "Der schnellste Weg vom iPhone zu Brainstorm: auslösen, sprechen, fertig, "
                       "ganz ohne eine App zu öffnen. In zwei Minuten baust du dir dafür einen "
                       "Kurzbefehl.",
            },
            {
                "v": ("bullets", "Das brauchst du", [
                    ("📱", "Die <b>Home Assistant Companion-App</b>, angemeldet an deinem Home Assistant"),
                    ("⚡", "Die App <b>Kurzbefehle</b>, die auf jedem iPhone vorinstalliert ist"),
                    ("🧠", "Brainstorm Hub, eingerichtet wie im Installationsvideo"),
                ], "Der Kurzbefehl ruft den Dienst brainstorm.add_idea auf."),
                "say": "Du brauchst nur die Home Assistant Companion-App und die App Kurzbefehle, "
                       "die auf jedem iPhone schon drauf ist.",
            },
        ],
    },
    {
        "title": "Kurzbefehl anlegen",
        "scenes": [
            {
                "v": ("phone", "Kurzbefehle ➔ ＋", [
                    ("<small>Name</small><b>Brainstorm</b>", True),
                    ("<small>Aktion 1</small>🎙️ <b>Text diktieren</b><br>Sprache: Deutsch<br>"
                     "Hören stoppen: Nach einer Pause", True),
                    ("<small>Aktion 2</small>…", False),
                ], [
                    ("1", "Neuen Kurzbefehl anlegen und <b>Brainstorm</b> nennen"),
                    ("2", "Aktion <b>Text diktieren</b> hinzufügen"),
                    ("3", "Sprache <b>Deutsch</b>, Hören stoppen <b>Nach einer Pause</b>"),
                ], "Der Name ist gleichzeitig dein Siri-Satz."),
                "say": "Öffne die App Kurzbefehle, tippe auf Plus und nenne den Kurzbefehl "
                       "Brainstorm. Der Name ist gleichzeitig dein Siri-Satz. Füge die Aktion "
                       "Text diktieren hinzu, mit Sprache Deutsch und Hören stoppen nach einer Pause.",
            },
        ],
    },
    {
        "title": "Home Assistant aufrufen",
        "scenes": [
            {
                "v": ("phone", "Kurzbefehl: Brainstorm", [
                    ("<small>Aktion 1</small>🎙️ Text diktieren", False),
                    ("<small>Aktion 2 · Home Assistant</small><b>Aktion ausführen</b><br>"
                     "Idee hinzufügen<br><small>brainstorm.add_idea</small>", True),
                ], [
                    ("4", "Von <b>Home Assistant</b> die Aktion <b>Aktion ausführen</b> hinzufügen"),
                    ("5", "Als Aktion <b>Idee hinzufügen</b> wählen"),
                ], "Findest du die Aktion nicht, öffne einmal die Companion-App."),
                "say": "Als Zweites suchst du bei Home Assistant die Aktion: Aktion ausführen. "
                       "Wähle darin Idee hinzufügen von Brainstorm.",
            },
            {
                "v": ("yaml", "Das Datenfeld",
                      '{"text": "", "source": "siri", "device": "iPhone"}\n\n'
                      '          ^\n          hier die Variable „Diktierter Text“ einsetzen',
                      "Den Gerätenamen hinter device kannst du frei wählen."),
                "say": "Ins Datenfeld kommt dieser kurze Text im Format JSON. Zwischen die "
                       "Anführungszeichen hinter text setzt du die Variable Diktierter Text. Den "
                       "Gerätenamen am Ende kannst du frei wählen.",
            },
            {
                "v": ("bullets", "Wichtig: gerade Anführungszeichen", [
                    ("⚠️", "Meldung <b>„Die Daten konnten nicht gelesen werden“</b>? Dann ist das JSON ungültig"),
                    ("❝", "Das iPhone setzt beim Tippen gern <b>typografische Anführungszeichen</b>"),
                    ("📋", "Text am besten <b>kopieren und einfügen</b>"),
                    ("⚙️", "Oder kurz ausschalten: Einstellungen ➔ Allgemein ➔ Tastatur ➔ <b>Intelligente Interpunktion</b>"),
                ], "Die Vorlage zum Kopieren steht in der README."),
                "say": "Ein häufiger Stolperstein: Das iPhone ersetzt beim Tippen die geraden "
                       "Anführungszeichen. Dann meldet der Kurzbefehl, dass die Daten nicht "
                       "gelesen werden konnten. Kopiere den Text deshalb am besten aus der Anleitung.",
            },
        ],
    },
    {
        "title": "Auslöser wählen",
        "scenes": [
            {
                "v": ("grid", "Drei Wege zum Kurzbefehl", [
                    ("🔘", "Action-Taste", "Einstellungen ➔ Action-Taste ➔ Kurzbefehl ➔ Brainstorm"),
                    ("👆", "Rückseite", "Bedienungshilfen ➔ Tippen ➔ Auf Rückseite tippen ➔ Doppeltippen"),
                    ("🗣️", "Siri", "„Hey Siri, Brainstorm“"),
                ], "Die Action-Taste gibt es ab dem iPhone 15 Pro."),
                "say": "Jetzt fehlt nur noch der Auslöser. Auf neueren iPhones legst du den "
                       "Kurzbefehl auf die Action-Taste. Oder du tippst zweimal auf die Rückseite "
                       "des iPhones. Und natürlich geht immer: Hey Siri, Brainstorm.",
            },
        ],
    },
    {
        "title": "Ausprobieren",
        "scenes": [
            {
                "v": ("transform", "Rauchmelder im Bad tauschen", "Rauchmelder im Bad tauschen",
                      ["🍎 Siri (iPhone)", "📂 Haus & Garten"],
                      "Die Notiz zeigt das Apfel-Logo und den Gerätenamen."),
                "say": "Probieren wir es aus: Action-Taste drücken und sagen, Rauchmelder im Bad "
                       "tauschen. Sekunden später steht die Notiz in Brainstorm, mit Apfel-Logo und "
                       "dem Namen deines iPhones.",
            },
            {
                "v": ("shot", "crop_list.png", 450, [
                    ("🧠", "Brainstorm sortiert wie immer: <b>Kategorie, Priorität, Termin</b>"),
                    ("🗣️", "Ganze Sätze gehen auch: <i>„morgen dringend Arzt anrufen“</i>"),
                    ("🏷️", "Herkunft <b>Siri (iPhone)</b> an der Notiz"),
                ], "Auch Termine im Satz werden erkannt."),
                "say": "Brainstorm sortiert die Notiz wie gewohnt ein. Auch ganze Sätze mit "
                       "Termin oder Priorität funktionieren, etwa: morgen dringend Arzt anrufen.",
            },
        ],
    },
    {
        "title": "Viel Spaß",
        "scenes": [
            {
                "v": ("bullets", "Kurz zusammengefasst", [
                    ("1", "Kurzbefehl <b>Brainstorm</b> mit <b>Text diktieren</b>"),
                    ("2", "Home Assistant: <b>Idee hinzufügen</b> mit dem JSON-Datenfeld"),
                    ("3", "Auf Action-Taste, Rückseite oder Siri legen"),
                ], "Anleitung: README ➔ Sprachsteuerung ➔ iPhone"),
                "say": "Das war's. Kurzbefehl anlegen, Idee hinzufügen, Auslöser wählen. Die "
                       "Anleitung zum Nachlesen findest du auf GitHub. Viel Spaß!",
            },
        ],
    },
]
