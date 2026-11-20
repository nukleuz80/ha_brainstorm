"""Storyboard: Brainstorm Hub teaser, about 45 seconds (German)."""
from __future__ import annotations

from pron import SPOKEN  # noqa: F401  (used by build.py)

TITLE = "Brainstorm Hub in 45 Sekunden"
OUT_NAME = "brainstorm-teaser"
TEASER = True
COVERS = ["Highlights & Features"]

LIST = "card=list&w=620"
MAP = "card=mindmap&w=1180"
AIMAP = 'card=mindmap&w=1180&cfg={"default_category":"Sommerfest","height":"540px"}&scene=aimap'

CHAPTERS: list[dict] = [
    {"title": "Brainstorm Hub", "scenes": [{
        "v": ("title", "Einfach sagen. Brainstorm sortiert.",
              "Ideen, Aufgaben und Einkäufe für Home Assistant"),
        "say": "Kennst du das? Dir fällt etwas ein, und zwei Minuten später ist es weg. Mit Brainstorm sagst du es einfach.",
    }]},
    {"title": "Ein Satz genügt", "scenes": [{
        "v": ("speech", [
            ("du", "Alexa, sage Brainstorm: ich muss morgen unbedingt den Arzt anrufen."),
            ("alexa", "Gespeichert unter Alltag, morgen um 9 Uhr."),
        ], "Alexa, Assist, Siri oder die Karte"),
        "say": "Ein ganzer Satz an Alexa, Assist oder Siri, und Brainstorm macht daraus eine Aufgabe, "
               "mit Termin, Priorität und Kategorie.",
    }]},
    {"title": "Alles in einer Karte", "scenes": [{
        "v": ("live", LIST, 640, 470, 1.0, [
            ("🗂️", "Sortiert nach <b>Kategorien</b>"),
            ("⏰", "Termine, <b>Erinnerungen</b>, Wiederholungen"),
            ("👨‍👩‍👧", "Mit der <b>Familie</b> geteilt"),
        ], ""),
        "actions": [(0.6, "point", "Rasensprenger reparieren"), (2.0, "click", "Projekte"),
                    (5.0, "click", "Alle")],
        "say": "Alles landet in einer Karte in Home Assistant. Sortiert nach Kategorien, mit Erinnerungen, "
               "und mit der ganzen Familie geteilt.",
    }]},
    {"title": "Als Mindmap", "scenes": [{
        "v": ("live", MAP, 1184, 470, 0.92, None, ""),
        "actions": [(0.8, "point", "Smart Mirror"), (2.2, "click", "Projekte"), (5.6, "click", "Alle")],
        "say": "Als Mindmap, Kanban oder Gliederung siehst du sofort, was zusammengehört.",
    }]},
    {"title": "Mit KI", "scenes": [{
        "v": ("live", AIMAP, 1184, 470, 0.85, None, ""),
        "actions": [(1.0, "point", "Neue Vorschläge"), (3.0, "point", "übernehmen")],
        "say": "Und auf Wunsch baut dir die KI eine ganze Mindmap, aus einem Thema, einem PDF oder einer Webseite.",
    }]},
    {"title": "Überall dabei", "scenes": [{
        "v": ("grid", "Überall, wo du bist", [
            ("📺", "Echo Show", "Liste und Mindmap am Display"),
            ("📅", "Kalender", "Termine im Home-Assistant-Kalender"),
            ("📱", "Handy", "Erinnerungen als Push"),
            ("✉️", "Mail", "Betreff „Notiz: …“ wird zur Notiz"),
            ("🤖", "KI-Assistent", "„Die Hecke ist geschnitten“ hakt ab"),
            ("🔒", "Lokal", "Deine Daten bleiben bei dir"),
        ], "Deutsch und Englisch"),
        "say": "Auf dem Echo Show, im Kalender und auf dem Handy. Und alles läuft lokal bei dir.",
    }]},
    {"title": "Brainstorm Hub", "scenes": [{
        "v": ("title", "Brainstorm Hub", "Kostenlos über HACS · github.com/nukleuz80/ha_brainstorm"),
        "say": "Brainstorm Hub. Kostenlos über HACS. Probier es aus!",
    }]},
]
