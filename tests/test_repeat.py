"""Tests for repeating ideas that come back after they are ticked off."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import pytest
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.brainstorm.store import next_repeat_due

from .conftest import SetupEntry

TZ = ZoneInfo("Europe/Berlin")


def _at(*args: int) -> datetime:
    return datetime(*args, tzinfo=TZ)


async def _call(hass: HomeAssistant, service: str, **data: Any) -> None:
    await hass.services.async_call("brainstorm", service, data, blocking=True)


@pytest.mark.parametrize(
    ("rule", "due", "now", "expected"),
    [
        ("daily", _at(2026, 11, 9, 8, 0), _at(2026, 11, 9, 7, 0), _at(2026, 11, 10, 8, 0)),
        ("weekly", _at(2026, 11, 9, 8, 0), _at(2026, 11, 9, 7, 0), _at(2026, 11, 16, 8, 0)),
        ("biweekly", _at(2026, 11, 9, 8, 0), _at(2026, 11, 9, 7, 0), _at(2026, 11, 23, 8, 0)),
        # Friday goes to Monday
        ("weekdays", _at(2026, 11, 13, 8, 0), _at(2026, 11, 13, 7, 0), _at(2026, 11, 16, 8, 0)),
        # The 31st falls on the last day of a shorter month and comes back after
        ("monthly", _at(2027, 1, 31, 9, 0), _at(2027, 1, 30, 9, 0), _at(2027, 2, 28, 9, 0)),
        ("monthly", _at(2027, 1, 31, 9, 0), _at(2027, 3, 1, 9, 0), _at(2027, 3, 31, 9, 0)),
        ("yearly", _at(2028, 2, 29, 9, 0), _at(2028, 2, 1, 9, 0), _at(2029, 2, 28, 9, 0)),
        # Ticked off late, it jumps over the rounds that passed
        ("weekly", _at(2026, 10, 1, 18, 0), _at(2026, 10, 20, 12, 0), _at(2026, 10, 22, 18, 0)),
        # Over the change of the clocks the time of day stays
        ("daily", _at(2026, 10, 24, 9, 0), _at(2026, 10, 24, 8, 0), _at(2026, 10, 25, 9, 0)),
    ],
)
def test_next_due(rule: str, due: datetime, now: datetime, expected: datetime) -> None:
    """Every rule finds the next date after now."""
    assert next_repeat_due(due, rule, now) == expected


def test_next_due_without_date() -> None:
    """Without a due date the next round is at 09:00."""
    now = _at(2026, 11, 9, 15, 30)
    assert next_repeat_due(None, "daily", now) == _at(2026, 11, 10, 9, 0)


async def test_repeat_is_set_listed_and_cleared(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Only known rules are taken, the cards see the rule, empty removes it."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Müll rausbringen", category="Inbox")
    await _call(hass, "update_idea", id=idea["id"], repeat="weekly")
    assert store.get_idea(idea["id"])["repeat"] == "weekly"
    listed = next(i for i in store.get_overview_attributes()["ideas"] if i["id"] == idea["id"])
    assert listed["repeat"] == "weekly"
    with pytest.raises(vol.Invalid):
        await _call(hass, "update_idea", id=idea["id"], repeat="hourly")
    await _call(hass, "update_idea", id=idea["id"], repeat="")
    assert "repeat" not in store.get_idea(idea["id"])


async def test_ticking_off_adds_the_next_round(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """The done idea stays done, a new one with its details and subtasks comes."""
    entry = await setup_entry()
    store = entry.runtime_data
    due = dt_util.now().replace(microsecond=0) + timedelta(hours=2)
    root = await store.async_add_idea(
        "Wochenputz", category="Inbox", priority="high", due=due, description="Alles"
    )
    sub_done = await store.async_add_idea("Bad", parent_id=root["id"], category="Inbox")
    sub_open = await store.async_add_idea("Küche", parent_id=root["id"], category="Inbox")
    await store.async_update_idea(root["id"], markers=["star"], update_markers=True, repeat="weekly", update_repeat=True)
    await store.async_update_idea(sub_done["id"], status="completed")

    await store.async_update_idea(root["id"], status="completed")

    old = store.get_idea(root["id"])
    assert old["status"] == "completed"
    assert "repeat" not in old
    new = store.get_idea(old["repeated_as"])
    assert new["status"] == "active"
    assert new["text"] == "Wochenputz"
    assert new["priority"] == "high"
    assert new["description"] == "Alles"
    assert new["markers"] == ["star"]
    assert new["repeat"] == "weekly"
    assert dt_util.parse_datetime(new["due"]) == due + timedelta(weeks=1)
    children = [i for i in store.ideas if i.get("parent_id") == new["id"]]
    assert sorted(c["text"] for c in children) == ["Bad", "Küche"]
    assert all(c["status"] == "active" for c in children)
    # The open subtask of the old round ended with it
    assert store.get_idea(sub_open["id"])["status"] == "completed"


async def test_reopening_takes_the_next_round_back(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Reopening the done idea removes the new round and keeps the rule."""
    entry = await setup_entry()
    store = entry.runtime_data
    root = await store.async_add_idea("Blumen gießen", category="Inbox")
    sub = await store.async_add_idea("Balkon", parent_id=root["id"], category="Inbox")
    await store.async_update_idea(root["id"], repeat="daily", update_repeat=True)
    await store.async_update_idea(root["id"], status="completed")
    new_id = store.get_idea(root["id"])["repeated_as"]
    count = len(store.ideas)

    await store.async_update_idea(root["id"], status="active")

    assert store.get_idea(new_id) is None
    assert len(store.ideas) == count - 2
    reopened = store.get_idea(root["id"])
    assert reopened["repeat"] == "daily"
    assert "repeated_as" not in reopened
    assert store.get_idea(sub["id"])["status"] == "active"


async def test_a_new_round_that_was_done_stays(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """When the new round is done already, reopening the old one leaves it."""
    entry = await setup_entry()
    store = entry.runtime_data
    root = await store.async_add_idea("Zeitung", category="Inbox")
    await store.async_update_idea(root["id"], repeat="daily", update_repeat=True)
    await store.async_update_idea(root["id"], status="completed")
    new_id = store.get_idea(root["id"])["repeated_as"]
    await store.async_update_idea(new_id, status="completed")

    await store.async_update_idea(root["id"], status="active")

    assert store.get_idea(new_id) is not None
    assert "repeat" not in store.get_idea(root["id"])
