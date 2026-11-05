"""Tests for the description below the title of an idea."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
import pytest
import voluptuous as vol

from .conftest import SetupEntry


def _inbox(hass: HomeAssistant) -> str:
    return next(
        s.entity_id for s in hass.states.async_all("todo") if "inbox" in s.entity_id
    )


async def _items(hass: HomeAssistant, entity_id: str) -> list[dict[str, Any]]:
    response = await hass.services.async_call(
        "todo",
        "get_items",
        {},
        target={"entity_id": entity_id},
        blocking=True,
        return_response=True,
    )
    return response[entity_id]["items"]


async def test_description_through_the_actions(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test adding, changing and removing a description."""
    entry = await setup_entry()
    store = entry.runtime_data
    response = await hass.services.async_call(
        "brainstorm",
        "add_idea",
        {"text": "LED-Leiste", "category": "Inbox", "description": "  5 m, mit Netzteil\n"},
        blocking=True,
        return_response=True,
    )
    idea_id = response["idea"]["id"]
    assert store.get_idea(idea_id)["description"] == "5 m, mit Netzteil"

    await hass.services.async_call(
        "brainstorm",
        "update_idea",
        {"id": idea_id, "text": "LED-Leiste Wohnzimmer"},
        blocking=True,
    )
    assert store.get_idea(idea_id)["description"] == "5 m, mit Netzteil"
    await hass.services.async_call(
        "brainstorm",
        "update_idea",
        {"id": idea_id, "description": "Warmweiß"},
        blocking=True,
    )
    assert store.get_idea(idea_id)["description"] == "Warmweiß"
    await hass.services.async_call(
        "brainstorm", "update_idea", {"id": idea_id, "description": ""}, blocking=True
    )
    assert "description" not in store.get_idea(idea_id)

    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            "brainstorm",
            "update_idea",
            {"id": idea_id, "description": "x" * 4001},
            blocking=True,
        )


async def test_description_reaches_the_cards(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that the overview sensor carries the description."""
    entry = await setup_entry()
    await entry.runtime_data.async_add_idea(
        "Router tauschen", category="Inbox", description="Fritzbox 7590"
    )
    await hass.async_block_till_done()
    ideas = next(
        state.attributes["ideas"]
        for state in hass.states.async_all("sensor")
        if "ideas" in state.attributes
    )
    assert ideas[0]["description"] == "Fritzbox 7590"


async def test_description_in_the_todo_lists(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the description in Home Assistant's own to-do lists."""
    entry = await setup_entry()
    store = entry.runtime_data
    entity_id = _inbox(hass)
    await hass.services.async_call(
        "todo",
        "add_item",
        {"item": "Drucker", "description": "Toner bestellen"},
        target={"entity_id": entity_id},
        blocking=True,
    )
    await hass.async_block_till_done()
    idea = store.ideas[0]
    assert idea["description"] == "Toner bestellen"
    assert (await _items(hass, entity_id))[0]["description"] == "Toner bestellen"

    # Renaming in the to-do list keeps the description
    await hass.services.async_call(
        "todo",
        "update_item",
        {"item": idea["id"], "rename": "Drucker Büro"},
        target={"entity_id": entity_id},
        blocking=True,
    )
    assert store.get_idea(idea["id"])["description"] == "Toner bestellen"

    # Without a description, the line about the source is shown and never stored
    plain = await store.async_add_idea("Kabel", category="Inbox", source="dashboard")
    await hass.async_block_till_done()
    item = next(i for i in await _items(hass, entity_id) if i["uid"] == plain["id"])
    assert item["description"]
    await hass.services.async_call(
        "todo",
        "update_item",
        {"item": plain["id"], "rename": "Kabel HDMI"},
        target={"entity_id": entity_id},
        blocking=True,
    )
    assert "description" not in store.get_idea(plain["id"])
    await hass.services.async_call(
        "todo",
        "update_item",
        {"item": plain["id"], "description": "2 m"},
        target={"entity_id": entity_id},
        blocking=True,
    )
    assert store.get_idea(plain["id"])["description"] == "2 m"


async def test_description_in_json_export_and_import(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a JSON export carries the description and an import keeps it."""
    entry = await setup_entry()
    store = entry.runtime_data
    await store.async_add_idea("Backup prüfen", category="Inbox", description="NAS und SFTP")
    exported = await hass.services.async_call(
        "brainstorm", "export_json", {}, blocking=True, return_response=True
    )
    text = str(exported)
    assert "NAS und SFTP" in text
