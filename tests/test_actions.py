"""Tests for the results and failures of actions and to-do lists."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from homeassistant.components.todo import TodoItem, TodoItemStatus
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.util import dt as dt_util

from custom_components.brainstorm.const import DOMAIN
from custom_components.brainstorm.todo import BrainstormTodoList, _due_from_item

from .conftest import SetupEntry


async def _call(hass: HomeAssistant, action: str, **data: Any) -> dict[str, Any]:
    """Call an action and return its response."""
    return await hass.services.async_call(
        DOMAIN, action, data, blocking=True, return_response=True
    )


async def test_add_idea_with_due_time_and_subtask(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the optional fields of adding an idea."""
    await setup_entry()
    due = dt_util.now().replace(microsecond=0) + timedelta(days=2)
    parent = (await _call(hass, "add_idea", text="Garage aufräumen"))["idea"]
    idea = (
        await _call(
            hass,
            "add_idea",
            text="Regal bauen",
            category="Projekte",
            priority="low",
            due=due.isoformat(),
            parent_id=parent["id"],
        )
    )["idea"]
    assert dt_util.parse_datetime(idea["due"]) == due
    assert idea["category"] == "Projekte"
    assert idea["priority"] == "low"
    assert idea["parent_id"] == parent["id"]


async def test_update_idea_changes_the_optional_fields(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test changing category, priority, order and parent of an idea."""
    await setup_entry()
    parent = (await _call(hass, "add_idea", text="Garage aufräumen"))["idea"]
    idea = (await _call(hass, "add_idea", text="Regal bauen"))["idea"]

    updated = (
        await _call(
            hass,
            "update_idea",
            id=idea["id"],
            category="Reisen",
            priority="low",
            order=7,
            parent_id=parent["id"],
        )
    )["idea"]
    assert updated["category"] == "Reisen"
    assert updated["priority"] == "low"
    assert updated["order"] == 7
    assert updated["parent_id"] == parent["id"]
    assert "Reisen" in (await _call(hass, "get_ideas"))["categories"]

    updated = (await _call(hass, "update_idea", id=idea["id"], parent_id=None))["idea"]
    assert updated["parent_id"] is None


async def test_update_idea_refuses_an_unknown_parent(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that an unknown parent is reported instead of being ignored."""
    await setup_entry()
    idea = (await _call(hass, "add_idea", text="Regal bauen"))["idea"]
    with pytest.raises(ServiceValidationError, match="gibtsnicht"):
        await _call(hass, "update_idea", id=idea["id"], parent_id="gibtsnicht")


async def test_reorder_ideas(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test saving an order, and that an unknown idea changes nothing."""
    entry = await setup_entry()
    first = (await _call(hass, "add_idea", text="Erste Notiz"))["idea"]["id"]
    second = (await _call(hass, "add_idea", text="Zweite Notiz"))["idea"]["id"]

    assert (await _call(hass, "reorder_ideas", idea_ids=[second, first]))["success"]
    store = entry.runtime_data
    assert store.get_idea(second)["order"] == 0
    assert store.get_idea(first)["order"] == 1

    with pytest.raises(ServiceValidationError, match="gibtsnicht"):
        await _call(hass, "reorder_ideas", idea_ids=[first, "gibtsnicht"])
    assert store.get_idea(first)["order"] == 1


async def test_delete_idea(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test deleting an idea, which frees its subtasks, and an unknown one."""
    entry = await setup_entry()
    parent = (await _call(hass, "add_idea", text="Garage aufräumen"))["idea"]["id"]
    child = (await _call(hass, "add_idea", text="Regal bauen", parent_id=parent))["idea"]

    assert (await _call(hass, "delete_idea", id=parent))["success"]
    assert entry.runtime_data.get_idea(parent) is None
    assert entry.runtime_data.get_idea(child["id"])["parent_id"] is None
    with pytest.raises(ServiceValidationError, match="gibtsnicht"):
        await _call(hass, "delete_idea", id="gibtsnicht")


async def test_get_ideas_with_all_statuses(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that the status all also returns completed ideas."""
    await setup_entry()
    idea = (await _call(hass, "add_idea", text="Regal bauen"))["idea"]
    await _call(hass, "update_idea", id=idea["id"], status="completed")
    assert (await _call(hass, "get_ideas"))["count"] == 0
    assert (await _call(hass, "get_ideas", status="all"))["count"] == 1


async def test_category_actions_report_failures(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test adding and removing categories, and everything that can go wrong."""
    entry = await setup_entry()
    result = await _call(hass, "add_category", name="Reisen", icon="mdi:car", color="#ff7800")
    assert "Reisen" in result["categories"]
    assert entry.runtime_data.category_icons["Reisen"] == "mdi:car"
    assert entry.runtime_data.category_colors["Reisen"] == "#ff7800"

    with pytest.raises(ServiceValidationError, match="existiert bereits"):
        await _call(hass, "add_category", name="reisen")
    with pytest.raises(ServiceValidationError, match="leer"):
        await _call(hass, "add_category", name="  ")

    result = await _call(hass, "remove_category", name="Reisen")
    assert "Reisen" not in result["categories"]
    for name in ("Reisen", "Inbox"):
        with pytest.raises(ServiceValidationError, match=name):
            await _call(hass, "remove_category", name=name)


async def test_set_category_style(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test the design of a category through the action."""
    await setup_entry()
    result = await _call(
        hass, "set_category_style", category="Alltag", icon="mdi:home", color="#06b6d4"
    )
    assert result["category_icons"]["Alltag"] == "mdi:home"
    assert result["category_colors"]["Alltag"] == "#06b6d4"

    result = await _call(hass, "set_category_style", category="Alltag", reset=True)
    assert "Alltag" not in result["category_icons"]
    with pytest.raises(ServiceValidationError, match="Kategoriename"):
        await _call(hass, "set_category_style", category=" ")
    with pytest.raises(ServiceValidationError):
        await _call(hass, "set_category_style", category="Alltag", color="rot")


async def test_export_markdown(
    hass: HomeAssistant, setup_entry: SetupEntry, tmp_path: Path
) -> None:
    """Test the written file with all kinds of origin and priority."""
    hass.config.config_dir = str(tmp_path)
    await setup_entry()
    for text, fields in (
        ("Erste Notiz", {"priority": "urgent", "source": "alexa", "device": "Echo"}),
        ("Zweite Notiz", {"priority": "high", "source": "alexa"}),
        ("Dritte Notiz", {"priority": "low", "source": "", "device": "Echo"}),
        ("Vierte Notiz", {"priority": "medium", "source": ""}),
    ):
        await _call(hass, "add_idea", text=text, category="Neues Thema", **fields)
    target = tmp_path / "export"
    assert (await _call(hass, "export_markdown", path=str(target)))["success"]

    lines = (target / "inbox.md").read_text("utf-8")
    assert "- [ ] Erste Notiz `[🔥 Dringend]` `[alexa (Echo)]`" in lines
    assert "- [ ] Zweite Notiz `[🔴 Hoch]` `[alexa]`" in lines
    assert "- [ ] Dritte Notiz `[🟢 Niedrig]` `[Echo]`" in lines
    assert "- [ ] Vierte Notiz _(" in lines


async def test_export_markdown_reports_file_errors(
    hass: HomeAssistant, setup_entry: SetupEntry, tmp_path: Path
) -> None:
    """Test that a full or broken disk is reported as a failed action."""
    hass.config.config_dir = str(tmp_path)
    await setup_entry()
    with (
        patch("custom_components.brainstorm.store.os.makedirs", side_effect=OSError("voll")),
        pytest.raises(HomeAssistantError, match="voll"),
    ):
        await _call(hass, "export_markdown", path=str(tmp_path / "export"))


async def test_share_reports_unknown_ideas(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_admin_user: Any
) -> None:
    """Test that sharing nothing at all is reported."""
    await setup_entry(
        options={"privacy_enabled": True, "privacy_owner": hass_admin_user.id}
    )
    with pytest.raises(ServiceValidationError, match="gefunden"):
        await _call(hass, "share", ids=["gibtsnicht"], shares={"all": "view"})


async def test_announcement_of_one_category_counts_its_ideas(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the text and number of an announcement about one category."""
    await setup_entry()
    await _call(hass, "add_idea", text="Milch kaufen", category="Alltag")
    await _call(hass, "add_idea", text="Beet umgraben", category="Haus & Garten")

    result = await _call(hass, "get_announcement", category="Alltag")
    assert result["count"] == 1
    assert "Milch kaufen" in result["speech"]
    result = await _call(hass, "get_announcement", category="Garten")
    assert "Haus und Garten" in result["speech"]
    result = await _call(hass, "get_announcement", category="Projekte")
    assert result["count"] == 0
    assert "keine offenen" in result["speech"]
    result = await _call(hass, "get_announcement")
    assert result["count"] == 2


async def test_unload_cleans_up_everything(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that nothing keeps running, not even after a reload."""
    baseline = hass.bus.async_listeners().get("mobile_app_notification_action", 0)
    entry = await setup_entry(options={"voice_mode": "skill"})
    webhook_id = entry.runtime_data.alexa_skill._webhook_id  # noqa: SLF001
    assert webhook_id in hass.data["webhook"]
    assert hass.bus.async_listeners()["mobile_app_notification_action"] == baseline + 1

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert hass.bus.async_listeners()["mobile_app_notification_action"] == baseline + 1

    store = entry.runtime_data
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert webhook_id not in hass.data["webhook"]
    assert not store._listeners  # noqa: SLF001
    assert hass.bus.async_listeners().get("mobile_app_notification_action", 0) == baseline


async def _todo_entity(hass: HomeAssistant, category: str) -> BrainstormTodoList:
    """Return the to-do list entity of a category."""
    return next(
        entity
        for entity in hass.data["entity_components"]["todo"].entities
        if entity.name.endswith(category)
    )


async def test_todo_list_describes_items_and_updates_them(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the description of an item and changing and deleting it."""
    entry = await setup_entry()
    store = entry.runtime_data
    low = await store.async_add_idea(
        "Regal bauen", category="Alltag", priority="low", source="", device="Echo"
    )
    entity = await _todo_entity(hass, "Alltag")

    item = next(i for i in entity.todo_items if i.uid == low["id"])
    assert item.description == "Priorität: 🟢 Niedrig • Gerät: Echo"

    due = dt_util.now().replace(microsecond=0) + timedelta(days=1)
    await entity.async_update_todo_item(
        TodoItem(uid=low["id"], summary="Regal", status=TodoItemStatus.COMPLETED, due=due)
    )
    assert store.get_idea(low["id"])["status"] == "completed"
    assert dt_util.parse_datetime(store.get_idea(low["id"])["due"]) == due

    await entity.async_delete_todo_items([low["id"]])
    assert store.get_idea(low["id"]) is None


async def test_todo_list_reports_unknown_items(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a change to an item that is gone fails visibly."""
    await setup_entry()
    entity = await _todo_entity(hass, "Alltag")
    item = TodoItem(uid="gibtsnicht", summary="x", status=TodoItemStatus.NEEDS_ACTION)
    with pytest.raises(ServiceValidationError, match="gibtsnicht"):
        await entity.async_update_todo_item(item)
    with pytest.raises(ServiceValidationError, match="gibtsnicht"):
        await entity.async_delete_todo_items(["gibtsnicht"])


async def test_todo_delete_refuses_other_owners(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_admin_user: Any
) -> None:
    """Test that only the owner can delete an item."""
    entry = await setup_entry(
        options={"privacy_enabled": True, "privacy_owner": hass_admin_user.id}
    )
    idea = await entry.runtime_data.async_add_idea(
        "Regal bauen", category="Alltag", owner=hass_admin_user.id
    )
    entity = await _todo_entity(hass, "Alltag")
    entity._context = None  # noqa: SLF001
    with patch.object(
        BrainstormTodoList, "_user_id", new_callable=lambda: property(lambda _: "fremd")
    ), pytest.raises(HomeAssistantError, match="Kein Zugriff"):
        await entity.async_delete_todo_items([idea["id"]])


def test_due_of_a_todo_item_keeps_a_time() -> None:
    """Test that a time from a to-do item stays what it was."""
    due = datetime(2026, 11, 2, 10, 30, tzinfo=dt_util.UTC)
    item = TodoItem(uid="1", summary="x", due=due)
    assert _due_from_item(item) == due
