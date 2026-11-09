"""Storyboard of the Brainstorm Alexa skill video (German)."""
from __future__ import annotations

from pron import SPOKEN  # noqa: F401  (used by build.py)

# README sections this video covers, check them on every release
COVERS = ["Variante C: Eigener Alexa-Skill", "Listen auf dem Echo Show", "Echte Alexa-Erinnerungen"]
TITLE = "Brainstorm: Eigenen Alexa-Skill einrichten"
OUT_NAME = "brainstorm-alexa-skill"

# Every chapter is one setting. Visual kinds: title, bullets, wizard, console, ha,
# speech, code, alexa_app.
CHAPTERS: list[dict] = [
    {
        "title": "Einleitung",
        "scenes": [
            {
                "v": ("title", "Dein eigener Alexa-Skill für Brainstorm",
                      "Schritt für Schritt durch alle wichtigen Einstellungen"),
                "say": "Willkommen! In diesem Video richtest du deinen eigenen Alexa-Skill "
                       "für Brainstorm ein. Wir gehen jede wichtige Einstellung in einem "
                       "eigenen Kapitel durch.",
            },
            {
                "v": ("speech", [
                    ("du", "Alexa, sage Brainstorm notiere Kellerlicht dimmen."),
                    ("alexa", "Gespeichert unter Smarthome."),
                ], "Mit Skill: ein Satz, eine Antwort"),
                "say": "Der Vorteil: Ohne Skill meldet Alexa oft zuerst einen Fehler. Mit "
                       "deinem Skill gibt es genau eine Antwort, und die Idee landet sofort "
                       "in der richtigen Kategorie.",
            },
        ],
    },
    {
        "title": "Voraussetzungen",
        "scenes": [
            {
                "v": ("bullets", "Das brauchst du", [
                    ("✅", "Brainstorm Hub ist in Home Assistant installiert"),
                    ("🔑", "Kostenloses Amazon-Entwicklerkonto – <b>dasselbe Konto wie deine Echos</b>"),
                    ("🌐", "Home Assistant per <b>HTTPS aus dem Internet</b> erreichbar, z. B. über Home Assistant Cloud"),
                    ("📡", "Optional: Integration <b>Alexa Media</b> für Geräteerkennung und freie Sätze"),
                ], "Das gleiche Amazon-Konto ist der häufigste Stolperstein."),
                "say": "Du brauchst ein kostenloses Amazon-Entwicklerkonto. Wichtig: Es muss "
                       "dasselbe Amazon-Konto sein, mit dem deine Echos angemeldet sind. "
                       "Außerdem muss Home Assistant per HTTPS aus dem Internet erreichbar "
                       "sein, zum Beispiel über Home Assistant Cloud.",
            },
            {
                "v": ("bullets", "Externe Adresse prüfen", [
                    ("⚙️", "Einstellungen ➔ System ➔ Netzwerk"),
                    ("🔗", "Feld <b>Internet</b> bzw. Home Assistant Cloud aktiv"),
                    ("🧩", "Aus dieser Adresse baut Brainstorm die geheime Webhook-Adresse im Skill-Code"),
                ], "Ohne externe Adresse kann der Skill Home Assistant nicht erreichen."),
                "say": "Prüfe unter Einstellungen, System, Netzwerk, dass eine Internet-Adresse "
                       "eingetragen oder Home Assistant Cloud aktiv ist. Aus dieser Adresse "
                       "baut Brainstorm später die geheime Adresse im Skill-Code.",
            },
        ],
    },
    {
        "title": "Home Assistant: Spracheingabe",
        "scenes": [
            {
                "v": ("ha", "Brainstorm › Alexa", [
                    ("Spracheingabe", "Skill", True,
                     "Nativ (ohne Skill) · <u>Skill</u> · Beide"),
                ], "Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub ➔ Konfigurieren ➔ "
                   "Alexa-Spracheingabe & Skill", "Weiter"),
                "say": "Öffne in Home Assistant Einstellungen, Geräte und Dienste, Brainstorm "
                       "Hub, Konfigurieren, und dann Alexa-Spracheingabe und Skill. Wähle bei "
                       "Spracheingabe Skill oder Beide, und klicke auf Weiter.",
            },
            {
                "v": ("ha", "Brainstorm › Alexa › Skill", [
                    ("Skill-Code (lambda_function.py)", "WEBHOOK_URL = \"https://•••••/api/webhook/brainstorm_•••\"", True, ""),
                    ("Sprachmodell (JSON-Editor)", "{ \"interactionModel\": { \"languageModel\": …", True, ""),
                    ("Neue geheime Adresse erzeugen …", "aus", False, ""),
                ], "Dieses Fenster offen lassen – du brauchst beide Felder gleich", "Absenden"),
                "say": "Jetzt siehst du die beiden Felder Skill-Code und Sprachmodell. Lass "
                       "dieses Fenster offen, du kopierst sie gleich in die Entwicklerkonsole. "
                       "Beide gibt es auf Deutsch und Englisch, passend zur Sprache von "
                       "Home Assistant. Und noch nicht Absenden klicken.",
            },
        ],
    },
    {
        "title": "Skill-Name",
        "scenes": [
            {
                "v": ("wizard", 1, "Name, Locale", [
                    ("Skill name", "Brainstorm", True),
                    ("Primary locale", "German (DE)", False),
                ], "Der Name ist nur die Anzeige in der Konsole und der Alexa-App."),
                "say": "Klicke in der Alexa-Entwicklerkonsole auf Create Skill. Als Namen "
                       "trägst du Brainstorm ein. Der Name ist nur die Anzeige in der Konsole "
                       "und in der Alexa-App. Wie du den Skill aufrufst, legt später das "
                       "Sprachmodell fest.",
            },
        ],
    },
    {
        "title": "Sprache (Primary locale)",
        "scenes": [
            {
                "v": ("wizard", 1, "Name, Locale", [
                    ("Skill name", "Brainstorm", False),
                    ("Primary locale", "German (DE)", True),
                ], "Gleiche Sprache wie dein Echo – sonst findet Alexa den Skill nicht."),
                "say": "Bei der Sprache wählst du German, D E. Sie muss zur Sprache deines "
                       "Echos passen, sonst findet Alexa den Skill nicht. Sprichst du mit "
                       "deinem Echo Englisch, nimmst du English und das englische "
                       "Sprachmodell aus Home Assistant.",
            },
        ],
    },
    {
        "title": "Erfahrung & Modell: Custom",
        "scenes": [
            {
                "v": ("wizard", 2, "Experience, Model, Hosting service", [
                    ("Type of experience", "Other", False),
                    ("Model", "Custom", True),
                    ("Hosting services", "Alexa-hosted (Python)", False),
                ], "Nur das Modell Custom erlaubt ein eigenes Sprachmodell."),
                "say": "Im nächsten Schritt ist die Art der Erfahrung egal, Other passt. "
                       "Entscheidend ist das Modell: Wähle Custom. Nur damit kannst du das "
                       "eigene Sprachmodell von Brainstorm einfügen.",
            },
        ],
    },
    {
        "title": "Hosting: Alexa-hosted (Python)",
        "scenes": [
            {
                "v": ("wizard", 2, "Experience, Model, Hosting service", [
                    ("Model", "Custom", False),
                    ("Hosting services", "Alexa-hosted (Python)", True),
                    ("Hosting region", "EU (Ireland)", True),
                ], "Python, nicht Node.js – der Skill-Code von Brainstorm ist Python."),
                "say": "Als Hosting wählst du Alexa-hosted, Python. Nicht Node J S, denn der "
                       "Skill-Code von Brainstorm ist Python. Amazon betreibt den Code dann "
                       "kostenlos für dich. Als Region empfiehlt sich in Europa E U Irland. "
                       "Den Endpunkt trägt Amazon dabei selbst ein, den musst du nicht ändern.",
            },
        ],
    },
    {
        "title": "Vorlage: Start from Scratch",
        "scenes": [
            {
                "v": ("wizard", 3, "Templates", [
                    ("Template", "Start from Scratch", True),
                    ("Review", "Create Skill", False),
                ], "Andere Vorlagen bringen Beispiel-Intents mit, die stören würden."),
                "say": "Als Vorlage nimmst du Start from Scratch. Andere Vorlagen bringen "
                       "Beispiel-Intents mit, die das Brainstorm-Sprachmodell ohnehin "
                       "ersetzt. Prüfe die Übersicht und klicke auf Create Skill. Das Anlegen "
                       "dauert etwa eine Minute.",
            },
        ],
    },
    {
        "title": "Interfaces: Alexa Presentation Language",
        "scenes": [
            {
                "v": ("console", "Build", "Interfaces", "apl",
                      "Nur nötig für Listen auf dem Echo Show."),
                "say": "Hast du einen Echo Show? Dann öffne im Tab Build den Punkt Interfaces "
                       "und schalte Alexa Presentation Language ein. Wähle die Hub-Profile "
                       "für den Echo Show und klicke oben auf Save. Danach zeigt der Echo "
                       "Show deine Listen. Antippen hakt eine Idee ab oder klappt ihre "
                       "Unterpunkte auf.",
            },
        ],
    },
    {
        "title": "Permissions: Reminders",
        "scenes": [
            {
                "v": ("console", "Build", "Permissions", "perm",
                      "Nur für echte Alexa-Erinnerungen nötig."),
                "say": "Möchtest du echte Alexa-Erinnerungen, öffne unter Build den Punkt "
                       "Permissions und schalte Reminders ein. Die Zustimmung gibst du "
                       "später einmal in der Alexa-App. Ohne diese Berechtigung erinnert dich "
                       "Home Assistant trotzdem, nur eben nicht über Amazon.",
            },
        ],
    },
    {
        "title": "Sprachmodell: JSON Editor",
        "scenes": [
            {
                "v": ("console", "Build", "JSON Editor", "json",
                      "Erst Save, dann Build Skill – und auf die Erfolgsmeldung warten."),
                "say": "Jetzt das Herzstück: Öffne Interaction Model und dann JSON Editor. "
                       "Markiere den kompletten Inhalt, lösche ihn und füge das Feld "
                       "Sprachmodell aus Home Assistant ein. Klicke auf Save und danach auf "
                       "Build Skill. Warte, bis die Erfolgsmeldung erscheint.",
            },
            {
                "v": ("bullets", "Was das Sprachmodell enthält", [
                    ("🗣️", "<b>notiere …</b> – Idee speichern"),
                    ("⏰", "<b>erinnere mich an …</b> · <b>erledigt</b> · <b>später</b>"),
                    ("📢", "<b>Ansage</b> · <b>alles vorlesen</b> · <b>zeige Alltag</b>"),
                    ("🧩", "Fallback: freie Sätze holt Home Assistant aus dem Alexa-Verlauf"),
                ], "Nach jedem Brainstorm-Update mit neuem Sprachmodell: erneut einfügen und Build."),
                "say": "Das Sprachmodell kennt alle Sätze: notiere, erinnere mich, erledigt, "
                       "später, Ansage und zeige. Kündigt ein Brainstorm-Update ein neues "
                       "Sprachmodell an, fügst du es erneut ein und klickst wieder auf Build.",
            },
        ],
    },
    {
        "title": "Aufrufname (Invocation Name)",
        "scenes": [
            {
                "v": ("console", "Build", "Invocations", "inv",
                      "Kommt aus dem Sprachmodell – nicht ändern."),
                "say": "Kontrolliere unter Invocations den Skill Invocation Name. Dort steht "
                       "jetzt brainstorm, klein geschrieben. Das hat das Sprachmodell "
                       "eingetragen. Ändere ihn nicht, sonst passen die Sätze aus der "
                       "Anleitung nicht mehr.",
            },
        ],
    },
    {
        "title": "Skill-Code: lambda_function.py",
        "scenes": [
            {
                "v": ("console", "Code", "lambda_function.py", "code",
                      "Gesamten Inhalt ersetzen, dann Deploy."),
                "say": "Wechsle in den Tab Code und öffne die Datei lambda function punkt "
                       "p y. Ersetze den gesamten Inhalt durch das Feld Skill-Code aus Home "
                       "Assistant und klicke auf Deploy. Die anderen Dateien bleiben, wie "
                       "sie sind.",
            },
            {
                "v": ("bullets", "Der Skill-Code ist geheim", [
                    ("🔒", "Er enthält deine <b>geheime Webhook-Adresse</b>"),
                    ("🚫", "Nicht teilen, nicht in Screenshots zeigen"),
                    ("♻️", "Bekannt geworden? <b>Neue geheime Adresse erzeugen</b> und Code neu kopieren"),
                ], "Nach einem Brainstorm-Update mit neuem Skill-Code: erneut einfügen und Deploy."),
                "say": "Halte den Skill-Code geheim, er enthält deine geheime Adresse. Wurde "
                       "sie bekannt, erzeugst du in Home Assistant eine neue und kopierst den "
                       "Skill-Code erneut.",
            },
        ],
    },
    {
        "title": "Test: Development",
        "scenes": [
            {
                "v": ("console", "Test", "Test", "test",
                      "Steht hier Off, kennt dein Echo den Skill nicht."),
                "say": "Öffne den Tab Test und stelle oben Development ein. Damit ist der "
                       "Skill auf allen Echos deines Amazon-Kontos aktiv, ganz ohne "
                       "Veröffentlichung. Steht dort Off, kennt dein Echo den Skill nicht.",
            },
            {
                "v": ("console", "Test", "Test", "testrun",
                      "Erst hier testen, dann am Echo."),
                "say": "Tippe zum Test im Eingabefeld: sage brainstorm notiere testidee. "
                       "Antwortet Alexa hier richtig, funktioniert auch der Echo.",
            },
        ],
    },
    {
        "title": "Kopplung mit Home Assistant",
        "scenes": [
            {
                "v": ("speech", [
                    ("ha", "Absenden in Home Assistant"),
                    ("du", "Alexa, sage Brainstorm notiere Testidee."),
                    ("alexa", "Gespeichert unter Inbox."),
                ], "Die erste Anfrage koppelt deinen Skill"),
                "say": "Klicke in Home Assistant auf Absenden und sprich am Echo: Alexa, sage "
                       "Brainstorm notiere Testidee. Die erste Anfrage koppelt deinen Skill. "
                       "Danach weist Home Assistant alle anderen Skills ab.",
            },
            {
                "v": ("ha", "Brainstorm › Alexa › Skill", [
                    ("Skill gekoppelt", "Ja", True, ""),
                    ("Letzte Skill-Anfrage", "heute, 20:15", True, ""),
                    ("Name für dieses unbekannte Gerät", "Alexa App iPhone", False,
                     "Für Anfragen aus der Alexa-App"),
                ], "Unter Konfigurieren siehst du Kopplung und letzte Anfrage", "Absenden"),
                "say": "Unter Konfigurieren siehst du jetzt die Kopplung und die letzte "
                       "Anfrage. Kam eine Anfrage aus der Alexa-App, kannst du dem Gerät "
                       "hier einen Namen geben.",
            },
        ],
    },
    {
        "title": "Alexa-App: Skill & Berechtigung",
        "scenes": [
            {
                "v": ("alexa_app",),
                "say": "In der Alexa-App findest du den Skill unter Mehr, Skills und Spiele, "
                       "Meine Skills, im Bereich für Entwickler-Skills. Hast du Reminders "
                       "eingeschaltet, erteile dort in den Einstellungen des Skills einmal "
                       "die Berechtigung für Erinnerungen.",
            },
        ],
    },
    {
        "title": "Alte Routinen aufräumen",
        "scenes": [
            {
                "v": ("bullets", "Nur im Modus Skill", [
                    ("🧹", "Alexa-Routinen für <b>„öffne Brainstorm“</b> aus Variante A löschen"),
                    ("⚠️", "Sonst startet statt des Skills der alte Dialog"),
                    ("🔀", "Eigene Automationen: <code>voice_mode</code> von "
                           "<code>sensor.brainstorm_ideen_ubersicht</code> prüfen"),
                ], "Im Modus Beide dürfen Routinen und Skill nebeneinander bestehen."),
                "say": "Nutzt du den Modus Skill, lösche die alten Alexa-Routinen für öffne "
                       "Brainstorm. Sonst startet statt des Skills der alte Dialog. Eigene "
                       "Automationen prüfen das Attribut voice mode und schalten sich so ab.",
            },
        ],
    },
    {
        "title": "Fehlerbehebung",
        "scenes": [
            {
                "v": ("bullets", "„Ich weiß nicht, wie ich dabei helfen soll“", [
                    ("🔨", "<b>Build</b> im JSON Editor fehlt"),
                    ("🧪", "Tab Test steht nicht auf <b>Development</b>"),
                    ("👤", "Konsole und Echo nutzen <b>verschiedene Amazon-Konten</b>"),
                    ("🌐", "„nicht gespeichert“: Modus Skill/Beide und Erreichbarkeit von Home Assistant prüfen"),
                ], "Freie Sätze ohne Befehlswort klappen nur am Echo, nicht in der Alexa-App."),
                "say": "Sagt Alexa: Ich weiß nicht, wie ich dabei helfen soll, fehlt meist der "
                       "Build, der Test steht nicht auf Development, oder Konsole und Echo "
                       "nutzen verschiedene Konten. Sagt Alexa, die Idee wurde nicht "
                       "gespeichert, prüfe den Modus und die Erreichbarkeit von Home Assistant.",
            },
        ],
    },
    {
        "title": "Zusammenfassung",
        "scenes": [
            {
                "v": ("bullets", "Alle Einstellungen auf einen Blick", [
                    ("1", "Name <b>Brainstorm</b> · Sprache <b>German (DE)</b> · Modell <b>Custom</b>"),
                    ("2", "Hosting <b>Alexa-hosted (Python)</b> · Vorlage <b>Start from Scratch</b>"),
                    ("3", "Optional: <b>Interfaces ➔ APL</b> · <b>Permissions ➔ Reminders</b>"),
                    ("4", "<b>JSON Editor</b>: Sprachmodell, Save, Build"),
                    ("5", "<b>Code</b>: Skill-Code, Deploy · <b>Test</b>: Development"),
                    ("6", "Home Assistant: <b>Absenden</b>, erster Satz koppelt"),
                ], "Viel Spaß beim Sammeln deiner Ideen!"),
                "say": "Zusammengefasst: Name Brainstorm, Sprache Deutsch, Modell Custom, "
                       "Hosting Alexa-hosted Python, Vorlage Start from Scratch. Optional "
                       "die Presentation Language und Reminders. Dann Sprachmodell, Build, "
                       "Skill-Code, Deploy, Test auf Development, und in Home Assistant "
                       "Absenden. Viel Spaß beim Sammeln deiner Ideen!",
            },
        ],
    },
]

# Pronunciation help for the German voice, applied to the spoken text only
