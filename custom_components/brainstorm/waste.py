"""Turn the pickups of a waste calendar into tasks on the eve.

Every pickup in the chosen calendars, such as the ones of Waste Collection
Schedule, becomes a task like "🟡 Gelbe Tonne rausstellen" at the chosen time
on the evening before. The task ticks itself off once the pickup day is over.
With ChoreOps people chosen, the tasks of a pickup day go to them in turn.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
import logging
import re
from typing import TYPE_CHECKING, Any

from homeassistant.const import (
    EVENT_HOMEASSISTANT_STARTED,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import CALLBACK_TYPE, CoreState, Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_call_later, async_track_time_change
from homeassistant.util import dt as dt_util, slugify

from .const import (
    ATTR_ID,
    ATTR_STATUS,
    ATTR_WASTE,
    ATTR_WASTE_DONE,
    CONF_WASTE_CALENDARS,
    CONF_WASTE_CATEGORY,
    CONF_WASTE_CHOREOPS_POINTS,
    CONF_WASTE_CHOREOPS_USERS,
    CONF_WASTE_ENABLED,
    CONF_WASTE_TIME,
    DEFAULT_WASTE_TIME,
    SHARE_ALL,
    SHARE_EDIT,
    SOURCE_WASTE,
    WASTE_DOMAIN,
)
from .languages import get_pack
from .languages.common import LanguagePack

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

DEFAULT_ICON = "🗑️"
# Calendars may not be loaded yet right after a start
START_DELAY = 60
# One calendar entry can name several pickups, such as "Paper, Organic"
_SPLIT = re.compile(r"\s*[,;]\s*")
# A remark in brackets, also one that is cut off: "Residual (14-day"
_REMARK = re.compile(r"\s*\(.*$")


def waste_available(hass: HomeAssistant) -> bool:
    """Tell whether Waste Collection Schedule is set up."""
    return bool(hass.config_entries.async_entries(WASTE_DOMAIN)) or bool(
        waste_calendars(hass)
    )


def waste_calendars(hass: HomeAssistant) -> list[str]:
    """Return the calendars of Waste Collection Schedule."""
    return sorted(
        entry.entity_id
        for entry in er.async_get(hass).entities.values()
        if entry.platform == WASTE_DOMAIN
        and entry.domain == "calendar"
        and entry.disabled_by is None
    )


def waste_name(summary: str, pack: LanguagePack) -> str:
    """Return the waste type of a calendar entry, without words like "Pickup"."""
    name = _REMARK.sub("", summary).strip()
    words = name.split()
    while len(words) > 1 and words[0].casefold().rstrip(":") in pack.waste_prefixes:
        words.pop(0)
    return " ".join(words) or summary.strip()


def waste_icon(name: str, pack: LanguagePack) -> str:
    """Return the sign of a waste type, such as 🟡 for packaging."""
    folded = name.casefold()
    return next(
        (icon for word, icon in pack.waste_icons if word in folded), DEFAULT_ICON
    )


def parse_time(value: Any) -> time:
    """Return the time of the settings, the default one if it is not readable."""
    parsed = dt_util.parse_time(str(value or "")) if value else None
    return parsed or (dt_util.parse_time(DEFAULT_WASTE_TIME) or time(18))


def _event_day(value: Any) -> date | None:
    """Return the day an event starts on, for all-day and timed events."""
    if isinstance(value, dict):
        value = value.get("date") or value.get("dateTime")
    text = str(value or "")
    if (day := dt_util.parse_date(text)) is not None:
        return day
    if (moment := dt_util.parse_datetime(text)) is not None:
        return dt_util.as_local(moment).date()
    return None


class WasteWatcher:
    """Create the tasks of the pickups and tick them off afterwards."""

    def __init__(
        self, hass: HomeAssistant, store: BrainstormStore, options: dict[str, Any]
    ) -> None:
        """Remember the settings."""
        self.hass = hass
        self.store = store
        self.enabled = bool(options.get(CONF_WASTE_ENABLED))
        self.calendars: list[str] = list(options.get(CONF_WASTE_CALENDARS) or [])
        self.category = str(options.get(CONF_WASTE_CATEGORY) or "").strip() or None
        self.time = parse_time(options.get(CONF_WASTE_TIME))
        self.users: list[str] = [
            str(user) for user in options.get(CONF_WASTE_CHOREOPS_USERS) or [] if user
        ]
        points = options.get(CONF_WASTE_CHOREOPS_POINTS)
        self.points = int(points) if points not in (None, "") else None
        self._unsubs: list[CALLBACK_TYPE] = []
        self._unsub_started: CALLBACK_TYPE | None = None

    async def async_start(self) -> None:
        """Check at the chosen time and after midnight, and once HA runs."""
        if self.enabled:
            self._unsubs.append(
                async_track_time_change(
                    self.hass,
                    self._handle_eve,
                    hour=self.time.hour,
                    minute=self.time.minute,
                    second=self.time.second,
                )
            )
        self._unsubs.append(
            async_track_time_change(
                self.hass, self._handle_midnight, hour=0, minute=0, second=30
            )
        )
        if self.hass.state is CoreState.running:
            self._unsubs.append(
                async_call_later(self.hass, START_DELAY, self._handle_later)
            )
        else:
            self._unsub_started = self.hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED, self._handle_started
            )

    @callback
    def async_stop(self) -> None:
        """Stop checking."""
        while self._unsubs:
            self._unsubs.pop()()
        if self._unsub_started is not None:
            self._unsub_started()
            self._unsub_started = None

    @callback
    def _handle_started(self, _event: Event) -> None:
        """Wait a moment for the calendars once Home Assistant has started."""
        # The listener is gone once it fired, so it must not be removed on stop
        self._unsub_started = None
        self._unsubs.append(
            async_call_later(self.hass, START_DELAY, self._handle_later)
        )

    async def _handle_later(self, _now: datetime) -> None:
        """Catch up on what was missed while Home Assistant was off."""
        await self.async_catch_up(dt_util.now())

    async def _handle_eve(self, now: datetime) -> None:
        """Create the tasks of tomorrow's pickups."""
        await self.async_create_for(now.date() + timedelta(days=1))

    async def _handle_midnight(self, now: datetime) -> None:
        """Tick off the tasks of pickups that are over."""
        await self.async_close_past(now.date())

    async def async_catch_up(self, now: datetime) -> None:
        """Close what is over and, after the chosen time, add tomorrow's tasks."""
        await self.async_close_past(now.date())
        if self.enabled and now.time() >= self.time:
            await self.async_create_for(now.date() + timedelta(days=1))

    def _calendars(self) -> list[str]:
        """Return the chosen calendars, or all of Waste Collection Schedule."""
        return self.calendars or waste_calendars(self.hass)

    async def _async_events(self, day: date) -> list[tuple[str, dict[str, Any]]]:
        """Return the events of a day in the calendars, with the calendar's name.

        Every calendar is read on its own, so one that is unavailable does not
        cost the pickups of the others.
        """
        start = dt_util.start_of_local_day(day)
        events: list[tuple[str, dict[str, Any]]] = []
        for entity in self._calendars():
            state = self.hass.states.get(entity)
            if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                continue
            try:
                response = await self.hass.services.async_call(
                    "calendar",
                    "get_events",
                    {
                        "entity_id": entity,
                        "start_date_time": start.isoformat(),
                        "end_date_time": (start + timedelta(days=1)).isoformat(),
                    },
                    blocking=True,
                    return_response=True,
                )
            except HomeAssistantError as err:
                _LOGGER.warning("Could not read the waste calendar %s: %s", entity, err)
                continue
            result = (response or {}).get(entity)
            for event in result.get("events", []) if isinstance(result, dict) else []:
                if _event_day(event.get("start")) == day:
                    events.append((str(state.name), event))
        return events

    def _tasks(self) -> list[dict[str, Any]]:
        """Return the waste tasks, open and done."""
        return [
            idea for idea in self.store.ideas if isinstance(idea.get(ATTR_WASTE), dict)
        ]

    def _user_for(self, day: date) -> str | None:
        """Return whose turn a pickup day is, keeping one person per day."""
        if not self.users:
            return None
        iso = day.isoformat()
        earlier: list[tuple[str, str]] = []
        for idea in self._tasks():
            info = idea[ATTR_WASTE]
            user = info.get("user")
            if user not in self.users:
                continue
            if info.get("date") == iso:
                return str(user)
            if str(info.get("date") or "") < iso:
                earlier.append((str(info.get("date")), str(user)))
        if not earlier:
            return self.users[0]
        last = max(earlier)[1]
        return self.users[(self.users.index(last) + 1) % len(self.users)]

    async def async_create_for(self, day: date) -> int:
        """Add a task for every pickup on a day that has none yet."""
        pack = get_pack(self.hass.config.language)
        iso = day.isoformat()
        known = {
            str(idea[ATTR_WASTE].get("key"))
            for idea in self._tasks()
            if idea[ATTR_WASTE].get("date") == iso
        }
        due = dt_util.start_of_local_day(day - timedelta(days=1)) + timedelta(
            hours=self.time.hour, minutes=self.time.minute
        )
        added = 0
        for calendar, event in await self._async_events(day):
            summary = " ".join(str(event.get("summary") or "").split())
            for part in _SPLIT.split(summary):
                if not part:
                    continue
                name = waste_name(part, pack)
                key = slugify(name)
                if not key or key in known:
                    continue
                known.add(key)
                await self._async_add(pack, day, key, name, calendar, summary, due)
                added += 1
        return added

    async def _async_add(
        self,
        pack: LanguagePack,
        day: date,
        key: str,
        name: str,
        calendar: str,
        summary: str,
        due: datetime,
    ) -> None:
        """Add the task of one pickup and hand it to ChoreOps if wanted."""
        user = self._user_for(day)
        idea = await self.store.async_add_idea(
            text=pack.msg("waste_task", icon=waste_icon(name, pack), name=name),
            category=self.category,
            source=SOURCE_WASTE,
            device=calendar,
            verbatim=True,
            due=due,
            description=pack.msg(
                "waste_task_description", calendar=calendar, summary=summary
            ),
            shares={SHARE_ALL: SHARE_EDIT} if self.store.privacy_enabled else None,
        )
        info: dict[str, Any] = {"date": day.isoformat(), "key": key}
        if user:
            info["user"] = user
        await self.store.async_set_fields({idea[ATTR_ID]: {ATTR_WASTE: info}})
        _LOGGER.info("Waste task added for %s on %s", name, day)
        bridge = self.store.choreops
        if user and bridge is not None:
            try:
                await bridge.async_hand_over(idea, user, self.points)
            except HomeAssistantError as err:
                # The task stays in Brainstorm, only the chore is missing
                _LOGGER.warning(
                    "Waste task for %s not handed to ChoreOps: %s", name, err
                )

    async def async_close_past(self, today: date) -> int:
        """Tick off the open tasks of pickups before today."""
        iso = today.isoformat()
        over = [
            idea
            for idea in self._tasks()
            if not idea.get(ATTR_WASTE_DONE)
            and str(idea[ATTR_WASTE].get("date") or "") < iso
        ]
        if not over:
            return 0
        # Marked first, so the task is not taken for an open one again
        await self.store.async_set_fields(
            {idea[ATTR_ID]: {ATTR_WASTE_DONE: True} for idea in over}
        )
        for idea in over:
            if idea.get(ATTR_STATUS) == "active":
                await self.store.async_update_idea(idea[ATTR_ID], status="completed")
        return len(over)
