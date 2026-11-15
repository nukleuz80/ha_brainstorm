"""Keep calendar events for the tasks with a due time.

A task with a due time gets an event in the chosen calendar, or in the one
chosen for its category. Changing the text or the time moves the event,
deleting the task removes it, and ticking it off leaves it in place. A due
time of 09:00 is how Brainstorm stores a day without a time, so such tasks
only get an event when their own 📅 switch is on.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, time, timedelta
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.calendar import CalendarEntity, CalendarEntityFeature
from homeassistant.components.calendar.const import DATA_COMPONENT
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CALLBACK_TYPE, CoreState, Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_CALENDAR,
    ATTR_CALENDAR_EVENT,
    ATTR_CALENDAR_SYNCED,
    ATTR_CATEGORY,
    ATTR_DESCRIPTION,
    ATTR_DUE,
    ATTR_ID,
    ATTR_STATUS,
    ATTR_TEXT,
    CONF_CALENDAR_CATEGORIES,
    CONF_CALENDAR_ENABLED,
    CONF_CALENDAR_ENTITY,
    EVENT_IDEA_ADDED,
    EVENT_IDEA_DELETED,
    EVENT_IDEA_UPDATED,
)

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

EVENT_LENGTH = timedelta(minutes=30)
# The time Brainstorm gives a due date without a time of its own
NO_TIME = time(9, 0)


def calendar_for(options: dict[str, Any], category: str | None) -> str | None:
    """Return the calendar of a category, or the default one."""
    chosen = options.get(CONF_CALENDAR_CATEGORIES) or {}
    if category and isinstance(chosen, dict) and chosen.get(category):
        return str(chosen[category])
    return options.get(CONF_CALENDAR_ENTITY) or None


def has_time(due: datetime) -> bool:
    """Tell whether a due date has a time of its own."""
    local = dt_util.as_local(due)
    return (local.hour, local.minute, local.second) != (
        NO_TIME.hour,
        NO_TIME.minute,
        0,
    )


class CalendarSync:
    """Add, move and remove the calendar events of tasks."""

    def __init__(
        self, hass: HomeAssistant, store: BrainstormStore, options: dict[str, Any]
    ) -> None:
        """Remember the settings."""
        self.hass = hass
        self.store = store
        self.options = options
        self.enabled = bool(options.get(CONF_CALENDAR_ENABLED)) and bool(
            options.get(CONF_CALENDAR_ENTITY) or options.get(CONF_CALENDAR_CATEGORIES)
        )
        self._lock = asyncio.Lock()
        self._unsubs: list[CALLBACK_TYPE] = []
        self._unsub_started: CALLBACK_TYPE | None = None

    async def async_start(self) -> None:
        """Follow the changes of tasks, and catch up once HA runs."""
        if not self.enabled:
            return
        for event_type in (EVENT_IDEA_ADDED, EVENT_IDEA_UPDATED):
            self._unsubs.append(
                self.hass.bus.async_listen(event_type, self._handle_changed)
            )
        self._unsubs.append(
            self.hass.bus.async_listen(EVENT_IDEA_DELETED, self._handle_deleted)
        )
        if self.hass.state is CoreState.running:
            self.hass.async_create_task(self.async_sync_all())
        else:
            self._unsub_started = self.hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED, self._handle_started
            )

    @callback
    def async_stop(self) -> None:
        """Stop following the tasks."""
        while self._unsubs:
            self._unsubs.pop()()
        if self._unsub_started is not None:
            self._unsub_started()
            self._unsub_started = None

    async def _handle_started(self, _event: Event) -> None:
        # The listener is gone once it fired, so it must not be removed on stop
        self._unsub_started = None
        await self.async_sync_all()

    async def _handle_changed(self, event: Event) -> None:
        if idea_id := event.data.get(ATTR_ID):
            await self.async_sync(str(idea_id))

    async def _handle_deleted(self, event: Event) -> None:
        record = event.data.get(ATTR_CALENDAR_EVENT)
        if isinstance(record, dict):
            async with self._lock:
                await self._async_remove(record)

    async def async_sync_all(self) -> None:
        """Bring the events of all open tasks up to date."""
        for idea in list(self.store.ideas):
            if idea.get(ATTR_STATUS) == "active":
                await self.async_sync(str(idea[ATTR_ID]))

    def wanted(self, idea: dict[str, Any]) -> dict[str, Any] | None:
        """Return the event a task should have, or None."""
        if not self.enabled or idea.get(ATTR_STATUS) != "active":
            return None
        switch = idea.get(ATTR_CALENDAR)
        due = dt_util.parse_datetime(str(idea.get(ATTR_DUE) or ""))
        if switch is False or due is None:
            return None
        if switch is None and not has_time(due):
            return None
        entity = calendar_for(self.options, idea.get(ATTR_CATEGORY))
        if not entity:
            return None
        return {
            "entity": entity,
            "start": dt_util.as_local(due).isoformat(),
            "summary": str(idea.get(ATTR_TEXT) or "").strip(),
        }

    async def async_sync(self, idea_id: str) -> None:
        """Bring the event of one task up to date."""
        async with self._lock:
            idea = next(
                (i for i in self.store.ideas if str(i.get(ATTR_ID)) == idea_id), None
            )
            if idea is None or idea.get(ATTR_STATUS) != "active":
                # Done tasks keep their event, as a record in the calendar
                return
            record = idea.get(ATTR_CALENDAR_EVENT)
            record = record if isinstance(record, dict) else None
            want = self.wanted(idea)
            if record is None and want is not None and idea.get(ATTR_CALENDAR_SYNCED):
                # Added once by an older version, without a way to find it again
                return
            if want is None:
                if record is not None:
                    await self._async_remove(record)
                    await self.store.async_mark_fields(
                        idea_id, {ATTR_CALENDAR_EVENT: None}
                    )
                return
            if record is not None and all(
                record.get(key) == want[key] for key in ("entity", "start", "summary")
            ):
                return
            start = dt_util.parse_datetime(want["start"])
            if start is None:
                return
            if record is None and start <= dt_util.now():
                # No events in the past for tasks that are late already
                return
            if record is not None:
                if await self._async_update(record, want, idea):
                    await self.store.async_mark_fields(
                        idea_id, {ATTR_CALENDAR_EVENT: {**record, **want}}
                    )
                    return
                await self._async_remove(record)
            new = await self._async_create(want, idea)
            await self.store.async_mark_fields(idea_id, {ATTR_CALENDAR_EVENT: new})

    def _entity(self, entity_id: str) -> CalendarEntity | None:
        component = self.hass.data.get(DATA_COMPONENT)
        return component.get_entity(entity_id) if component is not None else None

    def _supports(self, entity: CalendarEntity, feature: CalendarEntityFeature) -> bool:
        return bool((entity.supported_features or 0) & feature)

    def _event(self, want: dict[str, Any], idea: dict[str, Any]) -> dict[str, Any]:
        start = dt_util.parse_datetime(want["start"])
        assert start is not None
        event: dict[str, Any] = {
            "summary": want["summary"],
            "dtstart": start,
            "dtend": start + EVENT_LENGTH,
        }
        if description := idea.get(ATTR_DESCRIPTION):
            event["description"] = str(description)
        return event

    async def _async_create(
        self, want: dict[str, Any], idea: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Add the event and find its uid, for moving or removing it later."""
        entity = self._entity(want["entity"])
        if entity is None or not self._supports(
            entity, CalendarEntityFeature.CREATE_EVENT
        ):
            _LOGGER.warning("The calendar %s cannot take events", want["entity"])
            return None
        event = self._event(want, idea)
        try:
            await entity.async_create_event(**event)
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.warning("Could not add an event to %s: %s", want["entity"], err)
            return None
        record = dict(want)
        try:
            found = await entity.async_get_events(
                self.hass,
                event["dtstart"] - timedelta(minutes=1),
                event["dtend"] + timedelta(minutes=1),
            )
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.debug("Could not read back the event: %s", err)
            found = []
        for item in found:
            if item.summary == want["summary"] and item.uid:
                record["uid"] = item.uid
                break
        return record

    async def _async_update(
        self, record: dict[str, Any], want: dict[str, Any], idea: dict[str, Any]
    ) -> bool:
        """Change the event in place, where the calendar can do that."""
        if record.get("entity") != want["entity"] or not record.get("uid"):
            return False
        entity = self._entity(want["entity"])
        if entity is None or not self._supports(
            entity, CalendarEntityFeature.UPDATE_EVENT
        ):
            return False
        try:
            await entity.async_update_event(record["uid"], self._event(want, idea))
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.warning("Could not move the event in %s: %s", want["entity"], err)
            return False
        return True

    async def _async_remove(self, record: dict[str, Any]) -> None:
        """Remove an event, where the calendar can do that."""
        uid = record.get("uid")
        entity = self._entity(str(record.get("entity") or ""))
        if (
            not uid
            or entity is None
            or not self._supports(entity, CalendarEntityFeature.DELETE_EVENT)
        ):
            return
        try:
            await entity.async_delete_event(str(uid))
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.warning("Could not remove the event from %s: %s", record, err)
