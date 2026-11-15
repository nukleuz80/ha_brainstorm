"""Tests for the tasks on the eve of a waste pickup."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import pytest

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.brainstorm.languages import get_pack
from custom_components.brainstorm.waste import WasteWatcher, waste_icon, waste_name

from .conftest import SetupEntry

CALENDAR = "calendar.abfall"
DAY = date(2026, 11, 16)


@pytest.fixture
def pickups(hass: HomeAssistant) -> dict[str, str]:
    """A calendar of Waste Collection Schedule, its entries by ISO date."""
    entry = er.async_get(hass).async_get_or_create(
        "calendar", "waste_collection_schedule", "abfall", suggested_object_id="abfall"
    )
    assert entry.entity_id == CALENDAR
    hass.states.async_set(CALENDAR, "off", {"friendly_name": "Abfall"})
    days: dict[str, str] = {}

    async def get_events(call: ServiceCall) -> dict[str, Any]:
        start = dt_util.parse_datetime(call.data["start_date_time"])
        end = dt_util.parse_datetime(call.data["end_date_time"])
        assert start is not None and end is not None
        events = [
            {"start": iso, "end": iso, "summary": summary}
            for iso, summary in days.items()
            if start.date() <= date.fromisoformat(iso) < end.date()
        ]
        entities = call.data["entity_id"]
        if isinstance(entities, str):
            entities = [entities]
        assert "calendar.kaputt" not in entities
        return {entity: {"events": events} for entity in entities}

    hass.services.async_register(
        "calendar", "get_events", get_events, supports_response=SupportsResponse.ONLY
    )
    return days


def _choreops(hass: HomeAssistant, *names: str) -> list[dict[str, Any]]:
    """ChoreOps with its people, returning the chores it was given."""
    for name in names:
        entry = er.async_get(hass).async_get_or_create(
            "sensor", "choreops", f"entry1_{name.lower()}_points"
        )
        hass.states.async_set(
            entry.entity_id, "0", {"user_name": name, "purpose": "purpose_points"}
        )
    calls: list[dict[str, Any]] = []

    async def create(call: ServiceCall) -> dict[str, Any]:
        calls.append(dict(call.data))
        return {"id": f"c{len(calls)}"}

    hass.services.async_register(
        "choreops", "create_chore", create, supports_response=SupportsResponse.OPTIONAL
    )
    return calls


def _tasks(store: Any) -> list[dict[str, Any]]:
    return sorted(
        (i for i in store.ideas if i.get("waste")),
        key=lambda i: (i["waste"]["date"], i["text"]),
    )


def test_names_and_signs() -> None:
    """The waste type comes without "Pickup" and remarks, with its sign."""
    de = get_pack("de")
    name = waste_name("Abfuhr Restabfall (14tägige und vierwöchentliche Abfuhr", de)
    assert name == "Restabfall"
    assert waste_icon(name, de) == "⚫"
    assert waste_name("Abfuhr Gelbe Tonne", de) == "Gelbe Tonne"
    assert waste_icon("Gelbe Tonne", de) == "🟡"
    assert waste_icon("Bioabfall", de) == "🟤"
    assert waste_icon("Altpapier", de) == "🔵"
    assert waste_name("Abfuhr", de) == "Abfuhr"
    assert waste_icon("Sondermüll", de) == "🗑️"
    en = get_pack("en")
    assert waste_name("Collection: Recycling", en) == "Recycling"
    assert waste_icon("Recycling", en) == "🟡"


async def test_tasks_on_the_eve(
    hass: HomeAssistant, setup_entry: SetupEntry, pickups: dict[str, str]
) -> None:
    """Every pickup of a day becomes one task, only once, and closes afterwards."""
    pickups[DAY.isoformat()] = "Abfuhr Altpapier, Abfuhr Bioabfall"
    pickups["2026-11-23"] = "Abfuhr Gelbe Tonne"
    # An unavailable calendar is left out and costs nothing
    hass.states.async_set("calendar.kaputt", "unavailable")
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox", "Haushalt"]})
    store = entry.runtime_data
    watcher = WasteWatcher(
        hass,
        store,
        {
            "waste_enabled": True,
            "waste_calendars": ["calendar.kaputt", CALENDAR],
            "waste_category": "Haushalt",
            "waste_time": "19:30:00",
        },
    )
    assert await watcher.async_create_for(DAY) == 2
    assert await watcher.async_create_for(DAY) == 0
    tasks = _tasks(store)
    assert [t["text"] for t in tasks] == [
        "🔵 Altpapier rausstellen",
        "🟤 Bioabfall rausstellen",
    ]
    first = tasks[0]
    assert first["category"] == "Haushalt"
    assert first["source"] == "waste"
    assert first["device"] == "Abfall"
    assert first["waste"] == {"date": "2026-11-16", "key": "altpapier"}
    assert first["description"] == "Laut Abfall: Abfuhr Altpapier, Abfuhr Bioabfall"
    due = dt_util.as_local(dt_util.parse_datetime(first["due"]))
    assert (due.date(), due.hour, due.minute) == (date(2026, 11, 15), 19, 30)

    # Ticked off by hand, the task is not added again
    await store.async_update_idea(first["id"], status="completed")
    assert await watcher.async_create_for(DAY) == 0

    # The day after the pickup, the open task closes itself
    assert await watcher.async_close_past(DAY) == 0
    assert await watcher.async_close_past(DAY + timedelta(days=1)) == 2
    statuses = {t["text"]: (t["status"], t.get("waste_done")) for t in _tasks(store)}
    assert statuses == {
        "🔵 Altpapier rausstellen": ("completed", True),
        "🟤 Bioabfall rausstellen": ("completed", True),
    }
    assert await watcher.async_close_past(DAY + timedelta(days=2)) == 0


async def test_catch_up_after_the_time(
    hass: HomeAssistant, setup_entry: SetupEntry, pickups: dict[str, str]
) -> None:
    """After a restart, tomorrow's tasks come only once the time has passed."""
    pickups[DAY.isoformat()] = "Abfuhr Gelbe Tonne"
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    store = entry.runtime_data
    watcher = WasteWatcher(hass, store, {"waste_enabled": True})
    eve = dt_util.start_of_local_day(DAY - timedelta(days=1))
    await watcher.async_catch_up(eve + timedelta(hours=17, minutes=59))
    assert _tasks(store) == []
    await watcher.async_catch_up(eve + timedelta(hours=18))
    assert [t["text"] for t in _tasks(store)] == ["🟡 Gelbe Tonne rausstellen"]
    assert _tasks(store)[0]["category"] == "Inbox"

    # Switched off, nothing new is added
    off = WasteWatcher(hass, store, {"waste_enabled": False})
    pickups["2026-11-17"] = "Abfuhr Bioabfall"
    await off.async_catch_up(eve + timedelta(days=1, hours=20))
    assert len(_tasks(store)) == 1


async def test_choreops_in_turn(
    hass: HomeAssistant, setup_entry: SetupEntry, pickups: dict[str, str]
) -> None:
    """The tasks of a pickup day go to one person, the next day to the next one."""
    calls = _choreops(hass, "Lenja", "Jonathan")
    pickups[DAY.isoformat()] = "Abfuhr Altpapier, Abfuhr Bioabfall"
    pickups["2026-11-23"] = "Abfuhr Restabfall"
    pickups["2026-11-30"] = "Abfuhr Gelbe Tonne"
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    store = entry.runtime_data
    watcher = WasteWatcher(
        hass,
        store,
        {
            "waste_enabled": True,
            "waste_choreops_users": ["Lenja", "Jonathan"],
            "waste_choreops_points": 5,
        },
    )
    for day in ("2026-11-16", "2026-11-23", "2026-11-30"):
        await watcher.async_create_for(date.fromisoformat(day))
    await hass.async_block_till_done()
    users = [(t["waste"]["date"], t["waste"]["user"]) for t in _tasks(store)]
    assert users == [
        ("2026-11-16", "Lenja"),
        ("2026-11-16", "Lenja"),
        ("2026-11-23", "Jonathan"),
        ("2026-11-30", "Lenja"),
    ]
    assert [c["assigned_user_names"] for c in calls] == [
        ["Lenja"],
        ["Lenja"],
        ["Jonathan"],
        ["Lenja"],
    ]
    assert {c["points"] for c in calls} == {5}


async def test_settings_page(
    hass: HomeAssistant, setup_entry: SetupEntry, pickups: dict[str, str]
) -> None:
    """The page is offered with Waste Collection Schedule and saves its fields."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox", "Haushalt"]})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert (
        "⚪ Abfallkalender" in result["description_placeholders"]["integrations_status"]
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "integrations"}
    )
    assert "waste_collection_schedule" in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "waste_collection_schedule"}
    )
    assert result["type"] is FlowResultType.FORM
    fields = {str(key): key for key in result["data_schema"].schema}
    assert "waste_choreops_users" not in fields
    assert fields["waste_calendars"].default() == [CALENDAR]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "waste_enabled": True,
            "waste_calendars": [CALENDAR],
            "waste_category": "Haushalt",
            "waste_time": "19:00:00",
        },
    )
    assert result["step_id"] == "integrations"
    assert result["description_placeholders"]["status_waste"] == "an · 19:00"
    assert entry.options["waste_enabled"] is True
    assert entry.options["waste_category"] == "Haushalt"
    hass.config_entries.options.async_abort(result["flow_id"])


async def test_watcher_runs_with_the_entry(
    hass: HomeAssistant, setup_entry: SetupEntry, pickups: dict[str, str]
) -> None:
    """Set up with the entry, the eve check adds tomorrow's tasks at the time."""
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    today = dt_util.now().date()
    pickups[(today + timedelta(days=1)).isoformat()] = "Abfuhr Bioabfall"
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]},
        options={"waste_enabled": True, "waste_time": "23:59:58"},
    )
    moment: datetime = dt_util.start_of_local_day(today) + timedelta(
        hours=23, minutes=59, seconds=58
    )
    async_fire_time_changed(hass, moment)
    await hass.async_block_till_done()
    assert [t["text"] for t in _tasks(entry.runtime_data)] == [
        "🟤 Bioabfall rausstellen"
    ]
