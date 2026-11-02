"""The lists shown on an Echo with a screen, sent by Home Assistant to the skill."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import timedelta
from html import escape
import re
from typing import Any

from homeassistant.util import dt as dt_util

from .languages.common import LanguagePack
from .const import (
    ATTR_CATEGORY,
    ATTR_DUE,
    ATTR_ID,
    ATTR_PARENT_ID,
    ATTR_PRIORITY,
    ATTR_TEXT,
)

DIRECTIVE_TYPE = "Alexa.Presentation.APL.RenderDocument"
DOCUMENT_TOKEN = "brainstorm-lists"
EVENT_DONE = "done"

# An Echo loads images itself, so it needs an address it can reach from anywhere
LOGO_URL = (
    "https://raw.githubusercontent.com/nukleuz80/ha_brainstorm/main/"
    "custom_components/brainstorm/brand/icon.png"
)

# Only "payload" gets all data sources instead of the one with its name
DATA_NAME = "brainstorm"

# Alexa refuses answers above 120 KB, which these limits stay well below
MAX_DISPLAY_ITEMS = 150
MAX_DISPLAY_TEXT_LENGTH = 120
MAX_PARENT_LENGTH = 28

BACKGROUND_COLOR = "#14121f"
TILE_COLOR = "#ffffff14"
TEXT_COLOR = "#ffffff"
MUTED_COLOR = "#b8b5c9"
INACTIVE_DOT_COLOR = "#ffffff40"
OVERDUE_COLOR = "#ef4444"
TINT_ALPHA = "33"
# Categories without a chosen color still get pages that look different
PALETTE = (
    "#7c3aed",
    "#0ea5e9",
    "#10b981",
    "#f59e0b",
    "#ec4899",
    "#14b8a6",
    "#6366f1",
    "#84cc16",
)
DEFAULT_COLOR = PALETTE[0]
PRIORITY_COLORS = {"urgent": "#ef4444", "high": "#f97316", "low": "#94a3b8"}
PRIORITY_LABELS = {
    "urgent": "display_prio_urgent",
    "high": "display_prio_high",
    "low": "display_prio_low",
}
_HEX_COLOR = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})")

_HEADER: dict[str, Any] = {
    "type": "Frame",
    "width": "100%",
    "backgroundColor": "${page.tint}",
    "borderRadius": "@tileRadius",
    "items": [
        {
            "type": "Container",
            "direction": "row",
            "alignItems": "center",
            "paddingLeft": "@headerPadding",
            "paddingRight": "@headerPadding",
            "paddingTop": "@headerPaddingY",
            "paddingBottom": "@headerPaddingY",
            "items": [
                {
                    "type": "Image",
                    "source": LOGO_URL,
                    "width": "@logoSize",
                    "height": "@logoSize",
                    "scale": "best-fit",
                },
                {
                    "type": "Container",
                    "grow": 1,
                    "shrink": 1,
                    "paddingLeft": "@headerPadding",
                    "items": [
                        {
                            "type": "Text",
                            "text": "${page.title}",
                            "fontSize": "@titleSize",
                            "fontWeight": "bold",
                            "color": TEXT_COLOR,
                            "maxLines": 1,
                        },
                        {
                            "type": "Text",
                            "when": "${page.subtitle != ''}",
                            "text": "${page.subtitle}",
                            "fontSize": "@smallSize",
                            "color": MUTED_COLOR,
                            "maxLines": 1,
                        },
                    ],
                },
                {
                    "type": "Container",
                    "direction": "row",
                    "alignItems": "center",
                    "data": "${page.dots}",
                    "items": [
                        {
                            "type": "Frame",
                            "width": "@dotSize",
                            "height": "@dotSize",
                            "borderRadius": "@dotSize",
                            "spacing": "@dotSize",
                            "backgroundColor": "${data}",
                        }
                    ],
                },
            ],
        }
    ],
}

_CHECK: dict[str, Any] = {
    "type": "TouchWrapper",
    "width": "@touchSize",
    "height": "100%",
    "description": "${page.done_label}",
    "onPress": [{"type": "SendEvent", "arguments": [EVENT_DONE, "${data.id}"]}],
    "items": [
        {
            "type": "Container",
            "inheritParentState": True,
            "width": "100%",
            "height": "100%",
            "alignItems": "center",
            "justifyContent": "center",
            "items": [
                {
                    "type": "Frame",
                    "style": "checkCircle",
                    "inheritParentState": True,
                    "width": "@checkSize",
                    "height": "@checkSize",
                    "borderRadius": "@checkSize",
                    "borderWidth": "3dp",
                    "borderColor": "${data.accent}",
                }
            ],
        }
    ],
}

_CHIP: dict[str, Any] = {
    "type": "Frame",
    "spacing": "6dp",
    "borderRadius": "@chipRadius",
    "backgroundColor": "${data.tint}",
    "items": [
        {
            "type": "Text",
            "paddingLeft": "10dp",
            "paddingRight": "10dp",
            "text": "${data.text}",
            "fontSize": "@chipSize",
            "color": "${data.color}",
            "maxLines": 1,
        }
    ],
}

_TILE: dict[str, Any] = {
    "type": "Container",
    "width": "100%",
    "height": "100%",
    "padding": "@tileGap",
    "items": [
        {
            "type": "Frame",
            "width": "100%",
            "height": "100%",
            "backgroundColor": TILE_COLOR,
            "borderRadius": "@tileRadius",
            "items": [
                {
                    "type": "Container",
                    "direction": "row",
                    "alignItems": "center",
                    "width": "100%",
                    "height": "100%",
                    "items": [
                        _CHECK,
                        {
                            "type": "Container",
                            "grow": 1,
                            "shrink": 1,
                            "paddingRight": "14dp",
                            "items": [
                                {
                                    "type": "Text",
                                    "text": "${data.text}",
                                    "fontSize": "@rowSize",
                                    "color": TEXT_COLOR,
                                    "maxLines": 2,
                                },
                                {
                                    "type": "Container",
                                    "direction": "row",
                                    "paddingTop": "4dp",
                                    "data": "${data.chips}",
                                    "items": [_CHIP],
                                },
                            ],
                        },
                    ],
                }
            ],
        }
    ],
}

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
                "titleSize": "28dp",
                "logoSize": "54dp",
                "rowSize": "22dp",
                "smallSize": "16dp",
                "chipSize": "14dp",
                "chipRadius": "10dp",
                "checkSize": "32dp",
                "touchSize": "64dp",
                "dotSize": "9dp",
                "tileHeight": "98dp",
                "tileRadius": "16dp",
                "tileGap": "5dp",
                "headerPadding": "14dp",
                "headerPaddingY": "8dp",
            }
        },
        {
            "when": "${viewport.height >= 700}",
            "dimensions": {
                "titleSize": "42dp",
                "logoSize": "80dp",
                "rowSize": "30dp",
                "smallSize": "22dp",
                "chipSize": "20dp",
                "chipRadius": "14dp",
                "checkSize": "44dp",
                "touchSize": "88dp",
                "dotSize": "12dp",
                "tileHeight": "146dp",
                "tileRadius": "22dp",
                "tileGap": "8dp",
                "headerPadding": "20dp",
                "headerPaddingY": "14dp",
            },
        },
    ],
    "styles": {
        "checkCircle": {
            "values": [
                {"backgroundColor": "#00000000"},
                {"when": "${state.pressed}", "backgroundColor": "#ffffff55"},
            ]
        }
    },
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
                                "paddingLeft": "${viewport.shape == 'round' ? '12vw' : '3vw'}",
                                "paddingRight": "${viewport.shape == 'round' ? '12vw' : '3vw'}",
                                "paddingTop": "${viewport.shape == 'round' ? '10vh' : '3vh'}",
                                "paddingBottom": "${viewport.shape == 'round' ? '10vh' : '2vh'}",
                                "bind": [{"name": "page", "value": "${data}"}],
                                "items": [
                                    _HEADER,
                                    {
                                        "type": "GridSequence",
                                        "when": "${!page.empty}",
                                        "width": "100%",
                                        "height": "100%",
                                        "shrink": 1,
                                        "paddingTop": "1vh",
                                        "childWidth": "${viewport.width >= 800 ? '50%' : '100%'}",
                                        "childHeight": "@tileHeight",
                                        "data": "${page.items}",
                                        "items": [_TILE],
                                    },
                                    {
                                        "type": "Text",
                                        "when": "${page.empty}",
                                        "grow": 1,
                                        "textAlign": "center",
                                        "textAlignVertical": "center",
                                        "text": "${page.hint}",
                                        "fontSize": "@titleSize",
                                        "color": MUTED_COLOR,
                                    },
                                    {
                                        "type": "Text",
                                        "when": "${!page.empty && page.hint != ''}",
                                        "paddingTop": "1vh",
                                        "textAlign": "center",
                                        "text": "${page.hint}",
                                        "fontSize": "@smallSize",
                                        "color": MUTED_COLOR,
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


def _safe_text(text: Any, limit: int = MAX_DISPLAY_TEXT_LENGTH) -> str:
    """Return text the APL markup shows as it is, shortened for the screen."""
    cleaned = str(text or "").strip()
    if len(cleaned) > limit:
        cleaned = f"{cleaned[:limit - 1].rstrip()}…"
    return escape(cleaned, quote=False)


def _safe_color(color: Any, fallback: str) -> str:
    """Return a color as #rrggbb, as anything else breaks the document or its tint."""
    if not isinstance(color, str) or not _HEX_COLOR.fullmatch(color):
        return fallback
    if len(color) == 4:
        return "#" + "".join(digit * 2 for digit in color[1:])
    return color[:7]


def _chip(text: str, color: str) -> dict[str, str]:
    """Return a small label below an idea."""
    return {"text": text, "color": color, "tint": f"{color}{TINT_ALPHA}"}


def _due_chip(due: Any, pack: LanguagePack) -> dict[str, str] | None:
    """Return the label of a due date, red once it has passed."""
    parsed = dt_util.parse_datetime(due) if isinstance(due, str) else None
    if parsed is None:
        return None
    local = dt_util.as_local(parsed)
    now = dt_util.now()
    clock = local.strftime("%H:%M")
    if local.date() == now.date():
        text = f"{pack.msg('display_today')} {clock}"
    elif local.date() == (now + timedelta(days=1)).date():
        text = f"{pack.msg('display_tomorrow')} {clock}"
    else:
        text = local.strftime("%d.%m. %H:%M")
    return _chip(text, OVERDUE_COLOR if local < now else MUTED_COLOR)


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


def _row(
    idea: dict[str, Any],
    subtask: bool,
    color: str,
    texts: dict[Any, Any],
    pack: LanguagePack,
) -> dict[str, Any]:
    """Return one tile of a page."""
    priority = str(idea.get(ATTR_PRIORITY))
    accent = PRIORITY_COLORS.get(priority, color)
    chips = []
    if due := _due_chip(idea.get(ATTR_DUE), pack):
        chips.append(due)
    if priority in PRIORITY_LABELS:
        chips.append(_chip(pack.msg(PRIORITY_LABELS[priority]), accent))
    if subtask:
        parent = _safe_text(texts.get(idea.get(ATTR_PARENT_ID)), MAX_PARENT_LENGTH)
        chips.append(_chip(f"↳ {parent}", MUTED_COLOR))
    return {
        "id": idea.get(ATTR_ID),
        "text": _safe_text(idea.get(ATTR_TEXT)),
        "subtask": subtask,
        "accent": accent,
        "chips": chips,
    }


def _subtitle(rows: list[tuple[dict[str, Any], bool]], pack: LanguagePack) -> str:
    """Return how much is open on a page, and how much of it is urgent."""
    urgent = sum(1 for idea, _ in rows if idea.get(ATTR_PRIORITY) == "urgent")
    text = f"{len(rows)} {pack.msg('display_open')}"
    if urgent:
        text += f" · {urgent} {pack.msg('display_urgent')}"
    return text


def build_directive(
    ideas: list[dict[str, Any]],
    categories: Iterable[str],
    colors: dict[str, str],
    category: str | None,
    pack: LanguagePack,
) -> dict[str, Any]:
    """Return the directive that shows one swipeable page per category with ideas."""
    done_label = pack.msg("display_mark_done")
    grouped: dict[str, list[dict[str, Any]]] = {name: [] for name in categories}
    for idea in ideas:
        grouped.setdefault(str(idea.get(ATTR_CATEGORY)), []).append(idea)
    order = list(grouped)
    texts = {idea.get(ATTR_ID): idea.get(ATTR_TEXT) for idea in ideas}

    pages: list[dict[str, Any]] = []
    remaining = MAX_DISPLAY_ITEMS
    for name, members in grouped.items():
        if not members:
            continue
        rows = _with_subtasks(members)
        shown = rows[: max(remaining, 0)]
        remaining -= len(shown)
        hidden = len(rows) - len(shown)
        color = _safe_color(colors.get(name), PALETTE[len(pages) % len(PALETTE)])
        pages.append(
            {
                "category": name,
                "title": _safe_text(name),
                "subtitle": _subtitle(rows, pack),
                "color": color,
                "tint": f"{color}{TINT_ALPHA}",
                "done_label": done_label,
                "empty": False,
                "hint": (
                    pack.msg("display_more", count=hidden)
                    if hidden
                    else ""
                ),
                "items": [
                    _row(idea, subtask, color, texts, pack)
                    for idea, subtask in shown
                ],
            }
        )

    if not pages:
        pages.append(
            {
                "category": "",
                "title": "Brainstorm",
                "subtitle": "",
                "color": DEFAULT_COLOR,
                "tint": f"{DEFAULT_COLOR}{TINT_ALPHA}",
                "done_label": done_label,
                "empty": True,
                "hint": pack.msg("display_no_open"),
                "items": [],
            }
        )

    for number, page in enumerate(pages):
        page["dots"] = [
            TEXT_COLOR if index == number else INACTIVE_DOT_COLOR
            for index in range(len(pages))
        ]

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
