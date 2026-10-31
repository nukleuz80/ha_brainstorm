"""Tests for setup, services and entities of Brainstorm Hub."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.loader import async_get_integration

from custom_components.brainstorm.const import DOMAIN, OVERVIEW_ENTITY_ID

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
    path = Path(__file__).parents[1] / "custom_components/brainstorm/services.yaml"
    services = yaml.safe_load(path.read_text("utf-8"))
    assert "#" in services["add_category"]["fields"]["color"]["description"]
    assert "#" in services["set_category_style"]["fields"]["color"]["description"]
