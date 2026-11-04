"""Tests for subtasks the AI suggests on the mind map."""
from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

from homeassistant.core import (
    Context,
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.brainstorm.ai import (
    MAX_SUBTASK_SUGGESTIONS,
    AIUnavailableError,
    parse_subtask_suggestions,
)
from custom_components.brainstorm.const import OVERVIEW_ENTITY_ID

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


def test_parser_cleans_list_marks_and_repeats() -> None:
    """Test that numbers, bullets, headings, quotes and repeats go away."""
    answer = (
        "Unteraufgaben:\n"
        "1. Angebote einholen\n"
        "- **Termin festlegen**\n"
        "* angebote einholen\n"
        "2) „Material kaufen“\n"
        "[ ] Vorhandenes prüfen\n"
        "\n"
        "• Zaun streichen\n"
    )
    assert parse_subtask_suggestions(answer, ["Zaun streichen", "Vorhandenes prüfen"]) == [
        "Angebote einholen",
        "Termin festlegen",
        "Material kaufen",
    ]


def test_parser_limits_count_and_length() -> None:
    """Test that a long answer is cut to a usable list."""
    answer = "\n".join(f"Schritt {n} " + "x" * 300 for n in range(20))
    result = parse_subtask_suggestions(answer, [])
    assert len(result) == MAX_SUBTASK_SUGGESTIONS
    assert all(len(item) <= 200 for item in result)
    assert parse_subtask_suggestions(None, []) == []
    assert parse_subtask_suggestions("  \n- \n", []) == []


async def test_store_asks_with_the_idea_and_its_subtasks(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that only the idea, its category and its subtasks reach the AI."""
    calls = _register_ai(hass, "1. Farbe kaufen\n2. Zaun schleifen\n3. Zaun streichen")
    entry = await setup_entry(options=AI_OPTIONS)
    store = entry.runtime_data
    parent = await store.async_add_idea("Zaun streichen", category="Haus & Garten")
    await store.async_add_idea("Zaun schleifen", parent_id=parent["id"])
    await store.async_add_idea("Geheime andere Idee", category="Inbox")

    suggestions = await store.async_suggest_subtasks(store.get_idea(parent["id"]), "de")

    assert suggestions == ["Farbe kaufen"]
    instructions = calls[0].data["instructions"]
    assert "Zaun streichen" in instructions
    assert "Vorhandene Unteraufgaben: Zaun schleifen" in instructions
    assert "Geheime andere Idee" not in instructions
    assert calls[0].data["entity_id"] == "ai_task.test"
    # Nothing is stored before the person picks
    assert len(store.ideas) == 3


async def test_sensor_tells_the_cards_whether_ai_can_help(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that the cards only show the button with an AI task entity."""
    await setup_entry(options=AI_OPTIONS)
    assert hass.states.get(OVERVIEW_ENTITY_ID).attributes["ai_subtasks"] is True


async def test_sensor_without_ai(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test that the button stays hidden without an AI task entity."""
    await setup_entry()
    assert hass.states.get(OVERVIEW_ENTITY_ID).attributes["ai_subtasks"] is False


async def test_websocket_suggests_for_editable_ideas_only(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
    hass_owner_user: Any,
) -> None:
    """Test that a user only gets suggestions for ideas they may change."""
    assert await async_setup_component(hass, "websocket_api", {})
    calls = _register_ai(hass, "- Liste schreiben\n- Einkaufen gehen")
    entry = await setup_entry(
        options={
            **AI_OPTIONS,
            "privacy_enabled": True,
            "privacy_owner": hass_owner_user.id,
        }
    )
    store = entry.runtime_data
    user = hass.auth.async_validate_access_token(hass_read_only_access_token).user
    own = await store.async_add_idea("Party planen", context=Context(user_id=user.id))
    viewed = await store.async_add_idea(
        "nur lesen", context=Context(user_id=hass_owner_user.id)
    )
    await store.async_set_idea_shares(
        [viewed["id"]], {user.id: "view"}, hass_owner_user.id
    )
    hidden = await store.async_add_idea(
        "privat", context=Context(user_id=hass_owner_user.id)
    )
    client = await hass_ws_client(hass, hass_read_only_access_token)

    await client.send_json_auto_id(
        {"type": "brainstorm/suggest_subtasks", "idea_id": own["id"], "language": "de"}
    )
    reply = await client.receive_json()
    assert reply["result"] == {"suggestions": ["Liste schreiben", "Einkaufen gehen"]}

    await client.send_json_auto_id(
        {"type": "brainstorm/suggest_subtasks", "idea_id": viewed["id"]}
    )
    assert (await client.receive_json())["error"]["code"] == "unauthorized"

    await client.send_json_auto_id(
        {"type": "brainstorm/suggest_subtasks", "idea_id": hidden["id"]}
    )
    assert (await client.receive_json())["error"]["code"] == "not_found"
    # Neither the shared nor the private idea went to the AI
    assert len(calls) == 1


async def test_websocket_explains_missing_or_failing_ai(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    """Test the error codes the card turns into a message."""
    assert await async_setup_component(hass, "websocket_api", {})
    entry = await setup_entry()
    idea = await entry.runtime_data.async_add_idea("Party planen")
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(
        {"type": "brainstorm/suggest_subtasks", "idea_id": idea["id"]}
    )
    assert (await client.receive_json())["error"]["code"] == "ai_not_configured"

    _register_ai(hass, "   ")
    hass.config_entries.async_update_entry(entry, options={**entry.options, **AI_OPTIONS})
    await hass.async_block_till_done()
    store = entry.runtime_data
    idea = await store.async_add_idea("Urlaub planen")
    await client.send_json_auto_id(
        {"type": "brainstorm/suggest_subtasks", "idea_id": idea["id"]}
    )
    assert (await client.receive_json())["error"]["code"] == "ai_failed"


def _register_flaky_ai(hass: HomeAssistant, answers: list[Any]) -> list[ServiceCall]:
    """Let the AI refuse or answer in turn, as an overloaded provider does."""
    calls: list[ServiceCall] = []

    async def generate(call: ServiceCall) -> ServiceResponse:
        calls.append(call)
        answer = answers[min(len(calls), len(answers)) - 1]
        if isinstance(answer, Exception):
            raise answer
        return {"data": answer}

    hass.services.async_register(
        "ai_task", "generate_data", generate, supports_response=SupportsResponse.ONLY
    )
    return calls


async def test_a_refusing_provider_is_asked_once_more(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a short overload of the provider does not reach the person."""
    calls = _register_flaky_ai(
        hass, [HomeAssistantError("503 high demand"), "- Farbe kaufen"]
    )
    entry = await setup_entry(options=AI_OPTIONS)
    store = entry.runtime_data
    idea = await store.async_add_idea("Zaun streichen")
    with patch("custom_components.brainstorm.ai.AI_RETRY_DELAY_SECONDS", 0):
        assert await store.async_suggest_subtasks(idea) == ["Farbe kaufen"]
    assert len(calls) == 2


async def test_websocket_tells_when_the_ai_cannot_be_reached(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    """Test that a provider refusing twice is no empty answer for the card."""
    assert await async_setup_component(hass, "websocket_api", {})
    calls = _register_flaky_ai(hass, [HomeAssistantError("503 high demand")])
    entry = await setup_entry(options=AI_OPTIONS)
    idea = await entry.runtime_data.async_add_idea("Zaun streichen")
    client = await hass_ws_client(hass)
    with patch("custom_components.brainstorm.ai.AI_RETRY_DELAY_SECONDS", 0):
        await client.send_json_auto_id(
            {"type": "brainstorm/suggest_subtasks", "idea_id": idea["id"]}
        )
        reply = await client.receive_json()
    assert reply["error"]["code"] == "ai_unavailable"
    assert len(calls) == 2


async def test_a_slow_ai_is_not_asked_twice(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a timeout ends at once, so the person does not wait twice."""
    calls = _register_flaky_ai(hass, [TimeoutError()])
    entry = await setup_entry(options=AI_OPTIONS)
    store = entry.runtime_data
    idea = await store.async_add_idea("Zaun streichen")
    with pytest.raises(AIUnavailableError) as err:
        await store.async_suggest_subtasks(idea)
    assert err.value.timed_out is True
    assert len(calls) == 1
