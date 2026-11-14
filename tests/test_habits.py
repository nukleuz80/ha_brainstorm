"""Tests for habits that are ticked off once a day and keep a streak."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pytest

from homeassistant.components.todo import TodoItem, TodoItemStatus
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util

from custom_components.brainstorm.store import BrainstormStore, habit_summary

from .conftest import SetupEntry


async def _call(hass: HomeAssistant, **data: Any) -> None:
    await hass.services.async_call("brainstorm", "update_idea", data, blocking=True)


def _listed(store: BrainstormStore, idea_id: str) -> dict[str, Any]:
    return next(i for i in store.get_overview_attributes()["ideas"] if i["id"] == idea_id)


def _days_ago(*offsets: int) -> list[str]:
    today = dt_util.now().date()
    return [(today - timedelta(days=offset)).isoformat() for offset in offsets]


async def test_ticking_off_counts_the_day_and_stays(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A habit stays active, ticking it off marks today, reopening takes it back."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Zähne putzen", category="Inbox")
    await _call(hass, id=idea["id"], habit=True)
    assert _listed(store, idea["id"])["habit"] == {
        "today": False, "streak": 0, "best": 0, "total": 0, "days": []
    }

    await _call(hass, id=idea["id"], status="completed")
    assert store.get_idea(idea["id"])["status"] == "active"
    habit = _listed(store, idea["id"])["habit"]
    assert habit["today"] is True
    assert habit["streak"] == 1
    assert habit["days"] == _days_ago(0)

    await _call(hass, id=idea["id"], status="active")
    assert _listed(store, idea["id"])["habit"]["today"] is False

    # Turned off, it is an ordinary note again that can be done
    await _call(hass, id=idea["id"], habit=False)
    await _call(hass, id=idea["id"], status="completed")
    assert store.get_idea(idea["id"])["status"] == "completed"
    assert "habit" not in store.get_idea(idea["id"])


async def test_earlier_days_can_be_marked(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A day before can be marked or unmarked, not a future one."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Lesen", category="Inbox")
    await _call(hass, id=idea["id"], habit=True)
    for day in _days_ago(1, 2, 3):
        await _call(hass, id=idea["id"], habit_done=True, habit_date=day)
    habit = _listed(store, idea["id"])["habit"]
    # Not ticked off yet today, the streak from yesterday still counts
    assert habit["streak"] == 3
    await _call(hass, id=idea["id"], habit_done=False, habit_date=_days_ago(2)[0])
    assert _listed(store, idea["id"])["habit"]["streak"] == 1
    tomorrow = (dt_util.now().date() + timedelta(days=1)).isoformat()
    with pytest.raises(ServiceValidationError):
        await _call(hass, id=idea["id"], habit_done=True, habit_date=tomorrow)


def test_streaks() -> None:
    """The streak runs back from today or yesterday, the best one anywhere."""
    today = date(2026, 11, 14)
    days = ["2026-11-01", "2026-11-02", "2026-11-03", "2026-11-04", "2026-11-12", "2026-11-13"]
    summary = habit_summary({"habit": {"days": days}}, today)
    assert summary["streak"] == 2
    assert summary["best"] == 4
    assert summary["total"] == 6
    assert summary["today"] is False
    # Two days missed ends the streak
    assert habit_summary({"habit": {"days": days[:4]}}, today)["streak"] == 0
    assert habit_summary({"habit": {"days": ["kaputt", "2026-11-14"]}}, today)["streak"] == 1
    assert habit_summary({}, today) is None


async def test_todo_list_and_briefing(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """The to-do list ticks off today, the briefing names open habits."""
    entry = await setup_entry()
    store = entry.runtime_data
    habit = await store.async_add_idea("Gießen", category="Alltag")
    other = await store.async_add_idea("Joggen", category="Alltag")
    for idea in (habit, other):
        await store.async_update_idea(idea["id"], habit=True)
    entity = next(
        e for e in hass.data["entity_components"]["todo"].entities if e.name.endswith("Alltag")
    )
    await entity.async_update_todo_item(
        TodoItem(uid=habit["id"], summary="Gießen", status=TodoItemStatus.COMPLETED)
    )
    assert store.get_idea(habit["id"])["status"] == "active"
    item = next(i for i in entity.todo_items if i.uid == habit["id"])
    assert item.status == TodoItemStatus.COMPLETED

    assert store.reminders.build_digest(dt_util.now()) == "Gewohnheiten für heute: Joggen."


async def test_new_day_tells_the_listeners(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """At midnight the cards and lists hear of the new day."""
    entry = await setup_entry()
    store = entry.runtime_data
    calls: list[Any] = []
    store.register_listener(lambda *args: calls.append(args))
    store.async_new_day()
    assert calls


async def test_websocket_returns_the_habit(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_ws_client: Any
) -> None:
    """The calendar asks for the streak of one habit."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Lesen", category="Inbox")
    plain = await store.async_add_idea("Regal", category="Inbox")
    await store.async_update_idea(idea["id"], habit=True, habit_done=True)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "brainstorm/habit", "idea_id": idea["id"]})
    result = await client.receive_json()
    assert result["result"]["streak"] == 1
    await client.send_json_auto_id({"type": "brainstorm/habit", "idea_id": plain["id"]})
    assert (await client.receive_json())["success"] is False


async def test_turning_off_keeps_the_days(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Turned off and on again, for example by undo, the streak comes back."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Laufen", category="Inbox")
    await _call(hass, id=idea["id"], habit=True)
    for day in _days_ago(0, 1):
        await _call(hass, id=idea["id"], habit_done=True, habit_date=day)
    await _call(hass, id=idea["id"], habit=False)
    assert "habit" not in _listed(store, idea["id"])
    await _call(hass, id=idea["id"], habit=True)
    assert _listed(store, idea["id"])["habit"]["streak"] == 2
