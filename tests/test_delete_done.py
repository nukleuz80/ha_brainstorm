"""Tests for deleting ideas that are done."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import Context, Event, HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.brainstorm.const import EVENT_IDEA_DELETED

from .conftest import SetupEntry


def _idea(idea_id: str, status: str, days_ago: int, **extra: Any) -> dict[str, Any]:
    done = (dt_util.now() - timedelta(days=days_ago)).isoformat()
    idea = {
        "id": idea_id,
        "text": f"Eintrag {idea_id}",
        "category": "Inbox",
        "priority": "medium",
        "status": status,
        "created_at": done,
        "updated_at": done,
        "parent_id": None,
        **extra,
    }
    if status != "active":
        idea["completed_at"] = done
    return idea


STORED = {
    "categories": ["Inbox"],
    "ideas": [
        _idea("offen", "active", 90),
        _idea("alt", "completed", 40),
        _idea("archiv", "archived", 31),
        _idea("frisch", "completed", 3),
        _idea("kind", "active", 40, parent_id="alt"),
    ],
}


async def _delete_done(hass: HomeAssistant, **data: Any) -> dict[str, Any]:
    return await hass.services.async_call(
        "brainstorm", "delete_done", data, blocking=True, return_response=True
    )


async def test_delete_done_long_enough(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test that only ideas done for long enough go, in one go."""
    entry = await setup_entry(stored=STORED)
    store = entry.runtime_data
    events: list[Event] = []
    hass.bus.async_listen(EVENT_IDEA_DELETED, events.append)

    assert await _delete_done(hass, older_than_days=30) == {"deleted": 2}
    await hass.async_block_till_done()
    assert store.get_idea("alt") is None
    assert store.get_idea("archiv") is None
    assert store.get_idea("frisch") is not None
    assert store.get_idea("offen") is not None
    # The open subtask stays, as a main task
    assert store.get_idea("kind")["parent_id"] is None
    assert sorted(e.data["id"] for e in events) == ["alt", "archiv"]

    # Without days everything done goes
    assert await _delete_done(hass) == {"deleted": 1}
    assert store.get_idea("frisch") is None
    assert store.get_idea("offen") is not None
    assert await _delete_done(hass) == {"deleted": 0}


async def test_setting_deletes_by_itself(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test that the setting deletes done ideas and 0 keeps them."""
    entry = await setup_entry(stored=STORED)
    store = entry.runtime_data
    assert await store.async_delete_done_by_setting() == 0
    assert store.get_idea("alt") is not None

    store.options["delete_done_days"] = 35
    assert await store.async_delete_done_by_setting() == 1
    assert store.get_idea("alt") is None
    assert store.get_idea("archiv") is not None


async def _open_cleanup(hass: HomeAssistant, entry: Any) -> dict[str, Any]:
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "cleanup"}
    )
    assert result["step_id"] == "cleanup"
    return result


async def test_settings_delete_now_and_after_days(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the settings page: days are saved and act at once, the switch deletes all."""
    entry = await setup_entry(stored=STORED)
    result = await _open_cleanup(hass, entry)
    assert result["description_placeholders"]["done"] == "3"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"delete_done_days": 30, "delete_now": False}
    )
    await hass.async_block_till_done()
    assert result["step_id"] == "init"
    assert "2" in result["description_placeholders"]["notice"]
    assert entry.options["delete_done_days"] == 30
    store = entry.runtime_data
    assert store.get_idea("frisch") is not None
    assert store.get_idea("alt") is None

    result = await _open_cleanup(hass, entry)
    assert result["description_placeholders"]["done"] == "1"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"delete_done_days": 30, "delete_now": True}
    )
    await hass.async_block_till_done()
    assert "1" in result["description_placeholders"]["notice"]
    store = entry.runtime_data
    assert store.get_idea("frisch") is None
    assert store.get_idea("offen") is not None
    assert entry.options["delete_done_days"] == 30


async def test_others_keep_their_done_ideas(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that with privacy on a user only deletes their own done ideas."""
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]},
        options={"privacy_enabled": True, "privacy_owner": "user-jan"},
    )
    store = entry.runtime_data
    mine = await store.async_add_idea("von jan", context=Context(user_id="user-jan"))
    theirs = await store.async_add_idea("von lenja", context=Context(user_id="user-lenja"))
    for idea in (mine, theirs):
        await store.async_update_idea(idea["id"], status="completed")

    response = await hass.services.async_call(
        "brainstorm",
        "delete_done",
        {},
        blocking=True,
        return_response=True,
        context=Context(user_id="user-lenja"),
    )
    assert response == {"deleted": 1}
    assert store.get_idea(theirs["id"]) is None
    assert store.get_idea(mine["id"]) is not None
