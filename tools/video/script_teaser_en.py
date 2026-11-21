"""Storyboard: Brainstorm Hub teaser, about 45 seconds (English)."""
from __future__ import annotations

from script_features_en import SPOKEN  # noqa: F401  (used by build.py)

TITLE = "Brainstorm Hub in 45 seconds"
OUT_NAME = "brainstorm-teaser-en"
LANG = "en"
TEASER = True
COVERS = ["Highlights & Features"]

LIST = "card=list&w=620"
MAP = "card=mindmap&w=1180"
AIMAP = 'card=mindmap&w=1180&cfg={"default_category":"Summer party","height":"540px"}&scene=aimap'

CHAPTERS: list[dict] = [
    {"title": "Brainstorm Hub", "scenes": [{
        "v": ("title", "Just say it. Brainstorm sorts it.",
              "Ideas, tasks and shopping for Home Assistant"),
        "say": "Okay, you know the feeling? You have an idea, and two minutes later it's gone. "
               "With Brainstorm, you just say it.",
    }]},
    {"title": "One sentence is enough", "scenes": [{
        "v": ("speech", [
            ("du", "Alexa, tell Brainstorm I really need to call the doctor tomorrow."),
            ("alexa", "Saved under Daily Life, due tomorrow at 9 AM."),
        ], "Alexa, Assist, Siri or the card"),
        "say": "So, one whole sentence to Alexa, Assist or Siri, and Brainstorm turns it into a task, "
               "with a due date, a priority and a category.",
    }]},
    {"title": "Everything in one card", "scenes": [{
        "v": ("live", LIST, 640, 470, 1.0, [
            ("🗂️", "Sorted by <b>category</b>"),
            ("⏰", "Due dates, <b>reminders</b>, repeats"),
            ("👨‍👩‍👧", "Shared with your <b>family</b>"),
        ], ""),
        "actions": [(0.6, "point", "Fix the lawn sprinkler"), (2.0, "click", "Projects"),
                    (5.0, "click", "All")],
        "say": "Everything lands in one card in Home Assistant. Sorted by category, with reminders, "
               "and shared with the whole family.",
    }]},
    {"title": "As a mind map", "scenes": [{
        "v": ("live", MAP, 1184, 470, 0.92, None, ""),
        "actions": [(0.8, "point", "smart mirror"), (2.2, "click", "Projects"), (5.6, "click", "All")],
        "say": "And as a mind map, a board or an outline, you see at once what belongs together.",
    }]},
    {"title": "With AI", "scenes": [{
        "v": ("live", AIMAP, 1184, 470, 0.85, None, ""),
        "actions": [(1.0, "point", "New suggestions"), (3.0, "point", "Add 11")],
        "say": "If you like, the AI builds a whole mind map for you, from a topic, a PDF or a web page.",
    }]},
    {"title": "Wherever you are", "scenes": [{
        "v": ("grid", "Wherever you are", [
            ("📺", "Echo Show", "List and mind map on the display"),
            ("📅", "Calendar", "Due dates in your Home Assistant calendar"),
            ("📱", "Phone", "Reminders as push notifications"),
            ("✉️", "Mail", "Subject “Note: …” becomes a note"),
            ("🤖", "AI assistant", "“The hedge is trimmed” checks it off"),
            ("🔒", "Local", "Your data stays with you"),
        ], "English and German"),
        "say": "On the Echo Show, in your calendar and on your phone. And everything runs locally, at home.",
    }]},
    {"title": "Brainstorm Hub", "scenes": [{
        "v": ("title", "Brainstorm Hub", "Free in the Marketplace · github.com/nukleuz80/ha_brainstorm"),
        "say": "So, that's Brainstorm Hub. Free in the Marketplace. So go ahead and try it today!",
    }]},
]
