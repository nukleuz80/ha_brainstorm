"""Tests for importing an outline from Markdown, OPML and FreeMind."""

from __future__ import annotations

from typing import Any

import pytest

from custom_components.brainstorm.outline import OutlineError, parse_outline
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError

from .conftest import SetupEntry


def _shape(nodes: list[Any]) -> list[tuple[int, str]]:
    return [(n.depth, n.text) for n in nodes]


def test_markdown_headings_lists_and_indents() -> None:
    """Headings, list items and indented lines become one tree."""
    text = """﻿# Umzug

Kartons
## Küche
- Teller
  - Tassen
    * Henkel
- [x] Töpfe
1. Besteck
## Wohnzimmer
\tSofa
\t\tKissen
---
```
- kein Punkt
```
"""
    assert _shape(parse_outline(text)) == [
        (0, "Umzug"),
        (1, "Kartons"),
        (1, "Küche"),
        (2, "Teller"),
        (3, "Tassen"),
        (4, "Henkel"),
        (2, "Töpfe"),
        (2, "Besteck"),
        (1, "Wohnzimmer"),
        (2, "Sofa"),
        (3, "Kissen"),
    ]
    assert [n.done for n in parse_outline(text)][6] is True


def test_markdown_quote_is_a_description() -> None:
    """A quote below a list item is its description, as the cards export it."""
    nodes = parse_outline("# Map\n\n- Dach\n  > Ziegel rot\n  > und neu\n  - Rinne\n")
    assert _shape(nodes) == [(0, "Map"), (1, "Dach"), (2, "Rinne")]
    assert nodes[1].description == "Ziegel rot und neu"


def test_plain_indented_text_and_jumps() -> None:
    """Plain lines nest by indent; a jump of two levels hangs one level deeper."""
    text = "Einkauf\n    Milch\n        Hafer\n  Brot\nArbeit\n            tief"
    assert _shape(parse_outline(text)) == [
        (0, "Einkauf"),
        (1, "Milch"),
        (2, "Hafer"),
        (1, "Brot"),
        (0, "Arbeit"),
        (1, "tief"),
    ]


def test_opml() -> None:
    """OPML outlines keep their notes and done state."""
    text = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0"><head><title>Plan</title></head><body>
  <outline text="Garten" _note="Frühjahr">
    <outline text="Beet" _complete="true"/>
    <outline title="Zaun"><outline text="Farbe &amp; Pinsel"/></outline>
  </outline>
  <outline text="Keller"/>
</body></opml>"""
    nodes = parse_outline(text)
    assert _shape(nodes) == [(0, "Garten"), (1, "Beet"), (1, "Zaun"), (2, "Farbe & Pinsel"), (0, "Keller")]
    assert nodes[0].description == "Frühjahr"
    assert nodes[1].done is True


def test_freemind() -> None:
    """A FreeMind map keeps its root node, rich text and notes."""
    text = """<map version="1.0.1"><node TEXT="Projekt">
  <node TEXT="Idee"><richcontent TYPE="NOTE"><html><body><p>Mehr dazu</p></body></html></richcontent>
    <node><richcontent TYPE="NODE"><html><body><p>Fett <b>gedruckt</b></p></body></html></richcontent></node>
  </node>
</node></map>"""
    nodes = parse_outline(text)
    assert _shape(nodes) == [(0, "Projekt"), (1, "Idee"), (2, "Fett gedruckt")]
    assert nodes[1].description == "Mehr dazu"


def test_bad_outlines_are_refused() -> None:
    """Entities, broken XML and huge outlines are refused."""
    bomb = '<?xml version="1.0"?><!DOCTYPE lolz [<!ENTITY lol "lol">]><opml><body><outline text="&lol;"/></body></opml>'
    with pytest.raises(OutlineError):
        parse_outline(bomb)
    with pytest.raises(OutlineError):
        parse_outline("<opml><body><outline text='x'></body>")
    with pytest.raises(OutlineError):
        parse_outline("\n".join(f"- {i}" for i in range(301)))
    with pytest.raises(OutlineError):
        parse_outline("<map><node TEXT='a'/></map>", "opml")


async def test_import_outline_service(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """The service adds the tree in order, at the top of the list."""
    entry = await setup_entry()
    store = entry.runtime_data
    old = await store.async_add_idea("Alt", category="Inbox")
    result = await hass.services.async_call(
        "brainstorm",
        "import_outline",
        {"text": "# Reise\n- Pass\n- [x] Koffer\n  - Socken\n# Heim", "category": "Inbox"},
        blocking=True,
        return_response=True,
    )
    assert result["added"] == 5
    ids = result["ids"]
    ideas = {i["id"]: i for i in store.ideas}
    trip, passport, case, socks, home = (ideas[i] for i in ids)
    assert trip["parent_id"] is None and home["parent_id"] is None
    assert passport["parent_id"] == trip["id"] and case["parent_id"] == trip["id"]
    assert socks["parent_id"] == case["id"]
    assert case["status"] == "completed"
    assert {i["category"] for i in (trip, socks)} == {"Inbox"}
    order = [i["id"] for i in store.ideas]
    assert order.index(ids[0]) < order.index(ids[-1]) < order.index(old["id"])


async def test_import_below_a_note(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """With a parent the outline hangs below it, in its category."""
    entry = await setup_entry()
    store = entry.runtime_data
    root = await store.async_add_idea("Plan", category="Inbox")
    result = await hass.services.async_call(
        "brainstorm",
        "import_outline",
        {"text": "A\n  B", "parent_id": root["id"], "category": "Anders"},
        blocking=True,
        return_response=True,
    )
    a, b = (store.get_idea(i) for i in result["ids"])
    assert a["parent_id"] == root["id"] and b["parent_id"] == a["id"]
    assert a["category"] == root["category"]

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "brainstorm", "import_outline", {"text": "  \n\n"}, blocking=True
        )
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "brainstorm", "import_outline", {"text": "<opml>", "format": "opml"}, blocking=True
        )
