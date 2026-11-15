"""Tests for linking lists of Local To-do on their own settings page."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.brainstorm.local_todo import (
    CHOICE_NEW,
    CHOICE_NONE,
    async_create_list,
    local_lists,
)

from .conftest import SetupEntry


@pytest.fixture(autouse=True)
def local_storage(hass: HomeAssistant, tmp_path: Path) -> None:
    """Local To-do writes its lists as files next to the storage."""
    hass.config.config_dir = str(tmp_path)
    (tmp_path / ".storage").mkdir()


async def _local_list(hass: HomeAssistant, name: str, *items: str) -> str:
    entity_id = await async_create_list(hass, name)
    for item in items:
        await hass.services.async_call(
            "todo", "add_item", {"item": item}, target={"entity_id": entity_id}, blocking=True
        )
    return entity_id


async def _open_page(hass: HomeAssistant, entry_id: str) -> dict[str, Any]:
    result = await hass.config_entries.options.async_init(entry_id)
    assert "integrations" in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "integrations"}
    )
    assert "local_todo" in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "local_todo"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "local_todo"
    return result


async def _synced(hass: HomeAssistant) -> None:
    await hass.async_block_till_done()
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=10))
    await hass.async_block_till_done()


async def test_take_over_a_list_as_new_category(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A list taken over becomes a category, its items become notes."""
    aufgaben = await _local_list(hass, "Aufgaben", "Fenster putzen", "Keller fegen")
    await _local_list(hass, "Mama")
    assert [item.name for item in local_lists(hass)] == ["Aufgaben", "Mama"]
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox", "Garten"]})

    result = await _open_page(hass, entry.entry_id)
    fields = {str(key) for key in result["data_schema"].schema}
    assert {"Aufgaben", "Mama", "local_todo_new"} <= fields
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"Aufgaben": CHOICE_NEW, "Mama": CHOICE_NONE}
    )
    assert result["step_id"] == "integrations"
    assert entry.options["todo_sync"] == {"Aufgaben": aufgaben}
    await _synced(hass)

    store = entry.runtime_data
    assert "Aufgaben" in store.categories
    texts = {i["text"] for i in store.ideas if i["category"] == "Aufgaben"}
    assert texts == {"Fenster putzen", "Keller fegen"}
    link = store.get_public_attributes()["linked_lists"]["Aufgaben"]
    assert link == {"entity": aufgaben, "name": "Aufgaben", "local": True}

    # The menu shows the pair and the logo in colour
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert "🟢 Lokale To-do" in result["description_placeholders"]["integrations_status"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "integrations"}
    )
    assert result["description_placeholders"]["status_local_todo"] == "an · Aufgaben ↔ Aufgaben"
    hass.config_entries.options.async_abort(result["flow_id"])


async def test_new_local_list_for_a_category(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A category gets a new Local To-do list, its notes go there."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox", "Garten"]})
    store = entry.runtime_data
    await store.async_add_idea("Hecke schneiden", category="Garten")
    assert local_lists(hass) == []

    result = await _open_page(hass, entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"local_todo_new": "Garten"}
    )
    assert result["step_id"] == "integrations"
    lists = local_lists(hass)
    assert [item.name for item in lists] == ["Garten"]
    assert entry.options["todo_sync"] == {"Garten": lists[0].entity_id}
    await _synced(hass)
    items = await hass.services.async_call(
        "todo",
        "get_items",
        {},
        target={"entity_id": lists[0].entity_id},
        blocking=True,
        return_response=True,
    )
    assert [i["summary"] for i in items[lists[0].entity_id]["items"]] == ["Hecke schneiden"]


async def test_one_list_per_category(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Two lists may not share a category, nor a list of another integration."""
    await _local_list(hass, "Aufgaben")
    await _local_list(hass, "Mama")
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Garten"]},
        options={"todo_sync": {"Inbox": "todo.google_tasks"}},
    )
    result = await _open_page(hass, entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"Aufgaben": "Garten", "Mama": "Garten"}
    )
    assert result["errors"] == {"base": "local_todo_duplicate"}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"Aufgaben": "Garten", "Mama": CHOICE_NONE}
    )
    assert result["step_id"] == "integrations"
    # The list of the other integration stays linked
    assert entry.options["todo_sync"]["Inbox"] == "todo.google_tasks"
    assert entry.options["todo_sync"]["Garten"].startswith("todo.")


async def test_general_page_keeps_local_links(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Saving *Link To-do Lists* neither shows nor drops a local link."""
    aufgaben = await _local_list(hass, "Aufgaben")
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Aufgaben"]},
        options={"todo_sync": {"Aufgaben": aufgaben}},
    )
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "todo_sync"}
    )
    fields = {str(key) for key in result["data_schema"].schema}
    assert "Aufgaben" not in fields
    result = await hass.config_entries.options.async_configure(result["flow_id"], {})
    assert entry.options["todo_sync"] == {"Aufgaben": aufgaben}
