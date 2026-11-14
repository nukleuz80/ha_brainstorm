"""Tests for the trash that keeps deleted notes for 30 days."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import Context, HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.brainstorm.store import TRASH_DAYS, BrainstormStore

from .conftest import SetupEntry


async def _setup(setup_entry: SetupEntry, **stored: Any) -> BrainstormStore:
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Smarthome"], **stored}
    )
    return entry.runtime_data


async def test_trash_survives_a_restart(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_storage: dict[str, Any]
) -> None:
    """Test that a deleted note is saved with its subtasks and comes back."""
    store = await _setup(setup_entry)
    parent = await store.async_add_idea("Garten planen", category="Smarthome")
    child = await store.async_add_idea("Beet umgraben", parent_id=parent["id"])
    await store.async_delete_idea(parent["id"], context=Context(user_id="anna"))
    await hass.async_block_till_done()

    saved = next(v for k, v in hass_storage.items() if "brainstorm" in k)["data"]
    assert [entry["idea"]["id"] for entry in saved["trash"]] == [parent["id"]]
    assert saved["trash"][0]["orphans"] == [child["id"]]
    assert saved["trash"][0]["deleted_at"]

    # A fresh store reads the trash back, as after a restart
    other = BrainstormStore(hass, {})
    other._store = store._store
    await other.async_load()
    items = other.trash_items("anna")
    assert [item["id"] for item in items] == [parent["id"]]
    assert items[0]["subtasks"] == 1
    assert other.trash_items("bert") == other.trash_items("anna")  # no privacy
    restored = await other.async_restore_idea(parent["id"], "anna")
    assert restored is not None
    assert other.get_idea(child["id"])["parent_id"] == parent["id"]
    assert other.trash_items() == []


async def test_old_entries_expire(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test that what is older than the trash keeps is gone, an undated entry starts now."""
    old = (dt_util.now() - timedelta(days=TRASH_DAYS + 1)).isoformat()
    fresh = (dt_util.now() - timedelta(days=2)).isoformat()
    trash = [
        {"idea": {"id": "old1", "text": "Alt"}, "orphans": [], "user_id": None, "deleted_at": old},
        {"idea": {"id": "new1", "text": "Neu"}, "orphans": [], "user_id": None, "deleted_at": fresh},
        {"idea": {"id": "nodate", "text": "Ohne Datum"}, "orphans": [], "user_id": None},
    ]
    store = await _setup(setup_entry, trash=trash)
    assert {item["id"] for item in store.trash_items()} == {"new1", "nodate"}
    assert await store.async_purge_trash() == 0


async def test_websocket_list_restore_and_delete(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_ws_client: WebSocketGenerator
) -> None:
    """Test the commands the cards use."""
    store = await _setup(setup_entry)
    first = await store.async_add_idea("Lampe kaufen")
    second = await store.async_add_idea("Regal bauen")
    await store.async_delete_idea(first["id"])
    await store.async_delete_idea(second["id"])

    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "brainstorm/trash"})
    result = (await client.receive_json())["result"]
    assert result["days"] == TRASH_DAYS
    assert [item["text"] for item in result["items"]] == ["Regal bauen", "Lampe kaufen"]

    await client.send_json_auto_id({"type": "brainstorm/trash/restore", "ids": [first["id"]]})
    assert (await client.receive_json())["result"] == {"restored": [first["id"]]}
    assert store.get_idea(first["id"]) is not None

    await client.send_json_auto_id({"type": "brainstorm/trash/delete", "ids": [second["id"], "nope"]})
    assert (await client.receive_json())["result"] == {"deleted": 1}
    assert store.trash_items() == []
    assert store.deleted_idea(second["id"]) is None


async def test_privacy_keeps_the_trash_personal(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that only who deleted a private note, or may edit it, sees it in the trash."""
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]},
        options={"privacy_enabled": True},
    )
    store = entry.runtime_data
    idea = await store.async_add_idea("Geschenk für Bert", context=Context(user_id="anna"))
    await store.async_delete_idea(idea["id"], context=Context(user_id="anna"))
    assert [item["id"] for item in store.trash_items("anna")] == [idea["id"]]
    assert store.trash_items("bert") == []
    assert await store.async_purge_trash([idea["id"]], "bert") == 0
    assert await store.async_restore_idea(idea["id"], "bert") is None
