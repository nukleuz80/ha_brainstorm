"""Tests for the AI summary of a branch and for sorting in loose notes."""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.brainstorm.ai import clean_summary, parse_parent_suggestions

from .conftest import SetupEntry

AI_OPTIONS = {"ai_entity": "ai_task.test"}


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


def test_summary_is_plain_text() -> None:
    """Headings and list marks go, the text is joined and cut."""
    assert clean_summary("**Zusammenfassung:**\n- Der Zaun ist fast fertig.\n- Farbe fehlt.", 100) == (
        "Der Zaun ist fast fertig. Farbe fehlt."
    )
    assert clean_summary("x" * 50, 10) == "x" * 10
    assert clean_summary("  \n", 10) is None
    assert clean_summary(None, 10) is None


def test_parent_pairs() -> None:
    """Lines like L2 -> K5 become index pairs; repeats and unknown numbers go."""
    answer = "L1 -> K2\nl2: K1\nL1 -> K3\nL9 -> K1\nL3 -> K7\nKeine weitere"
    assert parse_parent_suggestions(answer, 3, 3) == [(0, 1), (1, 0)]
    assert parse_parent_suggestions(None, 3, 3) == []


async def test_summary_of_a_branch(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """The whole branch goes to the AI, nothing else, and nothing is stored."""
    calls = _register_ai(hass, "Der Umzug ist geplant. Kartons fehlen noch.")
    entry = await setup_entry(options=AI_OPTIONS)
    store = entry.runtime_data
    root = await store.async_add_idea("Umzug", category="Inbox")
    boxes = await store.async_add_idea("Kartons", parent_id=root["id"])
    await store.async_add_idea("Klebeband", parent_id=boxes["id"])
    await store.async_add_idea("Anderes Thema", category="Inbox")

    summary = await store.async_summarize_branch(store.get_idea(root["id"]), None, "de")

    assert summary == "Der Umzug ist geplant. Kartons fehlen noch."
    instructions = calls[0].data["instructions"]
    assert "Notiz: Umzug" in instructions
    assert "- Kartons\n  - Klebeband" in instructions
    assert "Anderes Thema" not in instructions
    assert not store.get_idea(root["id"]).get("description")


async def test_summary_needs_subtasks(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """A note without subtasks has nothing to sum up."""
    calls = _register_ai(hass, "egal")
    entry = await setup_entry(options=AI_OPTIONS)
    store = entry.runtime_data
    alone = await store.async_add_idea("Allein", category="Inbox")
    assert await store.async_summarize_branch(store.get_idea(alone["id"]), None) is None
    assert not calls


async def test_loose_notes_get_parents(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Loose main notes get a parent from the same category, without rings."""
    entry = await setup_entry(options=AI_OPTIONS)
    store = entry.runtime_data
    garden = await store.async_add_idea("Garten", category="Inbox")
    await store.async_add_idea("Rasen mähen", parent_id=garden["id"], category="Inbox")
    hedge = await store.async_add_idea("Hecke schneiden", category="Inbox")
    paint = await store.async_add_idea("Zaun streichen", category="Inbox")
    await store.async_add_idea("Fremd", category="Haus & Garten")

    # Candidates: Garten (has subtasks) first, then the rest in list order
    notes = [i for i in store.ideas if i["category"] == "Inbox" and i["status"] == "active"]
    with_kids = [i for i in notes if any(c.get("parent_id") == i["id"] for c in notes)]
    candidates = with_kids + [i for i in notes if i not in with_kids]
    loose = [i for i in notes if not i.get("parent_id") and i not in with_kids]
    k = {i["id"]: n for n, i in enumerate(candidates, 1)}
    lo = {i["id"]: n for n, i in enumerate(loose, 1)}
    answer = (
        f"L{lo[hedge['id']]} -> K{k[garden['id']]}\n"
        f"L{lo[paint['id']]} -> K{k[hedge['id']]}\n"
        f"L{lo[hedge['id']]} -> K{k[paint['id']]}\n"
    )
    calls = _register_ai(hass, answer)

    suggestions = await store.async_suggest_parents("Inbox", None, "de")

    assert [(s["text"], s["parent_text"]) for s in suggestions] == [
        ("Hecke schneiden", "Garten"),
        ("Zaun streichen", "Hecke schneiden"),
    ]
    instructions = calls[0].data["instructions"]
    assert f"L{lo[hedge['id']]}: Hecke schneiden" in instructions
    assert f"K{k[garden['id']]}: Garten" in instructions
    assert "Fremd" not in instructions and "Rasen" in instructions
    assert store.get_idea(hedge["id"]).get("parent_id") is None


async def test_websocket_commands(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_ws_client: WebSocketGenerator
) -> None:
    """Both commands answer, and explain a missing AI or nothing to sort."""
    assert await async_setup_component(hass, "websocket_api", {})
    entry = await setup_entry()
    store = entry.runtime_data
    root = await store.async_add_idea("Umzug", category="Inbox")
    await store.async_add_idea("Kartons", parent_id=root["id"])
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "brainstorm/summarize_branch", "idea_id": root["id"]})
    assert (await client.receive_json())["error"]["code"] == "ai_not_configured"

    _register_ai(hass, "Kurz gesagt: alles gut.")
    hass.config_entries.async_update_entry(entry, options={**entry.options, **AI_OPTIONS})
    await hass.async_block_till_done()
    await client.send_json_auto_id({"type": "brainstorm/summarize_branch", "idea_id": root["id"]})
    reply = await client.receive_json()
    assert reply["result"] == {"summary": "Kurz gesagt: alles gut.", "can_edit": True}

    await client.send_json_auto_id({"type": "brainstorm/suggest_parents", "category": "Leer"})
    assert (await client.receive_json())["error"]["code"] == "ai_failed"
