"""Tests for keeping a category in step with a to-do list of another integration."""
from __future__ import annotations

from collections.abc import Generator
from datetime import timedelta
from typing import Any
from unittest.mock import patch

import pytest
from homeassistant.core import Context, HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.brainstorm.const import ATTR_TODO_LINK, DOMAIN
from custom_components.brainstorm.store import BrainstormStore
from custom_components.brainstorm.todo_sync import sync_targets

from .conftest import SetupEntry

SHOPPING = "todo.einkaufsliste"


@pytest.fixture(autouse=True)
def no_shopping_list_file() -> Generator[None]:
    """Keep the shopping list in memory instead of a file in the config folder."""
    with (
        patch(
            "homeassistant.components.shopping_list.common.load_json_array",
            return_value=[],
        ),
        patch("homeassistant.components.shopping_list.common.ShoppingData.save"),
    ):
        yield


async def _shopping_list(hass: HomeAssistant) -> None:
    """Set up Home Assistant's own shopping list as the other to-do list."""
    entry = MockConfigEntry(domain="shopping_list")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def _items(hass: HomeAssistant) -> dict[str, dict[str, Any]]:
    """Return the items of the shopping list by their text."""
    response = await hass.services.async_call(
        "todo",
        "get_items",
        {"status": ["needs_action", "completed"]},
        target={"entity_id": SHOPPING},
        blocking=True,
        return_response=True,
    )
    return {item["summary"]: item for item in response[SHOPPING]["items"]}


async def _todo(hass: HomeAssistant, service: str, **data: Any) -> None:
    """Change the shopping list like a person in its app would."""
    await hass.services.async_call(
        "todo", service, data, target={"entity_id": SHOPPING}, blocking=True
    )


async def _sync(hass: HomeAssistant, store: BrainstormStore) -> None:
    """Run one sync and let what it started finish."""
    assert store.todo_sync is not None
    await store.todo_sync.async_sync()
    await hass.async_block_till_done()


async def _linked(
    hass: HomeAssistant, setup_entry: SetupEntry, **extra: Any
) -> BrainstormStore:
    """Set up the shopping list and Brainstorm with 'Einkauf' linked to it."""
    await _shopping_list(hass)
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Einkauf", "Alltag"]},
        options={"todo_sync": {"Einkauf": SHOPPING}, **extra},
    )
    return entry.runtime_data


def _idea(store: BrainstormStore, text: str) -> dict[str, Any]:
    """Return the idea with this text."""
    return next(i for i in store.ideas if i["text"] == text)


def test_sync_targets_ignore_what_is_no_todo_entity() -> None:
    """Test that only to-do entities count as linked lists."""
    assert sync_targets({}) == {}
    assert sync_targets(
        {"todo_sync": {"Einkauf": SHOPPING, "Alltag": "light.kitchen", "X": None}}
    ) == {"Einkauf": SHOPPING}


async def test_both_sides_get_what_the_other_has(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that ideas go to the list and new items come back as ideas."""
    store = await _linked(hass, setup_entry)
    await store.async_add_idea("Milch", category="Einkauf", source="dashboard")
    await store.async_add_idea("Rasen mähen", category="Alltag", source="dashboard")
    await _todo(hass, "add_item", item="eier vom bauern")
    await _sync(hass, store)

    assert set(await _items(hass)) == {"Milch", "eier vom bauern"}
    # Taken over word for word, so the item keeps its name on the other list
    taken = _idea(store, "eier vom bauern")
    assert taken["category"] == "Einkauf"
    assert taken["source"] == "todo_sync"
    assert taken[ATTR_TODO_LINK]["entity"] == SHOPPING
    milk = _idea(store, "Milch")
    assert milk[ATTR_TODO_LINK]["uid"] == (await _items(hass))["Milch"]["uid"]

    # A second sync finds nothing new and adds nothing twice
    await _sync(hass, store)
    assert len(await _items(hass)) == 2
    assert len([i for i in store.ideas if i["category"] == "Einkauf"]) == 2


async def test_an_item_with_the_same_text_is_linked_not_doubled(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that coupling a list that already holds an entry does not double it."""
    store = await _linked(hass, setup_entry)
    await _todo(hass, "add_item", item="Brot")
    await store.async_add_idea("brot", category="Einkauf", source="manual", verbatim=True)
    await _sync(hass, store)
    # Coupled for the first time, the spelling on the list wins
    assert list(await _items(hass)) == ["Brot"]
    assert [i["text"] for i in store.ideas] == ["Brot"]
    await _sync(hass, store)
    assert list(await _items(hass)) == ["Brot"]


async def test_ticking_off_works_both_ways(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that completing on either side completes on the other."""
    store = await _linked(hass, setup_entry)
    milk = await store.async_add_idea("Milch", category="Einkauf", source="dashboard")
    bread = await store.async_add_idea("Brot", category="Einkauf", source="dashboard")
    await _sync(hass, store)

    await _todo(hass, "update_item", item="Milch", status="completed")
    await store.async_update_idea(bread["id"], status="completed")
    await _sync(hass, store)
    assert store.get_idea(milk["id"])["status"] == "completed"
    assert (await _items(hass))["Brot"]["status"] == "completed"

    # Reopened on the list, the idea is open again
    await _todo(hass, "update_item", item="Milch", status="needs_action")
    await _sync(hass, store)
    assert store.get_idea(milk["id"])["status"] == "active"


async def test_renaming_works_both_ways(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a new name on either side reaches the other."""
    store = await _linked(hass, setup_entry)
    milk = await store.async_add_idea("Milch", category="Einkauf", source="dashboard")
    bread = await store.async_add_idea("Brot", category="Einkauf", source="dashboard")
    await _sync(hass, store)

    await _todo(hass, "update_item", item="Milch", rename="Hafermilch")
    await store.async_update_idea(bread["id"], text="Vollkornbrot")
    await _sync(hass, store)
    assert store.get_idea(milk["id"])["text"] == "Hafermilch"
    assert set(await _items(hass)) == {"Hafermilch", "Vollkornbrot"}


async def test_a_change_on_the_list_wins_over_one_in_brainstorm(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that both sides renaming the same entry keeps the list's name."""
    store = await _linked(hass, setup_entry)
    milk = await store.async_add_idea("Milch", category="Einkauf", source="dashboard")
    await _sync(hass, store)
    await _todo(hass, "update_item", item="Milch", rename="Hafermilch")
    await store.async_update_idea(milk["id"], text="Sojamilch")
    await _sync(hass, store)
    assert store.get_idea(milk["id"])["text"] == "Hafermilch"
    assert list(await _items(hass)) == ["Hafermilch"]


async def test_deleting_and_removing(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a deleted idea leaves the list and a removed item completes its idea."""
    store = await _linked(hass, setup_entry)
    milk = await store.async_add_idea("Milch", category="Einkauf", source="dashboard")
    bread = await store.async_add_idea("Brot", category="Einkauf", source="dashboard")
    await _sync(hass, store)

    await store.async_delete_idea(milk["id"])
    await _todo(hass, "remove_item", item=["Brot"])
    await _sync(hass, store)
    assert list(await _items(hass)) == []
    assert store.get_idea(bread["id"])["status"] == "completed"
    assert ATTR_TODO_LINK not in store.get_idea(bread["id"])

    # Brought back, the idea gets a new item instead of completing itself
    await store.async_restore_idea(milk["id"])
    await _sync(hass, store)
    assert store.get_idea(milk["id"])["status"] == "active"
    assert list(await _items(hass)) == ["Milch"]


async def test_moving_an_idea_away_removes_its_item(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that an idea moved to an unlinked category leaves the list."""
    store = await _linked(hass, setup_entry)
    milk = await store.async_add_idea("Milch", category="Einkauf", source="dashboard")
    await _sync(hass, store)
    await store.async_update_idea(milk["id"], category="Alltag")
    await _sync(hass, store)
    assert await _items(hass) == {}
    assert ATTR_TODO_LINK not in store.get_idea(milk["id"])


async def test_completed_ideas_are_not_added(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that coupling a list does not fill it with what is done already."""
    store = await _linked(hass, setup_entry)
    done = await store.async_add_idea("Mehl", category="Einkauf", source="dashboard")
    await store.async_update_idea(done["id"], status="completed")
    await _todo(hass, "add_item", item="Zucker")
    await _todo(hass, "update_item", item="Zucker", status="completed")
    await _sync(hass, store)
    assert set(await _items(hass)) == {"Zucker"}
    assert [i["text"] for i in store.ideas] == ["Mehl"]


async def test_private_ideas_stay_off_the_list(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that with privacy only ideas shared with everyone are synced."""
    store = await _linked(
        hass, setup_entry, privacy_enabled=True, privacy_owner="user-jan"
    )
    await store.async_add_idea(
        "Geschenk", category="Einkauf", context=Context(user_id="user-jan")
    )
    await store.async_add_idea(
        "Milch", category="Einkauf", source="dashboard", shares={"all": "edit"}
    )
    await _todo(hass, "add_item", item="Butter")
    await _sync(hass, store)
    assert set(await _items(hass)) == {"Milch", "Butter"}
    # What comes from the list is meant for everyone who can open it
    assert _idea(store, "Butter")["shares"] == {"all": "edit"}


async def test_changes_start_a_sync_on_their_own(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a change on either side starts a sync without being asked."""
    store = await _linked(hass, setup_entry)
    await store.async_add_idea("Milch", category="Einkauf", source="dashboard")
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=2))
    await hass.async_block_till_done()
    assert list(await _items(hass)) == ["Milch"]

    await _todo(hass, "add_item", item="Käse")
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=4))
    await hass.async_block_till_done()
    assert {i["text"] for i in store.ideas} == {"Milch", "Käse"}

    # A rename does not change the state of the list, the interval catches it
    await _todo(hass, "update_item", item="Käse", rename="Bergkäse")
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=6))
    await hass.async_block_till_done()
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=6, seconds=2))
    await hass.async_block_till_done()
    assert {i["text"] for i in store.ideas} == {"Milch", "Bergkäse"}


async def test_a_missing_list_is_logged_once(
    hass: HomeAssistant, setup_entry: SetupEntry, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that a list that is gone neither breaks Brainstorm nor floods the log."""
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Einkauf"]},
        options={"todo_sync": {"Einkauf": "todo.gone", "Weg": SHOPPING}},
    )
    store = entry.runtime_data
    await store.async_add_idea("Milch", category="Einkauf", source="dashboard")
    await _sync(hass, store)
    await _sync(hass, store)
    assert caplog.text.count("Could not sync category Einkauf") == 1


async def test_unlinking_keeps_the_items_and_drops_the_links(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that clearing the setting leaves the other list alone."""
    store = await _linked(hass, setup_entry)
    milk = await store.async_add_idea("Milch", category="Einkauf", source="dashboard")
    await _sync(hass, store)
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    hass.config_entries.async_update_entry(entry, options={"todo_sync": {}})
    await hass.async_block_till_done()
    store = entry.runtime_data
    assert ATTR_TODO_LINK not in store.get_idea(milk["id"])
    assert list(await _items(hass)) == ["Milch"]


async def test_options_link_lists_once_each(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the settings page that links categories to lists."""
    await _shopping_list(hass)
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox", "Einkauf"]})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert "todo_sync" in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "todo_sync"}
    )
    assert result["type"] is FlowResultType.FORM
    fields = {str(key): key for key in result["data_schema"].schema}
    assert {"Inbox", "Einkauf", "go_back"} <= set(fields)
    own = [
        e.entity_id
        for e in hass.states.async_all("todo")
        if e.entity_id.startswith("todo.") and e.entity_id != SHOPPING
    ]
    excluded = result["data_schema"].schema[fields["Einkauf"]].config["exclude_entities"]
    assert set(own) <= set(excluded)
    assert SHOPPING not in excluded

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"Inbox": SHOPPING, "Einkauf": SHOPPING}
    )
    assert result["errors"] == {"base": "todo_sync_duplicate"}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"Einkauf": SHOPPING}
    )
    assert result["type"] is FlowResultType.MENU
    await hass.async_block_till_done()
    assert entry.options["todo_sync"] == {"Einkauf": SHOPPING}


async def test_an_item_shown_late_is_linked_later(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that an idea waiting for its new item finds it at a later sync."""
    await _shopping_list(hass)
    await _todo(hass, "add_item", item="Milch")
    entry = await setup_entry(
        stored={
            "ideas": [
                {
                    "id": "milk0001",
                    "text": "Hafermilch",
                    "category": "Einkauf",
                    "status": "active",
                    "todo_link": {"entity": SHOPPING, "uid": None, "summary": "Milch",
                                  "status": "needs_action", "due": None},
                },
                {
                    "id": "other001",
                    "text": "Brot",
                    "category": "Einkauf",
                    "status": "active",
                    "todo_link": {"entity": "todo.gone", "uid": "x"},
                },
            ],
            "categories": ["Inbox", "Einkauf", "Alltag"],
        },
        options={"todo_sync": {"Einkauf": SHOPPING, "Alltag": "todo.gone"}},
    )
    store = entry.runtime_data
    await _sync(hass, store)
    assert store.get_idea("milk0001")["todo_link"]["uid"] is not None
    # The newer name in Brainstorm reaches the list, the other link is replaced
    assert set(await _items(hass)) == {"Hafermilch", "Brot"}
    assert store.get_idea("other001")["todo_link"]["entity"] == SHOPPING


async def test_the_same_new_name_on_both_sides_changes_nothing_more(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that both sides renaming alike settles without further calls."""
    store = await _linked(hass, setup_entry)
    milk = await store.async_add_idea("Milch", category="Einkauf", source="dashboard")
    await _sync(hass, store)
    await _todo(hass, "update_item", item="Milch", rename="Hafermilch")
    await store.async_update_idea(milk["id"], text="Hafermilch")
    await _sync(hass, store)
    assert store.get_idea(milk["id"])["todo_link"]["summary"] == "Hafermilch"
    assert list(await _items(hass)) == ["Hafermilch"]


async def test_due_times_use_what_the_list_understands(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a due time becomes a date and time, a date or nothing."""
    store = await _linked(hass, setup_entry)
    manager = store.todo_sync
    due = "2026-11-10T18:30:00+01:00"
    hass.states.async_set("todo.both", "0", {"supported_features": 64 | 32})
    hass.states.async_set("todo.date", "0", {"supported_features": 16})
    local = dt_util.as_local(dt_util.parse_datetime(due))
    assert manager._due_data("todo.both", due) == {"due_datetime": local.isoformat()}
    assert manager._due_data("todo.date", due) == {"due_date": local.date().isoformat()}
    assert manager._due_data(SHOPPING, due) == {}
    assert manager._due_data(SHOPPING, None) == {}


async def test_a_failing_change_is_logged(
    hass: HomeAssistant, setup_entry: SetupEntry, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that a list refusing a change does not stop the sync."""
    store = await _linked(hass, setup_entry)
    await store.todo_sync._async_call(SHOPPING, "update_item", {"item": "gibt es nicht"})
    assert "update_item on todo.einkaufsliste failed" in caplog.text


async def test_options_back_saves_nothing(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that going back from the list page keeps the old setting."""
    entry = await setup_entry(options={"todo_sync": {"Inbox": SHOPPING}})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "todo_sync"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"go_back": True}
    )
    assert result["type"] is FlowResultType.MENU
    assert entry.options["todo_sync"] == {"Inbox": SHOPPING}
