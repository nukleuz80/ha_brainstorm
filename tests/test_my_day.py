"""Tests for notes picked for today in "My day"."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pytest
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.brainstorm.store import my_day_part

from .conftest import SetupEntry


async def _call(hass: HomeAssistant, **data: Any) -> None:
    await hass.services.async_call("brainstorm", "update_idea", data, blocking=True)


def _listed(store: Any, idea_id: str) -> dict[str, Any]:
    return next(i for i in store.get_overview_attributes()["ideas"] if i["id"] == idea_id)


async def test_pick_list_and_take_out(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """A part of the day is kept with today's date, the cards see it."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Steuer machen", category="Inbox")
    await _call(hass, id=idea["id"], my_day="evening")
    assert store.get_idea(idea["id"])["my_day"] == {
        "date": dt_util.now().date().isoformat(),
        "part": "evening",
    }
    assert _listed(store, idea["id"])["my_day"] == "evening"
    with pytest.raises(vol.Invalid):
        await _call(hass, id=idea["id"], my_day="night")
    await _call(hass, id=idea["id"], my_day=None)
    assert "my_day" not in store.get_idea(idea["id"])
    assert "my_day" not in _listed(store, idea["id"])


def test_only_today_counts() -> None:
    """A pick of yesterday has run out, broken data counts as nothing."""
    today = date(2026, 11, 14)
    assert my_day_part({"my_day": {"date": "2026-11-14", "part": "morning"}}, today) == "morning"
    assert my_day_part({"my_day": {"date": "2026-11-13", "part": "morning"}}, today) is None
    assert my_day_part({"my_day": {"date": "2026-11-14", "part": "noon"}}, today) is None
    assert my_day_part({"my_day": "morning"}, today) is None
    assert my_day_part({}, today) is None


async def test_yesterdays_pick_is_not_listed(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """The cards no longer see a note picked on an earlier day."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Fenster putzen", category="Inbox")
    yesterday = (dt_util.now().date() - timedelta(days=1)).isoformat()
    await store.async_set_fields({idea["id"]: {"my_day": {"date": yesterday, "part": "day"}}})
    assert "my_day" not in _listed(store, idea["id"])


async def test_briefing_names_the_plan_by_part_of_day(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """The briefing says what was picked, by morning and evening, then what is due."""
    entry = await setup_entry()
    store = entry.runtime_data
    reminders = store.reminders
    now = dt_util.now()
    for text, part in (("Joggen", "morning"), ("Steuer", "evening"), ("Bad putzen", "morning")):
        idea = await store.async_add_idea(text, category="Inbox")
        await store.async_update_idea(idea["id"], my_day=part, update_my_day=True)
    # Picked and due: only named in the plan
    planned_due = await store.async_add_idea("Arzt anrufen", category="Inbox", due=now - timedelta(minutes=5))
    await store.async_update_idea(planned_due["id"], my_day="day", update_my_day=True)
    await store.async_add_idea("Müll raus", category="Inbox", due=now - timedelta(minutes=1))
    done = await store.async_add_idea("Erledigt", category="Inbox")
    await store.async_update_idea(done["id"], my_day="day", update_my_day=True, status="completed")

    digest = reminders.build_digest(now)
    assert digest.startswith("Für heute vorgenommen: morgens ")
    assert "Joggen" in digest and "Bad putzen" in digest
    assert "; tagsüber Arzt anrufen; abends Steuer." in digest
    assert digest.endswith("Heute steht an: Müll raus.")
    assert digest.count("Arzt anrufen") == 1
    assert "Erledigt" not in digest
