"""Tests for the calendar events of tasks with a due time."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
import uuid

import pytest

from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEntityFeature,
    CalendarEvent,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockModule,
    MockPlatform,
    mock_integration,
    mock_platform,
)

from custom_components.brainstorm.calendar_sync import calendar_for, has_time
from custom_components.brainstorm.const import DOMAIN

from .conftest import SetupEntry


class FakeCalendar(CalendarEntity):
    """A calendar that keeps its events in memory."""

    def __init__(self, name: str, features: CalendarEntityFeature) -> None:
        self._attr_name = name
        self._attr_unique_id = name
        self._attr_supported_features = features
        self.events: list[CalendarEvent] = []

    @property
    def event(self) -> CalendarEvent | None:
        return self.events[0] if self.events else None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        return [e for e in self.events if e.start < end_date and e.end > start_date]

    async def async_create_event(self, **kwargs: Any) -> None:
        self.events.append(
            CalendarEvent(
                start=kwargs["dtstart"],
                end=kwargs["dtend"],
                summary=kwargs["summary"],
                description=kwargs.get("description"),
                uid=uuid.uuid4().hex,
            )
        )

    async def async_delete_event(
        self,
        uid: str,
        recurrence_id: str | None = None,
        recurrence_range: str | None = None,
    ) -> None:
        self.events = [e for e in self.events if e.uid != uid]

    async def async_update_event(
        self,
        uid: str,
        event: dict[str, Any],
        recurrence_id: str | None = None,
        recurrence_range: str | None = None,
    ) -> None:
        for index, item in enumerate(self.events):
            if item.uid == uid:
                self.events[index] = CalendarEvent(
                    start=event["dtstart"],
                    end=event["dtend"],
                    summary=event["summary"],
                    uid=uid,
                )


@pytest.fixture
async def calendars(hass: HomeAssistant) -> dict[str, FakeCalendar]:
    """A family calendar that can delete, and a work calendar that can also move."""
    family = FakeCalendar(
        "Familie",
        CalendarEntityFeature.CREATE_EVENT | CalendarEntityFeature.DELETE_EVENT,
    )
    work = FakeCalendar(
        "Arbeit",
        CalendarEntityFeature.CREATE_EVENT
        | CalendarEntityFeature.DELETE_EVENT
        | CalendarEntityFeature.UPDATE_EVENT,
    )

    async def setup_platform(
        hass: HomeAssistant, config: Any, add: AddEntitiesCallback, info: Any = None
    ) -> None:
        add([family, work])

    mock_integration(hass, MockModule("fakecal"))
    mock_platform(
        hass, "fakecal.calendar", MockPlatform(async_setup_platform=setup_platform)
    )
    assert await async_setup_component(
        hass, "calendar", {"calendar": [{"platform": "fakecal"}]}
    )
    await hass.async_block_till_done()
    assert hass.states.get("calendar.familie") is not None
    return {"familie": family, "arbeit": work}


OPTIONS = {
    "calendar_enabled": True,
    "calendar_entity": "calendar.familie",
    "calendar_categories": {"Arbeit": "calendar.arbeit"},
}


def _at(days: int, hour: int, minute: int = 0) -> datetime:
    day = dt_util.start_of_local_day() + timedelta(days=days)
    return day.replace(hour=hour, minute=minute)


def test_rules() -> None:
    """09:00 means no time, and a category may have its own calendar."""
    assert has_time(_at(1, 14, 30))
    assert not has_time(_at(1, 9))
    assert calendar_for(OPTIONS, "Arbeit") == "calendar.arbeit"
    assert calendar_for(OPTIONS, "Inbox") == "calendar.familie"
    assert calendar_for({}, "Inbox") is None


async def test_events_follow_the_tasks(
    hass: HomeAssistant, setup_entry: SetupEntry, calendars: dict[str, FakeCalendar]
) -> None:
    """Add, move, rename, tick off and delete a task with a time."""
    family = calendars["familie"]
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Arbeit"]}, options=OPTIONS
    )
    store = entry.runtime_data
    idea = await store.async_add_idea(
        "Zahnarzt", source="dashboard", verbatim=True, due=_at(1, 14, 30)
    )
    await hass.async_block_till_done()
    assert [(e.summary, e.start) for e in family.events] == [
        ("Zahnarzt", _at(1, 14, 30))
    ]
    assert store.get_overview_attributes()["calendar"] == {"entity": "calendar.familie"}
    details = {i["id"]: i for i in store.get_overview_attributes()["ideas"]}
    assert details[idea["id"]]["calendar_event"] == "calendar.familie"

    # Moving and renaming: Familie cannot change events, so it is replaced
    await store.async_update_idea(
        idea["id"], text="Zahnarzt Kontrolle", due=_at(2, 10), update_due=True
    )
    await hass.async_block_till_done()
    assert [(e.summary, e.start) for e in family.events] == [
        ("Zahnarzt Kontrolle", _at(2, 10))
    ]

    # Ticked off, the event stays as a record
    await store.async_update_idea(idea["id"], status="completed")
    await hass.async_block_till_done()
    assert len(family.events) == 1

    # Deleted, it goes
    await store.async_delete_idea(idea["id"])
    await hass.async_block_till_done()
    assert family.events == []


async def test_category_calendar_and_moving_in_place(
    hass: HomeAssistant, setup_entry: SetupEntry, calendars: dict[str, FakeCalendar]
) -> None:
    """A category's own calendar is used, and moved in place where it can."""
    work = calendars["arbeit"]
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Arbeit"]}, options=OPTIONS
    )
    store = entry.runtime_data
    idea = await store.async_add_idea(
        "Meeting", category="Arbeit", source="dashboard", verbatim=True, due=_at(1, 11)
    )
    await hass.async_block_till_done()
    uid = work.events[0].uid
    await store.async_update_idea(idea["id"], due=_at(1, 12), update_due=True)
    await hass.async_block_till_done()
    assert [(e.uid, e.start) for e in work.events] == [(uid, _at(1, 12))]
    assert calendars["familie"].events == []

    # Moved to another category, the event moves to its calendar
    await store.async_update_idea(idea["id"], category="Inbox")
    await hass.async_block_till_done()
    assert work.events == []
    assert [e.summary for e in calendars["familie"].events] == ["Meeting"]


async def test_switch_and_rule(
    hass: HomeAssistant, setup_entry: SetupEntry, calendars: dict[str, FakeCalendar]
) -> None:
    """Without a time only with 📅 on; off removes it; past tasks get nothing."""
    family = calendars["familie"]
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]}, options=OPTIONS
    )
    store = entry.runtime_data
    day = await store.async_add_idea(
        "Müll", source="dashboard", verbatim=True, due=_at(1, 9)
    )
    await store.async_add_idea(
        "Verpasst", source="dashboard", verbatim=True, due=_at(-1, 15)
    )
    await hass.async_block_till_done()
    assert family.events == []

    async def switch(value: bool | None) -> None:
        await hass.services.async_call(
            DOMAIN, "update_idea", {"id": day["id"], "calendar": value}, blocking=True
        )
        await hass.async_block_till_done()

    await switch(True)
    assert [e.summary for e in family.events] == ["Müll"]
    details = {i["id"]: i for i in store.get_overview_attributes()["ideas"]}
    assert details[day["id"]]["calendar"] is True
    await switch(False)
    assert family.events == []
    await switch(None)
    assert family.events == []


async def test_switched_off_and_old_entries(
    hass: HomeAssistant, setup_entry: SetupEntry, calendars: dict[str, FakeCalendar]
) -> None:
    """Switched off nothing happens; tasks added by older versions stay alone."""
    future = _at(1, 15).isoformat()
    entry = await setup_entry(
        stored={
            "ideas": [
                {
                    "id": "alt1",
                    "text": "Alt",
                    "category": "Inbox",
                    "status": "active",
                    "due": future,
                    "calendar_synced": True,
                },
                {
                    "id": "neu1",
                    "text": "Neu",
                    "category": "Inbox",
                    "status": "active",
                    "due": future,
                },
            ],
            "categories": ["Inbox"],
        },
        options=OPTIONS,
    )
    await hass.async_block_till_done()
    assert [e.summary for e in calendars["familie"].events] == ["Neu"]
    store = entry.runtime_data
    assert store.calendar_sync is not None and store.calendar_sync.enabled
    await hass.config_entries.async_unload(entry.entry_id)

    off = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]},
        options={"calendar_entity": "calendar.familie"},
    )
    await off.runtime_data.async_add_idea(
        "Termin", source="dashboard", verbatim=True, due=_at(1, 16)
    )
    await hass.async_block_till_done()
    assert len(calendars["familie"].events) == 1
    assert off.runtime_data.get_overview_attributes()["calendar"] is None


async def test_settings_page(
    hass: HomeAssistant, setup_entry: SetupEntry, calendars: dict[str, FakeCalendar]
) -> None:
    """The page sets the default calendar and one category's calendar."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox", "Arbeit"]})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "reminders"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "reminder_extras"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["description_placeholders"]["calendar_categories"] == "–"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "calendar_enabled": True,
            "calendar_entity": "calendar.familie",
            "calendar_category": "Arbeit",
            "calendar_category_entity": "calendar.arbeit",
            "native_reminders": False,
        },
    )
    assert result["type"] is FlowResultType.MENU
    await hass.async_block_till_done()
    assert entry.options["calendar_categories"] == {"Arbeit": "calendar.arbeit"}
    assert "calendar_category" not in entry.options
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "reminder_extras"}
    )
    assert (
        result["description_placeholders"]["calendar_categories"]
        == "Arbeit → calendar.arbeit"
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "calendar_enabled": True,
            "calendar_entity": "calendar.familie",
            "calendar_category": "Arbeit",
            "native_reminders": False,
        },
    )
    await hass.async_block_till_done()
    assert entry.options["calendar_categories"] == {}
    hass.config_entries.options.async_abort(result["flow_id"])
