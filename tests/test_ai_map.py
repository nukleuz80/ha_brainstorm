"""Tests for a mind map the AI writes from a topic or a text."""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.brainstorm.ai import MAP_MAX_NODES, parse_map_outline

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


def test_outline_becomes_nodes() -> None:
    """Indentation sets the depth; fences, marks and repeats go."""
    answer = (
        "```markdown\n"
        "Sommerfest\n"
        "  - **Essen**\n"
        "    - Grill\n"
        "    - Salate\n"
        "  - Musik\n"
        "    - Playlist\n"
        "      - Ruhige Lieder\n"
        "        - Viel zu tief\n"
        "  - Musik\n"
        "```"
    )
    assert parse_map_outline(answer) == [
        {"text": "Sommerfest", "depth": 0},
        {"text": "Essen", "depth": 1},
        {"text": "Grill", "depth": 2},
        {"text": "Salate", "depth": 2},
        {"text": "Musik", "depth": 1},
        {"text": "Playlist", "depth": 2},
        {"text": "Ruhige Lieder", "depth": 3},
        {"text": "Viel zu tief", "depth": 3},
    ]
    assert parse_map_outline(None) == []
    assert parse_map_outline("Mindmap:\n- Eins") == [{"text": "Eins", "depth": 0}]


def test_depth_never_jumps_and_size_is_capped() -> None:
    """A first line that is indented starts at the top, and long answers stop."""
    assert parse_map_outline("Titel\n      - Tief") == [
        {"text": "Titel", "depth": 0},
        {"text": "Tief", "depth": 1},
    ]
    many = "Titel\n" + "\n".join(f"  - Punkt {n}" for n in range(100))
    assert len(parse_map_outline(many)) == MAP_MAX_NODES


async def test_map_from_a_topic(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """The topic goes to the AI in the prompt language, nothing is stored."""
    calls = _register_ai(hass, "Umzug\n  - Kartons\n    - Klebeband\n  - Ummelden")
    entry = await setup_entry(options=AI_OPTIONS)
    store = entry.runtime_data
    before = len(store.ideas)

    nodes = await store.async_generate_map("  Umzug  ", "de")

    assert nodes == [
        {"text": "Umzug", "depth": 0},
        {"text": "Kartons", "depth": 1},
        {"text": "Klebeband", "depth": 2},
        {"text": "Ummelden", "depth": 1},
    ]
    instructions = calls[0].data["instructions"]
    assert instructions.endswith("Eingabe:\nUmzug")
    assert "höchstens 40 Zeilen" in instructions
    assert len(store.ideas) == before

    await store.async_generate_map("Moving house", "en")
    assert calls[1].data["instructions"].endswith("Input:\nMoving house")


async def test_websocket_command(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_ws_client: WebSocketGenerator
) -> None:
    """The command answers with nodes and explains a missing or empty AI."""
    assert await async_setup_component(hass, "websocket_api", {})
    entry = await setup_entry()
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "brainstorm/generate_map", "text": "Urlaub"})
    assert (await client.receive_json())["error"]["code"] == "ai_not_configured"

    answers = ["Urlaub\n  - Packen", "   "]
    calls: list[ServiceCall] = []

    async def generate(call: ServiceCall) -> ServiceResponse:
        calls.append(call)
        return {"data": answers[min(len(calls), len(answers)) - 1]}

    hass.services.async_register(
        "ai_task", "generate_data", generate, supports_response=SupportsResponse.ONLY
    )
    hass.config_entries.async_update_entry(entry, options={**entry.options, **AI_OPTIONS})
    await hass.async_block_till_done()
    await client.send_json_auto_id({"type": "brainstorm/generate_map", "text": "Urlaub"})
    reply = await client.receive_json()
    assert reply["result"] == {
        "nodes": [{"text": "Urlaub", "depth": 0}, {"text": "Packen", "depth": 1}]
    }

    await client.send_json_auto_id({"type": "brainstorm/generate_map", "text": "Leer"})
    assert (await client.receive_json())["error"]["code"] == "ai_failed"
