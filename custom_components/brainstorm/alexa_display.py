"""The lists shown on an Echo with a screen, sent by Home Assistant to the skill."""
from __future__ import annotations

from collections.abc import Iterable
from html import escape
import re
from typing import Any

from .const import ATTR_CATEGORY, ATTR_ID, ATTR_PARENT_ID, ATTR_PRIORITY, ATTR_TEXT

DIRECTIVE_TYPE = "Alexa.Presentation.APL.RenderDocument"
DOCUMENT_TOKEN = "brainstorm-lists"
EVENT_DONE = "done"

# Alexa refuses answers above 120 KB, which these limits stay well below
MAX_DISPLAY_ITEMS = 150
MAX_DISPLAY_TEXT_LENGTH = 120

# Only "payload" gets all data sources instead of the one with its name
DATA_NAME = "brainstorm"

BACKGROUND_COLOR = "#14121f"
TEXT_COLOR = "#ffffff"
DEFAULT_COLOR = "#7c3aed"
PRIORITY_COLORS = {"urgent": "#ef4444", "high": "#f97316", "low": "#94a3b8"}
_HEX_COLOR = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})")

# The whole design lives here, so that changing it needs no new skill code
DOCUMENT: dict[str, Any] = {
    "type": "APL",
    "version": "1.8",
    "theme": "dark",
    "background": BACKGROUND_COLOR,
    "settings": {"idleTimeout": 120000},
    "resources": [
        {
            "dimensions": {
                "titleSize": "32dp",
                "rowSize": "26dp",
                "smallSize": "20dp",
                "checkSize": "36dp",
                "subtaskIndent": "36dp",
            }
        },
        {
            "when": "${viewport.height >= 700}",
            "dimensions": {
                "titleSize": "46dp",
                "rowSize": "36dp",
                "smallSize": "26dp",
                "checkSize": "48dp",
                "subtaskIndent": "56dp",
            },
        },
    ],
    "mainTemplate": {
        "parameters": [DATA_NAME],
        "items": [
            {
                "type": "Frame",
                "width": "100vw",
                "height": "100vh",
                "backgroundColor": BACKGROUND_COLOR,
                "items": [
                    {
                        "type": "Pager",
                        "width": "100vw",
                        "height": "100vh",
                        "navigation": "wrap",
                        "initialPage": f"${{{DATA_NAME}.start}}",
                        "data": f"${{{DATA_NAME}.pages}}",
                        "items": [
                            {
                                "type": "Container",
                                "width": "100%",
                                "height": "100%",
                                "paddingLeft": "${viewport.shape == 'round' ? '12vw' : '4vw'}",
                                "paddingRight": "${viewport.shape == 'round' ? '12vw' : '4vw'}",
                                "paddingTop": "${viewport.shape == 'round' ? '10vh' : '4vh'}",
                                "paddingBottom": "${viewport.shape == 'round' ? '10vh' : '3vh'}",
                                "bind": [{"name": "page", "value": "${data}"}],
                                "items": [
                                    {
                                        "type": "Container",
                                        "direction": "row",
                                        "alignItems": "center",
                                        "paddingBottom": "2vh",
                                        "items": [
                                            {
                                                "type": "Frame",
                                                "width": "10dp",
                                                "height": "@titleSize",
                                                "borderRadius": "5dp",
                                                "backgroundColor": "${page.color}",
                                            },
                                            {
                                                "type": "Text",
                                                "grow": 1,
                                                "shrink": 1,
                                                "paddingLeft": "16dp",
                                                "text": "${page.title}",
                                                "fontSize": "@titleSize",
                                                "color": TEXT_COLOR,
                                                "fontWeight": "bold",
                                                "maxLines": 1,
                                            },
                                            {
                                                "type": "Text",
                                                "paddingLeft": "16dp",
                                                "text": "‹ ${page.position} ›",
                                                "fontSize": "@smallSize",
                                                "color": "#b8b5c9",
                                            },
                                        ],
                                    },
                                    {
                                        "type": "Sequence",
                                        "grow": 1,
                                        "shrink": 1,
                                        "width": "100%",
                                        "data": "${page.items}",
                                        "items": [
                                            {
                                                "type": "Container",
                                                "direction": "row",
                                                "alignItems": "center",
                                                "width": "100%",
                                                "paddingBottom": "1.5vh",
                                                "paddingLeft": "${data.subtask ? @subtaskIndent : 0}",
                                                "items": [
                                                    {
                                                        "type": "TouchWrapper",
                                                        "description": "${page.done_label}",
                                                        "onPress": [
                                                            {
                                                                "type": "SendEvent",
                                                                "arguments": [
                                                                    EVENT_DONE,
                                                                    "${data.id}",
                                                                ],
                                                            }
                                                        ],
                                                        "items": [
                                                            {
                                                                "type": "Frame",
                                                                "width": "@checkSize",
                                                                "height": "@checkSize",
                                                                "borderRadius": "@checkSize",
                                                                "borderWidth": "3dp",
                                                                "borderColor": "${data.color}",
                                                            }
                                                        ],
                                                    },
                                                    {
                                                        "type": "Text",
                                                        "grow": 1,
                                                        "shrink": 1,
                                                        "paddingLeft": "18dp",
                                                        "text": "${data.text}",
                                                        "fontSize": "@rowSize",
                                                        "color": TEXT_COLOR,
                                                        "maxLines": 3,
                                                    },
                                                ],
                                            }
                                        ],
                                    },
                                    {
                                        "type": "Text",
                                        "when": "${page.hint != ''}",
                                        "paddingTop": "1vh",
                                        "text": "${page.hint}",
                                        "fontSize": "@smallSize",
                                        "color": "#b8b5c9",
                                    },
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    },
}


def _safe_text(text: Any) -> str:
    """Return text the APL markup shows as it is, shortened for the screen."""
    cleaned = str(text or "").strip()
    if len(cleaned) > MAX_DISPLAY_TEXT_LENGTH:
        cleaned = f"{cleaned[:MAX_DISPLAY_TEXT_LENGTH - 1].rstrip()}…"
    return escape(cleaned, quote=False)


def _safe_color(color: Any) -> str:
    """Return a color from the settings, as anything else breaks the document."""
    if isinstance(color, str) and _HEX_COLOR.fullmatch(color):
        return color
    return DEFAULT_COLOR


def _with_subtasks(ideas: list[dict[str, Any]]) -> list[tuple[dict[str, Any], bool]]:
    """Put subtasks right after their parent, like the dashboard card."""
    ids = {idea.get(ATTR_ID) for idea in ideas}
    children: dict[Any, list[dict[str, Any]]] = {}
    for idea in ideas:
        if idea.get(ATTR_PARENT_ID) in ids:
            children.setdefault(idea.get(ATTR_PARENT_ID), []).append(idea)

    ordered: list[tuple[dict[str, Any], bool]] = []
    for idea in ideas:
        if idea.get(ATTR_PARENT_ID) not in ids:
            ordered.append((idea, False))
            ordered.extend(
                (child, True) for child in children.get(idea.get(ATTR_ID), [])
            )
    return ordered


def build_directive(
    ideas: list[dict[str, Any]],
    categories: Iterable[str],
    colors: dict[str, str],
    category: str | None,
    german: bool,
) -> dict[str, Any]:
    """Return the directive that shows one swipeable page per category with ideas."""
    done_label = "Als erledigt markieren" if german else "Mark as done"
    grouped: dict[str, list[dict[str, Any]]] = {name: [] for name in categories}
    for idea in ideas:
        grouped.setdefault(str(idea.get(ATTR_CATEGORY)), []).append(idea)
    order = list(grouped)

    pages: list[dict[str, Any]] = []
    remaining = MAX_DISPLAY_ITEMS
    for name, members in grouped.items():
        if not members:
            continue
        rows = _with_subtasks(members)
        shown = rows[: max(remaining, 0)]
        remaining -= len(shown)
        hidden = len(rows) - len(shown)
        color = _safe_color(colors.get(name))
        pages.append(
            {
                "category": name,
                "title": f"{_safe_text(name)} ({len(rows)})",
                "color": color,
                "done_label": done_label,
                "hint": (
                    (f"+ {hidden} weitere" if german else f"+ {hidden} more")
                    if hidden
                    else ""
                ),
                "items": [
                    {
                        "id": idea.get(ATTR_ID),
                        "text": _safe_text(idea.get(ATTR_TEXT)),
                        "subtask": subtask,
                        "color": PRIORITY_COLORS.get(
                            str(idea.get(ATTR_PRIORITY)), color
                        ),
                    }
                    for idea, subtask in shown
                ],
            }
        )

    if not pages:
        pages.append(
            {
                "category": "",
                "title": "Brainstorm",
                "color": DEFAULT_COLOR,
                "done_label": done_label,
                "hint": "Keine offenen Ideen." if german else "No open ideas.",
                "items": [],
            }
        )

    for number, page in enumerate(pages, start=1):
        page["position"] = f"{number} / {len(pages)}"

    # A finished category is gone, so continue with the one that followed it
    start = 0
    if category in grouped:
        position = order.index(category)
        start = next(
            (
                index
                for index, page in enumerate(pages)
                if page["category"] in grouped
                and order.index(page["category"]) >= position
            ),
            len(pages) - 1,
        )

    return {
        "type": DIRECTIVE_TYPE,
        "token": DOCUMENT_TOKEN,
        "document": DOCUMENT,
        "datasources": {DATA_NAME: {"start": start, "pages": pages}},
    }
