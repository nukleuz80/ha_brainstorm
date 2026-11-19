"""Tests for the mind map on an Echo with a screen."""

from __future__ import annotations

import json
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.brainstorm import alexa_display, alexa_mindmap
from custom_components.brainstorm.alexa_skill import wants_mindmap
from custom_components.brainstorm.languages.de import PACK as GERMAN
from custom_components.brainstorm.languages.en import PACK as ENGLISH

from .conftest import SetupEntry

SKILL_ID = "amzn1.ask.skill.test"


def _texts(graphic: dict[str, Any]) -> list[str]:
    return [item["text"] for item in graphic["items"] if item["type"] == "text"]


def _directive(ideas: list[dict[str, Any]], mindmap: bool = True) -> dict[str, Any]:
    categories = list(dict.fromkeys(str(idea["category"]) for idea in ideas))
    return alexa_display.build_directive(ideas, categories, {}, None, GERMAN, mindmap)


def test_every_page_gets_its_map_and_a_switch() -> None:
    """Category in the middle, tasks around it, switched on the Echo itself."""
    directive = _directive(
        [
            {"id": "a", "text": "Garten", "category": "Haus", "priority": "urgent"},
            {"id": "b", "text": "Rosen", "category": "Haus", "parent_id": "a"},
            {"id": "c", "text": "Licht", "category": "Projekte"},
        ]
    )
    data = directive["datasources"][alexa_display.DATA_NAME]
    graphics = directive["document"]["graphics"]
    assert data["map"] is True
    assert [page["map"] for page in data["pages"]] == [
        "brainstorm-map-0",
        "brainstorm-map-1",
    ]
    assert all("members" not in page for page in data["pages"])
    house = graphics["brainstorm-map-0"]
    assert house["type"] == "AVG"
    assert _texts(house) == ["Haus", "Garten", "Rosen"]
    assert alexa_display.PRIORITY_COLORS["urgent"] in json.dumps(house)
    assert data["pages"][0]["map_label"] == "Mindmap"
    assert data["pages"][0]["list_label"] == "Liste"
    document = json.dumps(directive["document"])
    assert f'"componentId": "{alexa_display.SCREEN_ID}"' in document
    assert '"value": "${brainstorm.map}"' in document
    assert "${index" not in document
    # The shared document stays without the maps of one answer
    assert "graphics" not in alexa_display.DOCUMENT


def test_lists_come_first_unless_the_map_was_asked_for() -> None:
    """Without the wish the lists show, the maps are one touch away."""
    directive = _directive([{"id": "a", "text": "x", "category": "Haus"}], False)
    data = directive["datasources"][alexa_display.DATA_NAME]
    assert data["map"] is False
    assert data["pages"][0]["map"] == "brainstorm-map-0"


def test_empty_screen_has_no_map() -> None:
    """Nothing open, nothing to draw."""
    directive = alexa_display.build_directive([], ["Haus"], {}, None, GERMAN, True)
    data = directive["datasources"][alexa_display.DATA_NAME]
    assert data["map"] is False
    assert data["pages"][0]["map"] == ""
    assert "graphics" not in directive["document"]


def test_long_and_deep_branches_are_counted() -> None:
    """More than fits on a branch or below the last level becomes "+ n"."""
    ideas = [{"id": "p", "text": "Haupt", "category": "Haus"}]
    ideas += [
        {"id": f"k{i}", "text": f"Kind {i}", "category": "Haus", "parent_id": "p"}
        for i in range(10)
    ]
    parent = "k0"
    for depth in range(4):
        ideas.append(
            {
                "id": f"t{depth}",
                "text": f"Tief {depth}",
                "category": "Haus",
                "parent_id": parent,
            }
        )
        parent = f"t{depth}"
    graphic = alexa_mindmap.build_graphic("Haus", ideas, "#7c3aed", {})
    texts = _texts(graphic)
    shown = alexa_mindmap.MAX_CHILDREN
    assert [f"Kind {i}" in texts for i in range(10)] == [True] * shown + [False] * 3
    assert "+ 3" in texts
    # Main task, child and grandchild: three levels below the category
    assert "Tief 0" in texts
    assert "Tief 1" not in texts
    assert "+ 1" in texts


def test_texts_cannot_run_as_expressions() -> None:
    """Strings of an APL document are evaluated, text from ideas must not be."""
    graphic = alexa_mindmap.build_graphic(
        "${viewport}",
        [{"id": "a", "text": "#{x} " + "y" * 80, "category": "c"}],
        "#7c3aed",
        {},
    )
    dumped = json.dumps(graphic)
    assert "${" not in dumped
    assert "#{" not in dumped
    assert any(text.endswith("…") for text in _texts(graphic))


def test_a_small_map_is_not_blown_up() -> None:
    """One task alone keeps a sensible size on the screen."""
    graphic = alexa_mindmap.build_graphic(
        "Haus", [{"id": "a", "text": "x", "category": "Haus"}], "#7c3aed", {}
    )
    assert graphic["width"] >= alexa_mindmap.MIN_WIDTH
    assert graphic["height"] >= alexa_mindmap.MIN_HEIGHT


def test_maps_keep_the_answer_below_the_limit() -> None:
    """Many full categories still stay below Alexa's 120 KB."""
    ideas = [
        {"id": f"{index:08x}", "text": "x" * 500, "category": f"Liste {index % 12}"}
        for index in range(600)
    ]
    directive = _directive(ideas)
    pages = directive["datasources"][alexa_display.DATA_NAME]["pages"]
    assert len(json.dumps(directive).encode()) < 115_000
    assert pages[0]["map"]
    # Pages beyond the room keep their list without a switch
    assert len(directive["document"]["graphics"]) <= len(pages)


def test_mind_map_words() -> None:
    """ "Show the mind map garden" asks for the map, "show garden" not."""
    assert wants_mindmap("die Mindmap Garten", GERMAN)
    assert wants_mindmap("die mind map", GERMAN)
    assert not wants_mindmap("garten", GERMAN)
    assert wants_mindmap("the mind map garden", ENGLISH)


async def test_echo_shows_the_spoken_map(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """ "Zeig mir die Mindmap Projekte" opens the map of that category."""
    hass.config.language = "de"
    assert await async_setup_component(hass, "http", {})
    entry = await setup_entry(options={"voice_mode": "skill"})
    store = entry.runtime_data
    await store.async_add_idea("licht dimmen", category="Projekte")
    client = await hass_client_no_auth()
    url = f"/api/webhook/{store.alexa_skill._webhook_id}"  # noqa: SLF001

    async def show(text: str) -> dict[str, Any]:
        response = await client.post(
            url,
            json={
                "application_id": SKILL_ID,
                "action": "show",
                "text": text,
                "display": True,
            },
        )
        return await response.json()

    answer = await show("die mindmap projekte")
    assert answer["speech"] == "Hier ist die Mindmap Projekte."
    data = answer["directives"][0]["datasources"][alexa_display.DATA_NAME]
    assert data["map"] is True
    answer = await show("mindmap")
    assert answer["speech"] == "Hier sind deine Mindmaps."
    answer = await show("projekte")
    assert answer["speech"] == "Hier ist Projekte."
    assert (
        answer["directives"][0]["datasources"][alexa_display.DATA_NAME]["map"] is False
    )


def test_long_titles_wrap_instead_of_being_cut() -> None:
    """A title too long for one line goes on to a second one."""
    graphic = alexa_mindmap.build_graphic(
        "Haus & Garten",
        [
            {
                "id": "a",
                "text": "Spielhaus wasserdicht machen und streichen",
                "category": "Haus & Garten",
            }
        ],
        "#888888",
        {},
    )
    assert _texts(graphic) == [
        "Haus & Garten",
        "Spielhaus wasserdicht",
        "machen und streichen",
    ]


def test_a_flat_map_spreads_over_the_screen_height() -> None:
    """Few rows get more room between them, the map fills the screen."""
    ideas = [
        {"id": str(number), "text": f"Aufgabe {number}", "category": "Haus"}
        for number in range(6)
    ]
    graphic = alexa_mindmap.build_graphic("Haus", ideas, "#888888", {})
    rows = sorted({item["y"] for item in graphic["items"] if item["type"] == "text"})
    # Rows of 46 units 14 apart would span only 120 from top to bottom
    assert rows[-1] - rows[0] > 180


def test_the_header_keeps_room_before_the_switch() -> None:
    """The list switch does not stick to the category name."""
    found: list[dict[str, Any]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if any(
                isinstance(item, dict) and item.get("text") == "${page.title}"
                for item in node.get("items", [])
            ):
                found.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(alexa_display.DOCUMENT)
    assert found
    assert all(box.get("paddingRight") == "@headerPadding" for box in found)
