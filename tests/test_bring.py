"""Tests for syncing all Bring! lists into one category."""
from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import timedelta
from typing import Any
import uuid

import pytest
from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.config_entries import ConfigEntry, ConfigFlow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    MockModule,
    MockPlatform,
    async_mock_service,
    mock_config_flow,
    mock_integration,
    mock_platform,
)

from custom_components.brainstorm.bring import bring_lists, bring_settings
from custom_components.brainstorm.const import ATTR_BRING_LIST, ATTR_TODO_LINK, DOMAIN
from custom_components.brainstorm.store import BrainstormStore

from .conftest import SetupEntry

HOME = "todo.zu_hause"
CAMPER = "todo.camper"


class FakeBringList(TodoListEntity):
    """A to-do list that behaves like one of the Bring! integration.

    Bring keeps each name once per list, moves ticked items to its recent
    list, and gives a renamed item a new ID.
    """

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False
    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
        | TodoListEntityFeature.SET_DESCRIPTION_ON_ITEM
    )

    def __init__(self, list_uuid: str, name: str) -> None:
        """Initialize the list."""
        self._attr_unique_id = list_uuid
        self._attr_device_info = DeviceInfo(identifiers={("bring", list_uuid)}, name=name)
        self.items: list[TodoItem] = []

    @property
    def todo_items(self) -> list[TodoItem]:
        """Return the items."""
        return list(self.items)

    def _find(self, *, uid: str | None = None, summary: str | None = None) -> TodoItem | None:
        for item in self.items:
            if (uid and item.uid == uid) or (summary and item.summary == summary):
                return item
        return None

    def put(self, summary: str, status: TodoItemStatus = TodoItemStatus.NEEDS_ACTION,
            description: str | None = None) -> TodoItem:
        """Add an item directly, like someone in the Bring app."""
        item = TodoItem(summary=summary, uid=uuid.uuid4().hex, status=status,
                        description=description)
        self.items.append(item)
        return item

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Add an item, or bring back the one with the same name."""
        existing = self._find(summary=item.summary)
        if existing is not None:
            existing.status = TodoItemStatus.NEEDS_ACTION
        else:
            self.put(item.summary or "", description=item.description)
        self.async_write_ha_state()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Tick off or rename, a new name giving a new item."""
        current = self._find(uid=item.uid)
        assert current is not None
        if item.summary == current.summary:
            current.status = item.status
            current.description = item.description
        else:
            self.items.remove(current)
            self.put(item.summary or "", item.status or TodoItemStatus.NEEDS_ACTION,
                     item.description)
        self.async_write_ha_state()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Remove items."""
        self.items = [i for i in self.items if i.uid not in uids]
        self.async_write_ha_state()


@pytest.fixture
async def bring(hass: HomeAssistant) -> AsyncIterator[dict[str, FakeBringList]]:
    """Set up a fake Bring! integration with the lists Zu Hause and Camper."""
    lists = {
        HOME: FakeBringList("list-home", "Zu Hause"),
        CAMPER: FakeBringList("list-camper", "Camper"),
    }

    async def setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
        await hass.config_entries.async_forward_entry_setups(entry, ["todo"])
        return True

    async def setup_todo(
        hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback
    ) -> None:
        add(list(lists.values()))

    mock_integration(hass, MockModule("bring", async_setup_entry=setup_entry))
    mock_platform(hass, "bring.todo", MockPlatform(async_setup_entry=setup_todo))
    mock_platform(hass, "bring.config_flow", None)
    entry = MockConfigEntry(domain="bring")
    entry.add_to_hass(hass)
    with mock_config_flow("bring", ConfigFlow):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        assert hass.states.get(HOME) is not None
        yield lists


def _summaries(bring_list: FakeBringList, status: TodoItemStatus | None = None) -> set[str]:
    return {
        i.summary or "" for i in bring_list.items if status is None or i.status == status
    }


async def _sync(hass: HomeAssistant, store: BrainstormStore) -> None:
    assert store.todo_sync is not None
    await store.todo_sync.async_sync()
    await hass.async_block_till_done()


async def _setup(
    setup_entry: SetupEntry, ideas: list[dict[str, Any]] | None = None, **options: Any
) -> BrainstormStore:
    entry = await setup_entry(
        stored={"ideas": ideas or [], "categories": ["Inbox", "Einkauf", "Alltag"]},
        options={
            "bring_enabled": True,
            "bring_category": "Einkauf",
            "bring_default_list": HOME,
            **options,
        },
    )
    return entry.runtime_data


def _note(store: BrainstormStore, entity_id: str) -> dict[str, Any]:
    return next(
        i for i in store.ideas if (i.get(ATTR_BRING_LIST) or {}).get("entity") == entity_id
    )


def _idea(store: BrainstormStore, text: str) -> dict[str, Any]:
    return next(i for i in store.ideas if i["text"] == text and not i.get(ATTR_BRING_LIST))


def test_settings_need_a_switch_and_a_category() -> None:
    """Test reading the Bring settings."""
    assert bring_settings({}) is None
    assert bring_settings({"bring_enabled": True}) is None
    settings = bring_settings(
        {"bring_enabled": True, "bring_category": " Einkauf ", "bring_lists": [HOME]}
    )
    assert settings is not None
    assert settings.category == "Einkauf"
    assert settings.lists == (HOME,)


async def test_lists_are_found_by_their_name(
    hass: HomeAssistant, bring: dict[str, FakeBringList]
) -> None:
    """Test that the Bring lists are found with the names of their devices."""
    assert [(b.entity_id, b.name) for b in bring_lists(hass)] == [
        (CAMPER, "Camper"),
        (HOME, "Zu Hause"),
    ]


async def test_every_list_becomes_a_note_with_its_items(
    hass: HomeAssistant, setup_entry: SetupEntry, bring: dict[str, FakeBringList]
) -> None:
    """Test that lists become main notes and their items subtasks."""
    bring[HOME].put("Milch", description="1,5 l")
    bring[CAMPER].put("Gas")
    bring[CAMPER].put("Kaffee", TodoItemStatus.COMPLETED)
    store = await _setup(setup_entry)
    await _sync(hass, store)

    home, camper = _note(store, HOME), _note(store, CAMPER)
    assert home["text"] == "Zu Hause"
    assert home["category"] == "Einkauf"
    assert camper["text"] == "Camper"
    milk = _idea(store, "Milch")
    assert milk["parent_id"] == home["id"]
    assert milk["spec"] == "1,5 l"
    assert milk[ATTR_TODO_LINK]["entity"] == HOME
    assert _idea(store, "Gas")["parent_id"] == camper["id"]
    # What was bought before stays in Bring and out of Brainstorm
    assert not any(i["text"] == "Kaffee" for i in store.ideas)

    # A second sync adds nothing twice
    await _sync(hass, store)
    assert len(store.ideas) == 4
    assert _summaries(bring[HOME]) == {"Milch"}


async def test_notes_go_to_their_list_or_the_default_list(
    hass: HomeAssistant, setup_entry: SetupEntry, bring: dict[str, FakeBringList]
) -> None:
    """Test that subtasks go to their list and loose notes to the default list."""
    store = await _setup(setup_entry)
    await _sync(hass, store)
    await store.async_add_idea("Brot", category="Einkauf", source="dashboard")
    await store.async_add_idea(
        "Grillkohle", category="Einkauf", source="dashboard",
        parent_id=_note(store, CAMPER)["id"],
    )
    await store.async_add_idea("Rasen mähen", category="Alltag", source="dashboard")
    await _sync(hass, store)

    assert _summaries(bring[HOME]) == {"Brot"}
    assert _summaries(bring[CAMPER]) == {"Grillkohle"}
    assert _idea(store, "Brot")["parent_id"] == _note(store, HOME)["id"]
    assert _idea(store, "Brot")[ATTR_TODO_LINK]["uid"] is not None


async def test_renaming_follows_the_new_id_of_bring(
    hass: HomeAssistant, setup_entry: SetupEntry, bring: dict[str, FakeBringList]
) -> None:
    """Test that a renamed note stays open although Bring gives a new ID."""
    store = await _setup(setup_entry)
    await _sync(hass, store)
    milk = await store.async_add_idea(
        "Milch", category="Einkauf", source="dashboard", parent_id=_note(store, HOME)["id"]
    )
    await _sync(hass, store)
    old_uid = store.get_idea(milk["id"])[ATTR_TODO_LINK]["uid"]

    await store.async_update_idea(milk["id"], text="Hafermilch")
    await _sync(hass, store)
    await _sync(hass, store)
    idea = store.get_idea(milk["id"])
    assert idea["status"] == "active"
    assert idea[ATTR_TODO_LINK]["uid"] not in (None, old_uid)
    assert _summaries(bring[HOME]) == {"Hafermilch"}
    assert len([i for i in store.ideas if not i.get(ATTR_BRING_LIST)]) == 1


async def test_ticking_off_and_buying_again(
    hass: HomeAssistant, setup_entry: SetupEntry, bring: dict[str, FakeBringList]
) -> None:
    """Test that a note for something bought before brings the item back."""
    bring[HOME].put("Eier", TodoItemStatus.COMPLETED)
    store = await _setup(setup_entry)
    await _sync(hass, store)
    home = _note(store, HOME)["id"]

    # Bought in Bring before, the old item comes back
    eggs = await store.async_add_idea(
        "Eier", category="Einkauf", source="dashboard", parent_id=home
    )
    await _sync(hass, store)
    assert _summaries(bring[HOME], TodoItemStatus.NEEDS_ACTION) == {"Eier"}
    assert len(bring[HOME].items) == 1

    # Ticked off in Brainstorm, then noted again: the new note takes the item
    await store.async_update_idea(eggs["id"], status="completed")
    await _sync(hass, store)
    assert _summaries(bring[HOME], TodoItemStatus.COMPLETED) == {"Eier"}
    again = await store.async_add_idea(
        "Eier", category="Einkauf", source="dashboard", parent_id=home
    )
    await _sync(hass, store)
    await _sync(hass, store)
    assert _summaries(bring[HOME], TodoItemStatus.NEEDS_ACTION) == {"Eier"}
    assert len(bring[HOME].items) == 1
    assert store.get_idea(eggs["id"])["status"] == "completed"
    assert ATTR_TODO_LINK not in store.get_idea(eggs["id"])
    assert store.get_idea(again["id"])[ATTR_TODO_LINK]["uid"] is not None


async def test_moving_a_subtask_moves_the_item(
    hass: HomeAssistant, setup_entry: SetupEntry, bring: dict[str, FakeBringList]
) -> None:
    """Test that hanging an item under another list moves it there."""
    bring[HOME].put("Gas")
    store = await _setup(setup_entry)
    await _sync(hass, store)
    gas = _idea(store, "Gas")
    await store.async_update_idea(
        gas["id"], parent_id=_note(store, CAMPER)["id"], update_parent=True
    )
    await _sync(hass, store)
    await _sync(hass, store)
    assert _summaries(bring[HOME]) == set()
    assert _summaries(bring[CAMPER]) == {"Gas"}
    assert store.get_idea(gas["id"])[ATTR_TODO_LINK]["entity"] == CAMPER
    assert len([i for i in store.ideas if i["text"] == "Gas"]) == 1


async def test_list_notes_follow_bring(
    hass: HomeAssistant, setup_entry: SetupEntry, bring: dict[str, FakeBringList]
) -> None:
    """Test that list notes keep their name and come back with their items."""
    bring[CAMPER].put("Gas")
    store = await _setup(setup_entry)
    await _sync(hass, store)
    camper = _note(store, CAMPER)
    await store.async_update_idea(camper["id"], text="Wohnmobil", status="completed")
    await _sync(hass, store)
    assert store.get_idea(camper["id"])["text"] == "Camper"
    assert store.get_idea(camper["id"])["status"] == "active"

    await store.async_delete_idea(camper["id"])
    await _sync(hass, store)
    new_note = _note(store, CAMPER)
    assert new_note["id"] != camper["id"]
    assert _idea(store, "Gas")["parent_id"] == new_note["id"]
    assert _summaries(bring[CAMPER]) == {"Gas"}


async def test_only_chosen_lists_are_synced(
    hass: HomeAssistant, setup_entry: SetupEntry, bring: dict[str, FakeBringList]
) -> None:
    """Test that a list left out keeps its items and archives its note."""
    bring[CAMPER].put("Gas")
    store = await _setup(setup_entry)
    await _sync(hass, store)
    camper = _note(store, CAMPER)

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "bring_lists": [HOME]}
    )
    await hass.async_block_till_done()
    store = entry.runtime_data
    await _sync(hass, store)
    assert store.get_idea(camper["id"])["status"] == "archived"
    assert ATTR_TODO_LINK not in _idea(store, "Gas")
    assert _summaries(bring[CAMPER]) == {"Gas"}


async def test_switched_off_bring_leaves_everything(
    hass: HomeAssistant, setup_entry: SetupEntry, bring: dict[str, FakeBringList]
) -> None:
    """Test that switching Bring off unlinks without deleting anything."""
    bring[HOME].put("Milch")
    store = await _setup(setup_entry)
    await _sync(hass, store)
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "bring_enabled": False}
    )
    await hass.async_block_till_done()
    store = entry.runtime_data
    assert store.todo_sync is not None and not store.todo_sync.active
    assert ATTR_TODO_LINK not in _idea(store, "Milch")
    assert _summaries(bring[HOME]) == {"Milch"}


async def test_bring_lists_leave_the_general_linking(
    hass: HomeAssistant, setup_entry: SetupEntry, bring: dict[str, FakeBringList]
) -> None:
    """Test that a Bring list is never synced twice."""
    store = await _setup(
        setup_entry, todo_sync={"Alltag": CAMPER, "Einkauf": "todo.other"}
    )
    assert store.todo_sync is not None
    assert store.todo_sync.targets == {}


async def test_options_set_up_bring_in_one_page(
    hass: HomeAssistant, setup_entry: SetupEntry, bring: dict[str, FakeBringList]
) -> None:
    """Test the Bring page: a new category, sharing and the default list."""
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Alltag"]},
        options={
            "privacy_enabled": True,
            "privacy_owner": "user-jan",
            "todo_sync": {"Alltag": HOME},
        },
    )
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert "bring" in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "bring"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["description_placeholders"]["lists"] == "Camper, Zu Hause"
    fields = {str(key) for key in result["data_schema"].schema}
    assert {"bring_enabled", "bring_category", "bring_share_all"} <= fields

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"bring_enabled": True, "bring_category": " ", "bring_default_list": HOME},
    )
    assert result["errors"] == {"bring_category": "bring_category_missing"}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "bring_enabled": True,
            "bring_category": "Einkaufen",
            "bring_lists": [CAMPER],
            "bring_default_list": HOME,
        },
    )
    assert result["errors"] == {"bring_default_list": "bring_default_not_chosen"}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "bring_enabled": True,
            "bring_category": "Einkaufen",
            "bring_default_list": HOME,
            "bring_done_days": 5,
            "bring_share_all": True,
        },
    )
    assert result["type"] is FlowResultType.MENU
    await hass.async_block_till_done()
    assert entry.options["bring_category"] == "Einkaufen"
    assert entry.options["bring_done_days"] == 5
    assert entry.options["todo_sync"] == {}
    store = entry.runtime_data
    assert "Einkaufen" in store.categories
    assert store._category_shares["user-jan"]["Einkaufen"] == {"all": "edit"}


async def test_options_hide_bring_without_the_integration(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that the Bring page is only offered with Bring lists."""
    entry = await setup_entry()
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert "bring" not in result["menu_options"]


async def test_list_notes_are_put_back_in_place(
    hass: HomeAssistant, setup_entry: SetupEntry, bring: dict[str, FakeBringList]
) -> None:
    """Test that a moved list note returns and a missing category comes back."""
    store = await _setup(setup_entry, bring_default_list="todo.gone")
    await _sync(hass, store)
    home, camper = _note(store, HOME), _note(store, CAMPER)
    # An unknown default list falls back to the first list by name
    loose = await store.async_add_idea("Brot", category="Einkauf", source="dashboard")
    await _sync(hass, store)
    assert store.get_idea(loose["id"])["parent_id"] == camper["id"]

    await store.async_update_idea(
        home["id"], category="Alltag", parent_id=camper["id"], update_parent=True
    )
    await store.async_remove_category("Einkauf")
    await _sync(hass, store)
    home = store.get_idea(home["id"])
    assert "Einkauf" in store.categories
    assert home["category"] == "Einkauf"
    assert home["parent_id"] is None


async def test_bought_items_are_hidden_after_some_days(
    hass: HomeAssistant, setup_entry: SetupEntry, bring: dict[str, FakeBringList]
) -> None:
    """Test that old ticked off items leave Brainstorm and stay in Bring."""
    store = await _setup(setup_entry, bring_done_days=2)
    await _sync(hass, store)
    home = _note(store, HOME)["id"]
    milk = await store.async_add_idea(
        "Milch", category="Einkauf", source="dashboard", parent_id=home
    )
    bread = await store.async_add_idea(
        "Brot", category="Einkauf", source="dashboard", parent_id=home
    )
    other = await store.async_add_idea("Rasen mähen", category="Alltag", source="dashboard")
    await _sync(hass, store)
    for idea in (milk, bread, other):
        await store.async_update_idea(idea["id"], status="completed")
    await _sync(hass, store)

    # Only what was ticked off long enough ago goes
    old = (dt_util.now() - timedelta(days=3)).isoformat()
    store.get_idea(milk["id"])["updated_at"] = old
    store.get_idea(other["id"])["updated_at"] = old
    await _sync(hass, store)
    assert store.get_idea(milk["id"])["status"] == "archived"
    assert ATTR_TODO_LINK not in store.get_idea(milk["id"])
    assert store.get_idea(bread["id"])["status"] == "completed"
    assert store.get_idea(other["id"])["status"] == "completed"
    assert _note(store, HOME)["status"] == "active"
    assert _summaries(bring[HOME], TodoItemStatus.COMPLETED) == {"Milch", "Brot"}

    # Noted again, the item bought before comes back for the new note
    again = await store.async_add_idea(
        "Milch", category="Einkauf", source="dashboard", parent_id=home
    )
    await _sync(hass, store)
    assert _summaries(bring[HOME], TodoItemStatus.NEEDS_ACTION) == {"Milch"}
    assert len(bring[HOME].items) == 2
    assert store.get_idea(again["id"])[ATTR_TODO_LINK]["uid"] is not None


async def test_zero_days_keeps_bought_items(
    hass: HomeAssistant, setup_entry: SetupEntry, bring: dict[str, FakeBringList]
) -> None:
    """Test that 0 days switches hiding off."""
    store = await _setup(setup_entry, bring_done_days=0)
    await _sync(hass, store)
    milk = await store.async_add_idea(
        "Milch", category="Einkauf", source="dashboard", parent_id=_note(store, HOME)["id"]
    )
    await store.async_update_idea(milk["id"], status="completed")
    store.get_idea(milk["id"])["updated_at"] = "2020-01-01T00:00:00+00:00"
    await _sync(hass, store)
    assert store.get_idea(milk["id"])["status"] == "completed"
    assert await store.async_archive_ideas([milk["id"], "unknown"]) == 1
    assert await store.async_archive_ideas([milk["id"]]) == 0


async def test_messages_go_to_the_right_list(
    hass: HomeAssistant, setup_entry: SetupEntry, bring: dict[str, FakeBringList]
) -> None:
    """Test that a list note and its items send their messages through Bring."""
    calls = async_mock_service(hass, "bring", "send_message")
    store = await _setup(setup_entry)
    await _sync(hass, store)
    camper = _note(store, CAMPER)
    gas = await store.async_add_idea(
        "Gas", category="Einkauf", source="dashboard", parent_id=camper["id"]
    )

    async def send(idea_id: str, message: str) -> dict[str, Any]:
        return await hass.services.async_call(
            DOMAIN,
            "bring_message",
            {"id": idea_id, "message": message},
            blocking=True,
            return_response=True,
        )

    assert await send(camper["id"], "going_shopping") == {
        "entity_id": CAMPER,
        "message": "going_shopping",
    }
    # Not yet linked, the item still finds its list through its note
    await send(gas["id"], "urgent_message")
    await _sync(hass, store)
    await send(gas["id"], "urgent_message")
    assert [(c.data["message"], c.data.get("item"), c.data["entity_id"]) for c in calls] == [
        ("going_shopping", None, CAMPER),
        ("urgent_message", "Gas", CAMPER),
        ("urgent_message", "Gas", CAMPER),
    ]

    # The card learns which notes stand for a list
    details = {i["id"]: i for i in store.get_overview_attributes()["ideas"]}
    assert details[camper["id"]]["bring_list"] == CAMPER
    assert "bring_list" not in details[gas["id"]]

    other = await store.async_add_idea("Rasen mähen", category="Alltag", source="dashboard")
    for idea_id, message, key in (
        (camper["id"], "urgent_message", "bring_urgent_needs_item"),
        (other["id"], "going_shopping", "bring_not_linked"),
        ("unknown", "going_shopping", "idea_not_found"),
    ):
        with pytest.raises(ServiceValidationError) as err:
            await send(idea_id, message)
        assert err.value.translation_key == key
