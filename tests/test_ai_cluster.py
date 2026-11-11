"""Tests for grouping loose notes into themes with the AI."""

from __future__ import annotations

from typing import Any

from homeassistant.core import (
    Context,
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.setup import async_setup_component
import pytest
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.brainstorm.ai import CLUSTER_MAX_THEMES, parse_clusters

from .conftest import SetupEntry

AI_OPTIONS = {"ai_entity": "ai_task.test"}
OLAF = "user-olaf"
FRIDA = "user-frida"


def _register_ai(hass: HomeAssistant, answer: Any) -> list[ServiceCall]:
    """Let the AI give a fixed answer and return the calls it got."""
    calls: list[ServiceCall] = []

    async def generate(call: ServiceCall) -> ServiceResponse:
        calls.append(call)
        return {"data": answer}

    hass.services.async_register(
        "ai_task", "generate_data", generate, supports_response=SupportsResponse.ONLY
    )
    return calls


async def _call(
    hass: HomeAssistant, service: str, user: str | None = OLAF, **data: Any
) -> Any:
    return await hass.services.async_call(
        "brainstorm",
        service,
        data,
        blocking=True,
        return_response=True,
        context=Context(user_id=user),
    )


async def _add(
    hass: HomeAssistant, text: str, category: str = "Alltag", **extra: Any
) -> str:
    response = await _call(hass, "add_idea", text=text, category=category, **extra)
    return response["idea"]["id"]


def test_answer_becomes_themes() -> None:
    """Titles lose their marks, each note counts once, single notes are no theme."""
    answer = (
        "Themen:\n"
        "- **Garten**: L1, L3, L9\n"
        "2. Haus – L2, L4\n"
        "Einzeln: L5\n"
        "Garten: L6, L7\n"
        "„Technik“ (L6, L7, L99, L1)"
    )
    assert parse_clusters(answer, 9) == [
        ("Garten", [0, 2, 8]),
        ("Haus", [1, 3]),
        ("Technik", [5, 6]),
    ]
    assert parse_clusters(None, 5) == []
    assert parse_clusters(": L1, L2", 5) == []
    many = "\n".join(f"Thema {n}: L{2 * n + 1}, L{2 * n + 2}" for n in range(10))
    assert len(parse_clusters(many, 20)) == CLUSTER_MAX_THEMES


async def test_loose_notes_go_to_the_ai(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Only main notes without subtasks are asked about, nothing is stored."""
    calls = _register_ai(hass, "Garten: L1, L3\nHaus: L2, L4\nRest: L5")
    entry = await setup_entry(options=AI_OPTIONS)
    store = entry.runtime_data
    for text in ("Rasen mähen", "Fenster putzen", "Hecke schneiden"):
        await _add(hass, text)
    project = await _add(hass, "Umzug")
    await _add(hass, "Kartons", parent_id=project)
    await _add(hass, "Ganz woanders", category="Projekte")
    assert await store.async_cluster_ideas("Alltag", OLAF, "de") is None

    await _add(hass, "Keller fegen")
    await _add(hass, "Lampe tauschen")
    loose = store.loose_ideas("Alltag", OLAF)
    assert len(loose) == 5
    themes = await store.async_cluster_ideas("Alltag", OLAF, "de")

    instructions = calls[0].data["instructions"]
    assert "„Alltag“" in instructions
    for index, idea in enumerate(loose, 1):
        assert f"L{index}: {idea['text']}" in instructions
    assert "Umzug" not in instructions
    assert "Kartons" not in instructions
    assert "Ganz woanders" not in instructions

    def pick(index: int) -> dict[str, str]:
        return {"idea_id": loose[index]["id"], "text": loose[index]["text"]}

    assert themes == [
        {"title": "Garten", "ideas": [pick(0), pick(2)]},
        {"title": "Haus", "ideas": [pick(1), pick(3)]},
    ]
    assert all(store.get_idea(idea["id"])["parent_id"] is None for idea in loose)

    await store.async_cluster_ideas("Alltag", OLAF, "en")
    assert "Group them into three to seven themes" in calls[1].data["instructions"]


async def test_group_notes_below_a_new_note(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """The new note takes the first place, the notes keep order and subtasks."""
    entry = await setup_entry()
    store = entry.runtime_data
    first = await _add(hass, "Rasen mähen")
    other = await _add(hass, "Fenster putzen")
    second = await _add(hass, "Hecke schneiden")
    child = await _add(hass, "Schere schleifen", parent_id=second)

    response = await _call(hass, "group_ideas", title="  Garten  ", ids=[second, first, second])
    assert response["grouped"] == 2
    group = store.get_idea(response["id"])
    assert group["text"] == "Garten"
    assert group["category"] == "Alltag"
    assert group["parent_id"] is None
    assert store.get_idea(first)["parent_id"] == group["id"]
    assert store.get_idea(second)["parent_id"] == group["id"]
    assert store.get_idea(child)["parent_id"] == second
    assert store.get_idea(other)["parent_id"] is None
    orders = {i: store.get_idea(i)["order"] for i in (first, second, group["id"])}
    assert orders[group["id"]] == min(orders.values())

    # Deleting the new note, as undo does, makes them main notes again
    await _call(hass, "delete_idea", id=group["id"])
    assert store.get_idea(first)["parent_id"] is None
    assert store.get_idea(second)["parent_id"] is None


async def test_group_refuses_bad_input(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A title is needed, the notes share a category and may be changed."""
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Alltag", "Projekte"]},
        options={"privacy_enabled": True, "privacy_owner": OLAF},
    )
    store = entry.runtime_data
    first = await _add(hass, "Rasen mähen")
    second = await _add(hass, "Fenster putzen")
    elsewhere = await _add(hass, "Website", category="Projekte")

    for title, ids, user in (
        ("   ", [first], OLAF),
        ("Mix", [first, elsewhere], OLAF),
        ("Weg", [first, "missing"], OLAF),
        ("Fremd", [first, second], FRIDA),
    ):
        with pytest.raises(ServiceValidationError):
            await _call(hass, "group_ideas", user, title=title, ids=ids)
    assert len(store.ideas) == 3

    await _call(hass, "share", ids=[first, second], shares={FRIDA: "view"})
    with pytest.raises(ServiceValidationError):
        await _call(hass, "group_ideas", FRIDA, title="Fremd", ids=[first, second])
    await _call(hass, "share", ids=[first, second], shares={FRIDA: "edit"})
    response = await _call(hass, "group_ideas", FRIDA, title="Haushalt", ids=[first, second])
    assert store.get_idea(first)["parent_id"] == response["id"]


async def test_websocket_command(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_ws_client: WebSocketGenerator
) -> None:
    """The command answers with themes and explains a missing AI or too few notes."""
    assert await async_setup_component(hass, "websocket_api", {})
    entry = await setup_entry()
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "brainstorm/cluster_ideas", "category": "Alltag"})
    assert (await client.receive_json())["error"]["code"] == "ai_not_configured"

    _register_ai(hass, "Garten: L1, L2")
    hass.config_entries.async_update_entry(entry, options={**entry.options, **AI_OPTIONS})
    await hass.async_block_till_done()
    await client.send_json_auto_id({"type": "brainstorm/cluster_ideas", "category": "Alltag"})
    assert (await client.receive_json())["error"]["code"] == "too_few_notes"

    for text in ("Rasen", "Hecke", "Fenster", "Keller"):
        await hass.services.async_call(
            "brainstorm", "add_idea", {"text": text, "category": "Alltag"}, blocking=True
        )
    await client.send_json_auto_id({"type": "brainstorm/cluster_ideas", "category": "Alltag"})
    reply = await client.receive_json()
    assert [theme["title"] for theme in reply["result"]["themes"]] == ["Garten"]
    assert len(reply["result"]["themes"][0]["ideas"]) == 2
