"""Storyboard: Brainstorm reminders and notifications (German)."""
from __future__ import annotations

from pron import SPOKEN

TITLE = "Brainstorm Hub: Erinnerungen & Benachrichtigungen"
OUT_NAME = "brainstorm-erinnerungen"
# README sections this video covers, check them on every release
COVERS = ["Erinnerungen & Benachrichtigungen", "Brainstorm › Erinnerungen › …"]

PATH = "Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub ➔ Konfigurieren"

CHAPTERS: list[dict] = [
    {
        "title": "Erinnerungen",
        "scenes": [
            {
                "v": ("title", "Erinnerungen & Benachrichtigungen", "Brainstorm denkt für dich mit"),
                "say": "Brainstorm erinnert dich von selbst an fällige Einträge. Per Alexa-Ansage, "
                       "aufs Handy, an einem Ort oder als tägliches Briefing. In diesem Video "
                       "zeige ich dir, wie du Termine setzt und alles einstellst.",
            },
        ],
    },
    {
        "title": "Termin per Sprache",
        "scenes": [
            {
                "v": ("transform", "erinnere mich morgen um 8 an die Mülltonnen", "Mülltonnen",
                      ["⏰ Morgen 8:00", "📂 Alltag"],
                      "Mit dem eigenen Skill: „Alexa, sage Brainstorm erinnere mich …“"),
                "say": "Am einfachsten geht es per Sprache. Sag: Alexa, sage Brainstorm, erinnere "
                       "mich morgen um 8 an die Mülltonnen. Brainstorm speichert die Notiz mit "
                       "Termin morgen um acht Uhr.",
            },
            {
                "v": ("grid", "Das versteht Brainstorm", [
                    ("🌙", "Tageszeiten", "heute Abend, morgen früh, übermorgen"),
                    ("📅", "Wochentage", "am Freitag, nächste Woche"),
                    ("🗓️", "Datum", "am 25.11., am zweiten Dezember um zwölf"),
                    ("⏳", "Abstände", "in zwei Stunden, in zehn Minuten"),
                    ("🕣", "Uhrzeiten", "um 8, um halb neun, um Viertel nach drei"),
                    ("➡️", "Nächstes Jahr", "Liegt ein Datum schon hinter dir, gilt das nächste Jahr"),
                ], "Ein reines Datum ohne Uhrzeit bedeutet 9:00 Uhr."),
                "say": "Verstanden werden Tageszeiten wie heute Abend oder morgen früh, Wochentage, "
                       "ein Datum, Abstände wie in zwei Stunden und Uhrzeiten wie um halb neun. "
                       "Ohne Uhrzeit erinnert Brainstorm um neun Uhr morgens.",
            },
        ],
    },
    {
        "title": "Termin auf der Karte",
        "scenes": [
            {
                "v": ("bullets", "Ohne Stimme geht es auch", [
                    ("👆", "Eintrag <b>lange drücken</b> ➔ <i>Erinnern: heute Abend, morgen früh, nächste Woche</i> oder <i>Zeitpunkt wählen</i>"),
                    ("✏️", "Im <b>Bearbeiten-Dialog</b> Datum und Uhrzeit setzen"),
                    ("🔊", "<b>Erinnern auf:</b> wählt die Echos, die genau diese Erinnerung sprechen"),
                    ("📋", "Oder das <b>Fälligkeitsdatum</b> in der To-do-Liste von Home Assistant"),
                ], "In Automationen: brainstorm.add_idea und brainstorm.update_idea mit dem Feld due."),
                "say": "Auf der Karte drückst du einen Eintrag lange und wählst einen Zeitpunkt. Im "
                       "Bearbeiten-Dialog setzt du Datum und Uhrzeit, und unter Erinnern auf "
                       "wählst du die Echos, die genau diese Erinnerung sprechen.",
            },
        ],
    },
    {
        "title": "Einschalten",
        "scenes": [
            {
                "v": ("menu", "Brainstorm › Erinnerungen", [
                    ("Ein/Aus & Kanäle", True), ("Ruhezeit, Briefing & Wochenrückblick", False),
                    ("Regeln pro Liste", False), ("Orte & Heimkommen", False), ("Personen", False),
                    ("Kalender & Alexa-Erinnerungen", False), ("Sperrzeiten pro Echo", False),
                    ("🧪 Kanäle jetzt testen", False),
                ], PATH + " ➔ Erinnerungen & Benachrichtigungen",
                    "Jede Funktion hat ihren eigenen Schalter, alles ist optional."),
                "say": "Eingestellt wird alles in der Integration unter Konfigurieren, "
                       "Erinnerungen und Benachrichtigungen. Jede Funktion hat einen eigenen "
                       "Schalter. Wir beginnen mit Ein und Aus und den Kanälen.",
            },
            {
                "v": ("switches", "Brainstorm › Erinnerungen › Ein/Aus & Kanäle", [
                    ("Erinnerungen nutzen", True, True, "Hauptschalter für alles in diesem Menü"),
                    ("Alexa-Ansage", "Echo, von dem der Eintrag kam", True,
                     "Oder: zuletzt genutzter Echo, feste Echos, Aus"),
                    ("Benachrichtigungen senden", True, True, "z. B. notify.mobile_app_iphone"),
                    ("Wartezeit vor Benachrichtigungen", "5 Minuten", False,
                     "Erst spricht der Echo, das Handy folgt nur, wenn du nicht reagierst"),
                    ("Wichtige offene Einträge erneut senden", False, False,
                     "Hohe und dringende Einträge nach einer Wartezeit an weitere Dienste"),
                ], PATH + " ➔ Erinnerungen", "Die Alexa-Ansage braucht Alexa Media Player."),
                "say": "Schalte Erinnerungen nutzen ein und wähle, welcher Echo ansagt, zum "
                       "Beispiel der, an dem du den Eintrag gesprochen hast. Dazu kommen "
                       "Benachrichtigungsdienste wie dein Handy. Mit einer Wartezeit kommt das "
                       "Handy nur, wenn du am Echo nicht reagierst.",
            },
        ],
    },
    {
        "title": "Aufs Handy",
        "scenes": [
            {
                "v": ("phone", "Sperrbildschirm", [
                    ('<small>🧠 BRAINSTORM · jetzt</small><b>Erinnerung: Mülltonnen</b><br>Alltag · 8:00 Uhr'
                     '<div class="act"><span>Erledigt</span><span>1 Stunde später</span><span>Morgen</span></div>', True),
                    ('<small>🧠 BRAINSTORM · gestern</small>Briefing: 3 Termine heute, Reifen wechseln ist dringend', False),
                ], [
                    ("✅", "<b>Erledigt</b> hakt den Eintrag direkt ab"),
                    ("⏰", "<b>1 Stunde später</b> oder <b>Morgen</b> verschiebt ihn"),
                    ("📣", "Wichtiges geht auf Wunsch erneut raus, z. B. an Pushover"),
                    ("🧪", "<b>Kanäle jetzt testen</b> schickt sofort eine Probe"),
                ], "Die Knöpfe gibt es in der Home Assistant Companion-App."),
                "say": "Auf dem Handy kommt die Erinnerung mit drei Knöpfen: Erledigt, eine Stunde "
                       "später und Morgen. Wichtige Einträge schickt Brainstorm auf Wunsch erneut, "
                       "zum Beispiel an Pushover. Mit Kanäle jetzt testen prüfst du alles sofort.",
            },
        ],
    },
    {
        "title": "Ruhezeit, Briefing & Rückblick",
        "scenes": [
            {
                "v": ("switches", "Brainstorm › Erinnerungen › Ruhezeit, Briefing & Rückblick", [
                    ("Ruhezeit nutzen", True, False, "Von 22:00 bis 7:00 warten Erinnerungen"),
                    ("Tägliches Briefing", True, True, "Um 7:30 eine Übersicht des Tages"),
                    ("Nur wenn hier jemand erkannt wird", "binary_sensor.kueche_bewegung", True,
                     "Wartet bis zu 6 Stunden, bis jemand da ist"),
                    ("Wochenrückblick", True, False, "Sonntags: Einträge, die länger als 14 Tage offen sind"),
                ], PATH + " ➔ Erinnerungen",
                    "Dringendes erreicht in der Ruhezeit das Handy, aber kein Echo spricht."),
                "say": "In der Ruhezeit warten Erinnerungen bis zum Morgen. Nur Dringendes erreicht "
                       "dann das Handy, kein Echo spricht. Das tägliche Briefing gibt dir eine "
                       "Übersicht, auf Wunsch erst, wenn ein Bewegungsmelder jemanden sieht. Der "
                       "Wochenrückblick nennt, was schon lange offen ist.",
            },
            {
                "v": ("bullets", "Sperrzeiten pro Echo", [
                    ("🛏️", "Bis zu drei <b>Sperrzeiten</b>, z. B. für den Echo im Kinderzimmer"),
                    ("🔕", "Auf Wunsch schaltet Brainstorm dort auch <b>Nicht stören</b> ein und aus"),
                    ("🌅", "Endet die Zeit früher als sie beginnt, gilt sie bis zum nächsten Morgen"),
                ], "„Nicht stören“ braucht Alexa Media Player."),
                "say": "Einzelne Echos kannst du zusätzlich sperren, etwa im Kinderzimmer am "
                       "Nachmittag. Auf Wunsch schaltet Brainstorm dort auch Nicht stören ein, "
                       "dann ist sogar Alexa selbst still.",
            },
        ],
    },
    {
        "title": "Regeln pro Liste",
        "scenes": [
            {
                "v": ("switches", "Brainstorm › Erinnerungen › Regeln › Einkauf", [
                    ("Erinnerungen dieser Liste gehen an", "Nur Benachrichtigungen (privat)", True,
                     "Normale Kanäle · Nur Alexa · Nur Benachrichtigungen · Nichts, nur Ereignis"),
                    ("Eigene Benachrichtigungsdienste", "notify.mobile_app_pixel", False,
                     "Leer nutzt die normalen Dienste"),
                    ("Offene Einträge an bestimmten Tagen senden", True, False, "Samstag um 9:00"),
                    ("Offene Einträge an einem Ort senden", True, True, "Zone: Edeka"),
                ], PATH + " ➔ Erinnerungen", "Ideal für Einkaufslisten: Sie kommen, wenn du im Laden bist."),
                "say": "Jede Liste kann eigene Regeln haben. Private Listen gehen nur aufs Handy, "
                       "statt laut am Echo. Die Einkaufsliste kommt jeden Samstag, oder sobald du "
                       "beim Supermarkt ankommst.",
            },
        ],
    },
    {
        "title": "Orte & Heimkommen",
        "scenes": [
            {
                "v": ("speech", [
                    ("du", "Alexa, sage Brainstorm erinnere mich wenn ich heimkomme an den Müll."),
                    ("du", "Alexa, sage Brainstorm erinnere mich wenn ich bei Edeka bin an die Milch."),
                    ("ha", "📍 Erinnerung kommt, sobald du die Zone betrittst"),
                ], "Nutzt deine Zonen in Home Assistant"),
                "say": "Unter Orte und Heimkommen erlaubst du Erinnerungen an Orten. Dann sagst du: "
                       "erinnere mich, wenn ich heimkomme, an den Müll. Oder: wenn ich bei Edeka "
                       "bin, an die Milch. Dafür nutzt Brainstorm deine Zonen.",
            },
        ],
    },
    {
        "title": "Für andere Personen",
        "scenes": [
            {
                "v": ("speech", [
                    ("du", "Alexa, sage Brainstorm erinnere Frida morgen um 8 an den Zahnarzt."),
                    ("alexa", "Ich erinnere Frida morgen um 8 Uhr an den Zahnarzt."),
                ], "Jede Person mit eigenen Echos und Diensten"),
                "say": "Erinnerungen können auch für andere sein: erinnere Frida morgen um 8 an "
                       "den Zahnarzt. Unter Personen legst du fest, welcher Echo und welches Handy "
                       "für jede Person zuständig ist.",
            },
        ],
    },
    {
        "title": "Antworten per Sprache",
        "scenes": [
            {
                "v": ("speech", [
                    ("alexa", "Erinnerung: Mülltonnen."),
                    ("du", "Alexa, sage Brainstorm erledigt."),
                    ("du", "Alexa, sage Brainstorm später."),
                ], "Mit dem eigenen Alexa-Skill"),
                "say": "Hat dich Alexa erinnert, sagst du einfach: Alexa, sage Brainstorm erledigt. "
                       "Oder: später, dann kommt die Erinnerung in einer Stunde noch einmal.",
            },
        ],
    },
    {
        "title": "Kalender & echte Alexa-Erinnerungen",
        "scenes": [
            {
                "v": ("switches", "Brainstorm › Erinnerungen › Kalender & Alexa", [
                    ("Erinnerungen in einen Kalender eintragen", True, True,
                     "Nur in eine Richtung und einmal pro Erinnerung"),
                    ("Kalender", "calendar.familie", False, "z. B. ein Google- oder CalDAV-Kalender"),
                    ("Zusätzlich echte Alexa-Erinnerungen anlegen", True, True,
                     "Alexa klingelt selbst, Home Assistant spricht nicht zusätzlich"),
                ], PATH + " ➔ Erinnerungen",
                    "Echte Alexa-Erinnerungen brauchen Build ➔ Permissions ➔ Reminders in der Alexa-Konsole."),
                "say": "Erinnerungen landen auf Wunsch auch in einem Kalender. Mit dem Skill legt "
                       "Brainstorm zusätzlich echte Alexa-Erinnerungen an. Dafür schaltest du in "
                       "der Alexa-Konsole unter Permissions die Reminders ein und stimmst einmal "
                       "in der Alexa-App zu.",
            },
        ],
    },
    {
        "title": "Eigene Automationen",
        "scenes": [
            {
                "v": ("yaml", "Jede Erinnerung ist ein Ereignis",
                      "trigger:\n  - trigger: event\n    event_type: brainstorm_reminder_due\naction:\n"
                      "  - action: light.turn_on\n    target:\n      entity_id: light.flur\n"
                      "    data:\n      color_name: orange",
                      "Das Ereignis kommt auch ganz ohne eingerichtete Kanäle."),
                "say": "Jede Erinnerung löst außerdem das Ereignis brainstorm reminder due aus. "
                       "Damit baust du eigene Automationen, zum Beispiel lässt du das Licht im Flur "
                       "orange leuchten.",
            },
        ],
    },
    {
        "title": "Viel Spaß",
        "scenes": [
            {
                "v": ("bullets", "Kurz zusammengefasst", [
                    ("🗣️", "Termin sagen oder auf der Karte setzen"),
                    ("🔊", "Echo, Handy, Ort, Kalender oder Automation"),
                    ("🌙", "Ruhezeit, Sperrzeiten und Regeln pro Liste"),
                ], "Alle Schalter erklärt: README ➔ Erinnerungen & Benachrichtigungen"),
                "say": "Das waren die Erinnerungen von Brainstorm. Jeden Schalter findest du noch "
                       "einmal in der Anleitung auf GitHub erklärt. Viel Spaß!",
            },
        ],
    },
]
