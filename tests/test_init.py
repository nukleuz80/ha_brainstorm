"""Tests for setup, services and entities of Brainstorm Hub."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import yaml
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.loader import async_get_integration

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.brainstorm.const import DOMAIN, OVERVIEW_ENTITY_ID
from custom_components.brainstorm.store import get_loaded_store

from .conftest import SetupEntry

SERVICES = {
    "add_idea",
    "update_idea",
    "delete_idea",
    "get_ideas",
    "add_category",
    "set_category_style",
    "remove_category",
    "export_markdown",
    "get_announcement",
    "reorder_ideas",
}


async def test_services_survive_unload_and_report_error(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that services stay registered and fail cleanly without a loaded entry."""
    entry = await setup_entry()
    assert SERVICES <= set(hass.services.async_services()[DOMAIN])

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
    assert SERVICES <= set(hass.services.async_services()[DOMAIN])

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN, "add_idea", {"text": "Neue Notiz hier"}, blocking=True
        )


async def test_reload_keeps_data_and_llm_api(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a reload loads again without duplicate registrations."""
    entry = await setup_entry()
    await hass.services.async_call(
        DOMAIN, "add_idea", {"text": "Neue Notiz hier"}, blocking=True
    )
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert len(entry.runtime_data.ideas) == 1


@pytest.mark.parametrize("service", ["update_idea", "delete_idea"])
async def test_unknown_id_raises(
    hass: HomeAssistant, setup_entry: SetupEntry, service: str
) -> None:
    """Test that services report unknown idea IDs."""
    await setup_entry()
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(DOMAIN, service, {"id": "nope"}, blocking=True)


async def test_overview_sensor(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test sensor entity ID, state, device version and recorder exclusions."""
    entry = await setup_entry()
    await hass.services.async_call(
        DOMAIN, "add_idea", {"text": "Neue Notiz hier"}, blocking=True
    )
    await hass.async_block_till_done()

    state = hass.states.get(OVERVIEW_ENTITY_ID)
    assert state is not None
    assert state.state == "1"
    assert len(state.attributes["ideas"]) == 1
    assert {"ideas", "completed_ideas", "speech_overview"} <= set(
        state.state_info["unrecorded_attributes"]
    )

    integration = await async_get_integration(hass, DOMAIN)
    devices = dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    assert [device.sw_version for device in devices] == [str(integration.version)]


async def test_todo_lists_follow_categories(
    hass: HomeAssistant, setup_entry: SetupEntry, entity_registry: er.EntityRegistry
) -> None:
    """Test that todo entities appear and disappear with their category."""
    entry = await setup_entry()

    def todo_ids() -> set[str]:
        return {
            e.unique_id.split("_todo_")[1]
            for e in er.async_entries_for_config_entry(entity_registry, entry.entry_id)
            if e.domain == "todo"
        }

    assert "alltag" in todo_ids()
    await hass.services.async_call(DOMAIN, "add_category", {"name": "Reisen"}, blocking=True)
    await hass.async_block_till_done()
    assert "reisen" in todo_ids()

    await hass.services.async_call(DOMAIN, "remove_category", {"name": "Reisen"}, blocking=True)
    await hass.async_block_till_done()
    assert "reisen" not in todo_ids()
    assert not [
        s for s in hass.states.async_all("todo") if "reisen" in s.entity_id
    ]
    assert entry.runtime_data.category_counts["Inbox"] == 0

    # Adding the category again creates a working entity again
    await hass.services.async_call(DOMAIN, "add_category", {"name": "Reisen"}, blocking=True)
    await hass.async_block_till_done()
    assert "reisen" in todo_ids()
    assert [s for s in hass.states.async_all("todo") if "reisen" in s.entity_id]


async def test_stale_todo_entity_removed_on_setup(
    hass: HomeAssistant, setup_entry: SetupEntry, entity_registry: er.EntityRegistry
) -> None:
    """Test that entities of categories deleted earlier are cleaned up on reload."""
    entry = await setup_entry()
    await hass.services.async_call(DOMAIN, "add_category", {"name": "Reisen"}, blocking=True)
    await hass.async_block_till_done()
    store = entry.runtime_data
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    entity_registry.async_get_or_create(
        "todo", DOMAIN, f"{entry.entry_id}_todo_alt", config_entry=entry
    )
    store._categories.remove("Reisen")  # noqa: SLF001
    await store.async_save()

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    unique_ids = {
        e.unique_id
        for e in er.async_entries_for_config_entry(entity_registry, entry.entry_id)
    }
    assert f"{entry.entry_id}_todo_alt" not in unique_ids
    assert f"{entry.entry_id}_todo_reisen" not in unique_ids
    assert f"{entry.entry_id}_todo_inbox" in unique_ids


async def test_todo_service_roundtrip_hides_archived(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the todo services and that archived ideas are not listed as open."""
    entry = await setup_entry()
    store = entry.runtime_data
    entity_id = next(
        s.entity_id for s in hass.states.async_all("todo") if "inbox" in s.entity_id
    )
    await hass.services.async_call(
        "todo", "add_item", {"item": "xyz abc"}, target={"entity_id": entity_id}, blocking=True
    )
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == "1"

    idea = store.ideas[0]
    await store.async_update_idea(idea["id"], status="archived")
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == "0"
    response = await hass.services.async_call(
        "todo",
        "get_items",
        {},
        target={"entity_id": entity_id},
        blocking=True,
        return_response=True,
    )
    assert response[entity_id]["items"] == []


def test_services_yaml_descriptions_are_complete() -> None:
    """Test that a hash in a description does not truncate it as a YAML comment."""
    root = Path(__file__).parents[1] / "custom_components/brainstorm"
    services = yaml.safe_load((root / "services.yaml").read_text("utf-8"))
    texts = json.loads((root / "strings.json").read_text("utf-8"))["services"]
    assert set(services) == set(texts)
    for name, service in services.items():
        assert set(service.get("fields") or {}) == set(texts[name].get("fields") or {})
        assert all(field["description"] for field in texts[name].get("fields", {}).values())
    assert "#" in texts["add_category"]["fields"]["color"]["description"]


async def test_setup_retries_when_stored_data_cannot_be_read(
    hass: HomeAssistant,
) -> None:
    """Test that a failing read of the storage makes Home Assistant try again."""
    entry = MockConfigEntry(domain=DOMAIN, title="Brainstorm Hub")
    entry.add_to_hass(hass)
    with patch(
        "custom_components.brainstorm.BrainstormStore.async_load",
        side_effect=HomeAssistantError("disk error"),
    ):
        assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_RETRY
    assert not hass.states.async_entity_ids("todo")


async def test_actions_explain_that_the_entry_is_not_loaded(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the translated error of an action without a loaded entry."""
    entry = await setup_entry()
    assert await hass.config_entries.async_unload(entry.entry_id)
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN, "add_idea", {"text": "Licht reparieren"}, blocking=True
        )
    assert err.value.translation_domain == DOMAIN
    assert err.value.translation_key == "not_loaded"
    root = Path(__file__).parent.parent / "custom_components" / "brainstorm"
    for name in ("strings.json", "translations/en.json", "translations/de.json"):
        texts = json.loads((root / name).read_text("utf-8"))
        assert texts["exceptions"]["not_loaded"]["message"]


async def test_runtime_data_is_the_only_place_of_the_store(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that nothing of a loaded entry is kept in hass.data."""
    entry = await setup_entry()
    assert DOMAIN not in hass.data
    assert get_loaded_store(hass) is entry.runtime_data
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert get_loaded_store(hass) is None


async def test_entities_are_named_relative_to_the_device_and_are_not_polled(
    hass: HomeAssistant, setup_entry: SetupEntry, entity_registry: er.EntityRegistry
) -> None:
    """Test the names of the entities and that they only update when pushed."""
    hass.config.language = "en"
    entry = await setup_entry()
    entries = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
    names = {reg.domain: reg.original_name for reg in entries if reg.domain == "sensor"}
    assert names == {"sensor": "Ideas overview"}
    assert hass.states.get(OVERVIEW_ENTITY_ID).name == "Brainstorm Hub Ideas overview"
    assert "Daily Life" in {reg.original_name for reg in entries if reg.domain == "todo"}
    component = hass.data["entity_components"]
    for domain in ("sensor", "todo"):
        for entity in component[domain].entities:
            if entity.platform.platform_name == DOMAIN:
                assert entity.should_poll is False
                assert entity.has_entity_name is True


async def test_cards_get_an_error_without_a_loaded_entry(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_ws_client: Any
) -> None:
    """Test the answer of the WebSocket command while nothing is loaded."""
    entry = await setup_entry()
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "brainstorm/ideas"})
    assert (await client.receive_json())["success"] is True

    assert await hass.config_entries.async_unload(entry.entry_id)
    await client.send_json_auto_id({"type": "brainstorm/ideas"})
    reply = await client.receive_json()
    assert reply["success"] is False
    assert reply["error"]["code"] == "not_found"
