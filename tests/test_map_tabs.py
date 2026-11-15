"""Tests for the saved map views shown as tabs above the mind map."""

from __future__ import annotations

from typing import Any

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.brainstorm.const import MAP_TABS_MAX
from custom_components.brainstorm.store import BrainstormStore, _clean_map_tab

from .conftest import SetupEntry


async def _setup(setup_entry: SetupEntry, **stored: Any) -> BrainstormStore:
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Garten", "Keller"], **stored}
    )
    return entry.runtime_data


async def test_tabs_survive_a_restart(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_storage: dict[str, Any]
) -> None:
    """Test that a saved view is stored with its filter, layout and viewport."""
    store = await _setup(setup_entry)
    rev = store.get_public_attributes()["map_tabs_rev"]
    tab = await store.async_save_map_tab(
        {
            "name": "  Beete   vorne ",
            "icon": "🌱",
            "category": "Garten",
            "layout": "tree",
            "filter": {"query": "Beet", "prios": ["high"], "overdue": True},
            "view": {"x": 12.345, "y": -3, "scale": 9},
        },
        "anna",
    )
    assert tab["name"] == "Beete vorne"
    assert tab["private"] is False
    assert tab["view"] == {"x": 12.3, "y": -3.0, "scale": 4.0}
    assert tab["filter"]["prios"] == ["high"] and tab["filter"]["soon"] is False
    assert store.get_public_attributes()["map_tabs_rev"] == rev + 1

    saved = next(v for k, v in hass_storage.items() if "brainstorm" in k)["data"]
    assert saved["map_tabs"][0]["id"] == tab["id"]

    other = BrainstormStore(hass, {})
    other._store = store._store
    await other.async_load()
    assert [t["name"] for t in other.map_tabs("bert")] == ["Beete vorne"]


async def test_private_tabs_and_order(setup_entry: SetupEntry) -> None:
    """Test that a tab only for me stays hidden and others keep their place."""
    store = await _setup(setup_entry)
    shared = await store.async_save_map_tab({"name": "Alle", "category": "all"}, "anna")
    mine = await store.async_save_map_tab(
        {"name": "Meins", "category": "Keller", "private": True}, "anna"
    )
    berts = await store.async_save_map_tab(
        {"name": "Bert", "category": "Garten", "private": True}, "bert"
    )
    assert [t["id"] for t in store.map_tabs("anna")] == [shared["id"], mine["id"]]
    assert [t["id"] for t in store.map_tabs("bert")] == [shared["id"], berts["id"]]

    # Someone else may neither change nor delete a private tab
    assert not await store.async_delete_map_tab(mine["id"], "bert")
    with pytest.raises(ServiceValidationError):  # becomes a new tab without a list
        await store.async_save_map_tab({"id": mine["id"], "name": "Fremd"}, "bert")
    assert store.map_tabs("anna")[1]["name"] == "Meins"

    await store.async_order_map_tabs([mine["id"], shared["id"]], "anna")
    assert [t["id"] for t in store.map_tabs("anna")] == [mine["id"], shared["id"]]
    assert [t["id"] for t in store.map_tabs("bert")] == [shared["id"], berts["id"]]

    # Sharing a private tab makes it visible for everyone
    await store.async_save_map_tab({"id": mine["id"], "private": False}, "anna")
    assert mine["id"] in [t["id"] for t in store.map_tabs("bert")]


async def test_removed_list_moves_tabs_to_inbox(setup_entry: SetupEntry) -> None:
    """Test that a tab of a deleted list follows its notes to the Inbox."""
    store = await _setup(setup_entry)
    tab = await store.async_save_map_tab({"name": "Keller", "category": "Keller"})
    assert await store.async_remove_category("Keller")
    assert store.map_tabs()[0]["category"] == "Inbox"
    assert store.map_tabs()[0]["id"] == tab["id"]


async def test_limit_and_invalid(setup_entry: SetupEntry) -> None:
    """Test the tab limit and a tab without a name."""
    store = await _setup(setup_entry)
    with pytest.raises(ServiceValidationError):
        await store.async_save_map_tab({"name": " ", "category": "Garten"})
    store._map_tabs = [
        {"id": f"t{i}", "name": "x", "category": "Garten", "owner": None}
        for i in range(MAP_TABS_MAX)
    ]
    with pytest.raises(ServiceValidationError):
        await store.async_save_map_tab({"name": "Zu viel", "category": "Garten"})


def test_clean_map_tab() -> None:
    """Test that broken stored tabs are dropped or repaired."""
    assert _clean_map_tab("x") is None
    assert _clean_map_tab({"id": "a", "name": "A"}) is None
    tab = _clean_map_tab(
        {
            "id": "a",
            "name": "A",
            "category": "Garten",
            "layout": "spiral",
            "branch": True,
            "view": {"x": "nan", "y": 0, "scale": 1},
            "filter": {"tags": ["#x", {"bad": 1}]},
        }
    )
    assert tab["layout"] is None
    assert tab["branch"] is False  # a branch tab needs a branch
    assert tab["view"] is None
    assert tab["filter"]["tags"] == ["#x"]
    assert tab["detail"] is None
    assert _clean_map_tab({"id": "a", "name": "A", "category": "G", "detail": "compact"})["detail"] == "compact"
    assert _clean_map_tab({"id": "a", "name": "A", "category": "G", "detail": "tiny"})["detail"] is None


async def test_websocket_commands(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_ws_client: WebSocketGenerator
) -> None:
    """Test the commands the mind map card uses."""
    store = await _setup(setup_entry)
    idea = await store.async_add_idea("Beete", category="Garten")
    client = await hass_ws_client(hass)

    await client.send_json_auto_id(
        {
            "type": "brainstorm/map_tabs/save",
            "name": "Beete",
            "category": "Garten",
            "focus": idea["id"],
            "branch": True,
            "private": True,
            "detail": "compact",
        }
    )
    tab = (await client.receive_json())["result"]["tab"]
    assert tab["branch"] is True and tab["private"] is True
    assert tab["detail"] == "compact"

    await client.send_json_auto_id(
        {"type": "brainstorm/map_tabs/save", "tab_id": tab["id"], "name": "Gemüse"}
    )
    assert (await client.receive_json())["result"]["tab"]["name"] == "Gemüse"

    second = await store.async_save_map_tab({"name": "Alle", "category": "all"})
    await client.send_json_auto_id(
        {"type": "brainstorm/map_tabs/order", "ids": [second["id"], tab["id"]]}
    )
    ordered = (await client.receive_json())["result"]["tabs"]
    assert [t["id"] for t in ordered] == [second["id"], tab["id"]]

    await client.send_json_auto_id({"type": "brainstorm/map_tabs/delete", "tab_id": tab["id"]})
    assert (await client.receive_json())["success"]
    await client.send_json_auto_id({"type": "brainstorm/map_tabs/delete", "tab_id": tab["id"]})
    assert not (await client.receive_json())["success"]

    await client.send_json_auto_id({"type": "brainstorm/map_tabs"})
    assert [t["name"] for t in (await client.receive_json())["result"]["tabs"]] == ["Alle"]

    await client.send_json_auto_id(
        {"type": "brainstorm/map_tabs/save", "name": " ", "category": "Garten"}
    )
    reply = await client.receive_json()
    assert not reply["success"]


async def test_move_branch_to_its_own_map(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a branch moves with all subtasks and its tab, and can go back."""
    store = await _setup(setup_entry)
    house = await store.async_add_idea("Haus", category="Keller")
    garden = await store.async_add_idea("Beete", category="Keller", parent_id=house["id"])
    bed = await store.async_add_idea("Tomaten", category="Keller", parent_id=garden["id"])
    other = await store.async_add_idea("Regal", category="Keller", parent_id=house["id"])
    tab = await store.async_save_map_tab(
        {"name": "Beete", "category": "Keller", "focus": garden["id"], "branch": True}
    )
    response = await hass.services.async_call(
        "brainstorm",
        "move_branch",
        {"id": garden["id"], "category": "  Gemüse  beet "},
        blocking=True,
        return_response=True,
    )
    assert response == {
        "moved": 2,
        "category": "Gemüse beet",
        "from_category": "Keller",
        "from_parent": house["id"],
    }
    assert "Gemüse beet" in store.categories
    assert store.get_idea(garden["id"])["category"] == "Gemüse beet"
    assert store.get_idea(garden["id"])["parent_id"] is None
    assert store.get_idea(bed["id"])["category"] == "Gemüse beet"
    assert store.get_idea(bed["id"])["parent_id"] == garden["id"]
    assert store.get_idea(other["id"])["category"] == "Keller"
    assert next(t for t in store.map_tabs() if t["id"] == tab["id"])["category"] == "Gemüse beet"

    # Back below the old parent
    await hass.services.async_call(
        "brainstorm",
        "move_branch",
        {"id": garden["id"], "category": "Keller", "parent_id": house["id"]},
        blocking=True,
    )
    assert store.get_idea(garden["id"])["parent_id"] == house["id"]
    assert store.get_idea(bed["id"])["category"] == "Keller"

    # A parent in another category or inside the branch is ignored
    await store.async_move_branch(garden["id"], "Garten", bed["id"])
    assert store.get_idea(garden["id"])["parent_id"] is None
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "brainstorm", "move_branch", {"id": garden["id"], "category": "  "}, blocking=True
        )
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "brainstorm", "move_branch", {"id": "nope", "category": "Garten"}, blocking=True
        )
