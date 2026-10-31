"""Proactive reminders, briefing, review, places and people for Brainstorm Hub."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
import logging
import re
from typing import TYPE_CHECKING, Any

from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import entity_sources
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_ALEXA_NATIVE,
    ATTR_ASSIGNEE,
    ATTR_CALENDAR_SYNCED,
    ATTR_CATEGORY,
    ATTR_CREATED_AT,
    ATTR_DEVICE,
    ATTR_DUE,
    ATTR_ESCALATED,
    ATTR_ID,
    ATTR_PRIORITY,
    ATTR_REMINDED_AT,
    ATTR_TEXT,
    ATTR_TRIGGER,
    ATTR_URGENT_SENT,
    CONF_AI_ENABLED,
    CONF_AI_ENTITY,
    CONF_ARRIVAL_ENABLED,
    CONF_CALENDAR_ENABLED,
    CONF_CALENDAR_ENTITY,
    CONF_DEFAULT_PERSON,
    CONF_DIGEST_ENABLED,
    CONF_DIGEST_PRESENCE,
    CONF_DIGEST_TIME,
    CONF_LIST_RULES,
    CONF_LIST_RULES_ENABLED,
    CONF_NOTIFY_ENABLED,
    CONF_PERSON_RULES,
    CONF_PERSONS_ENABLED,
    CONF_PLACES_ENABLED,
    CONF_QUIET_ENABLED,
    CONF_QUIET_END,
    CONF_QUIET_START,
    CONF_REMINDER_ALEXA,
    CONF_REMINDER_DELAY,
    CONF_REMINDER_ECHOS,
    CONF_REMINDER_NOTIFY,
    CONF_REMINDERS_ENABLED,
    CONF_REVIEW_DAYS,
    CONF_REVIEW_ENABLED,
    CONF_REVIEW_TIME,
    CONF_REVIEW_WEEKDAY,
    CONF_URGENT_DELAY,
    CONF_URGENT_ENABLED,
    CONF_URGENT_NOTIFY,
    DEFAULT_REVIEW_DAYS,
    DEFAULT_URGENT_DELAY,
    EVENT_REMINDER_DUE,
    PRIORITY_HIGH,
    PRIORITY_URGENT,
    REMINDER_ALEXA_FIXED,
    REMINDER_ALEXA_OFF,
    REMINDER_ALEXA_ORIGIN,
    REMINDERS_STORAGE_KEY,
    REMINDERS_STORAGE_VERSION,
    RULE_CHANNEL,
    RULE_CHANNEL_ALEXA,
    RULE_CHANNEL_DEFAULT,
    RULE_CHANNEL_NONE,
    RULE_CHANNEL_NOTIFY,
    RULE_NOTIFY,
    RULE_SCHEDULE_ENABLED,
    RULE_SCHEDULE_TIME,
    RULE_SCHEDULE_WEEKDAYS,
    RULE_ZONE,
    RULE_ZONE_ENABLED,
)
from .nlp import parse_due, strip_reminder_words

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

CHECK_INTERVAL = timedelta(seconds=30)
LATE_SCHEDULE_LIMIT = timedelta(hours=2)
PRESENCE_SCHEDULE_LIMIT = timedelta(hours=6)
AI_TIMEOUT_SECONDS = 20
CALENDAR_EVENT_LENGTH = timedelta(minutes=30)
REVIEW_MAX_ITEMS = 5
ACTION_PREFIX = "BRAINSTORM_"
ACTION_DONE = "DONE"
ACTION_SNOOZE = "SNOOZE"
ACTION_TOMORROW = "TOMORROW"
TOMORROW_TIME = time(9, 0)
ZONE_HOME = "zone.home"
ALEXA_MEDIA_DOMAIN = "alexa_media"
MOBILE_APP_SERVICE_PREFIX = "mobile_app_"
PRESENT_STATES = ("on", "home", "detected", "occupied")

_HOME_WORDS = (
    r"(?:wieder\s+)?(?:nach\s+hause\s+komm\w*|heim\s?komm\w*|zu\s?hause\s+(?:bin|ist)"
    r"|daheim\s+(?:bin|ist))"
)
_PLACE_WORDS = r"(?:im|in\s+der|in|beim|bei|am)"


def _parse_time(value: str | None) -> time | None:
    """Parse a stored time of day."""
    return dt_util.parse_time(value) if value else None


def is_quiet_time(now: datetime, start: time | None, end: time | None) -> bool:
    """Return whether a time lies in the quiet hours, which may span midnight."""
    if start is None or end is None or start == end:
        return False
    current = now.time()
    if start < end:
        return start <= current < end
    return current >= start or current < end


def format_due(due: datetime, now: datetime) -> str:
    """Return a due time the way a person says it."""
    due = dt_util.as_local(due)
    today = dt_util.as_local(now).date()
    clock = f"{due.hour} Uhr" if due.minute == 0 else f"{due.hour} Uhr {due.minute}"
    day = due.date()
    if day == today:
        return f"heute um {clock}"
    if day == today + timedelta(days=1):
        return f"morgen um {clock}"
    if day == today + timedelta(days=2):
        return f"übermorgen um {clock}"
    weekday = (
        "Montag",
        "Dienstag",
        "Mittwoch",
        "Donnerstag",
        "Freitag",
        "Samstag",
        "Sonntag",
    )[day.weekday()]
    return f"am {weekday}, den {day.day}.{day.month}., um {clock}"


def find_echo_entity(hass: HomeAssistant, name: str) -> str | None:
    """Find an Echo by its name, as other integrations may use the same name."""
    sources = entity_sources(hass)
    for state in hass.states.async_all("media_player"):
        source = sources.get(state.entity_id)
        if (
            source is not None
            and source["domain"] == ALEXA_MEDIA_DOMAIN
            and state.attributes.get("friendly_name") == name
        ):
            return state.entity_id
    return None


@dataclass
class ReminderRequest:
    """What a spoken reminder asks for."""

    text: str
    due: datetime | None = None
    trigger: dict[str, str | None] | None = None
    assignee: str | None = None


def _names_of(hass: HomeAssistant, domain: str) -> dict[str, str]:
    """Return lower-case names and their first words for the entities of a domain."""
    names: dict[str, str] = {}
    for state in hass.states.async_all(domain):
        name = str(state.attributes.get("friendly_name") or state.name).lower().strip()
        names.setdefault(name, state.entity_id)
        first = re.split(r"[\s,-]+", name, maxsplit=1)[0]
        if len(first) >= 3:
            names.setdefault(first, state.entity_id)
    return names


def _alternatives(names: dict[str, str]) -> str:
    """Return a regular expression group for names, longest first."""
    return "|".join(re.escape(name) for name in sorted(names, key=len, reverse=True))


def build_reminder_request(
    hass: HomeAssistant, options: dict[str, Any], text: str, now: datetime
) -> ReminderRequest:
    """Understand who should be reminded of what, when or where."""
    remaining = text.strip()
    assignee: str | None = None
    people: dict[str, str] = {}

    if options.get(CONF_PERSONS_ENABLED):
        people = _names_of(hass, "person")
        if people and (
            match := re.match(rf"({_alternatives(people)})\b\s*", remaining, re.I)
        ):
            assignee = people[match.group(1).lower()]
            remaining = remaining[match.end() :]

    due, remaining = parse_due(remaining, now)
    trigger: dict[str, str | None] | None = None
    default_person = options.get(CONF_DEFAULT_PERSON) or None
    who = r"(ich|sie|er"
    if people:
        who += f"|{_alternatives(people)}"
    who += ")"

    def person_for(word: str | None) -> str | None:
        """Return the person a word in the sentence stands for."""
        lowered = (word or "").lower()
        if lowered == "ich":
            return default_person
        if lowered in ("sie", "er"):
            return assignee
        return people.get(lowered, assignee or default_person)

    if due is None and options.get(CONF_ARRIVAL_ENABLED):
        if match := re.search(rf"\bwenn\s+{who}\s+{_HOME_WORDS}\b", remaining, re.I):
            trigger = {"zone": ZONE_HOME, "person": person_for(match.group(1))}
            remaining = f"{remaining[: match.start()]} {remaining[match.end() :]}"

    if due is None and trigger is None and options.get(CONF_PLACES_ENABLED):
        zones = {
            name: entity
            for name, entity in _names_of(hass, "zone").items()
            if entity != ZONE_HOME
        }
        if zones:
            place = _alternatives(zones)
            match = re.search(
                rf"\bwenn\s+{who}\s+{_PLACE_WORDS}\s+({place})(?:\s+(?:bin|ist))?\b",
                remaining,
                re.I,
            )
            if match:
                trigger = {
                    "zone": zones[match.group(2).lower()],
                    "person": person_for(match.group(1)),
                }
            elif match := re.search(
                rf"^(?:{_PLACE_WORDS})\s+({place})\b", remaining, re.I
            ):
                trigger = {
                    "zone": zones[match.group(1).lower()],
                    "person": person_for("ich"),
                }
            if match:
                remaining = f"{remaining[: match.start()]} {remaining[match.end() :]}"

    return ReminderRequest(strip_reminder_words(remaining), due, trigger, assignee)


class ReminderManager:
    """Deliver ideas over the channels this installation has switched on."""

    def __init__(
        self, hass: HomeAssistant, store: BrainstormStore, options: dict[str, Any]
    ) -> None:
        """Initialize the manager."""
        self.hass = hass
        self._ideas = store
        self._options = options
        self._state: Store[dict[str, Any]] = Store(
            hass, REMINDERS_STORAGE_VERSION, REMINDERS_STORAGE_KEY
        )
        self._last_digest: date | None = None
        self._last_review: date | None = None
        self._last_lists: dict[str, str] = {}
        self._last_list_zones: dict[str, str] = {}
        self._unsubs: list[CALLBACK_TYPE] = []

    @property
    def enabled(self) -> bool:
        """Return whether reminders are switched on at all."""
        return bool(self._options.get(CONF_REMINDERS_ENABLED, True))

    def _rule(self, category: str | None) -> dict[str, Any]:
        """Return the active rule of a list."""
        if not self._options.get(CONF_LIST_RULES_ENABLED):
            return {}
        return (self._options.get(CONF_LIST_RULES) or {}).get(category or "", {})

    def _person_rule(self, person: str | None) -> dict[str, Any]:
        """Return the channels chosen for a person."""
        if not person or not self._options.get(CONF_PERSONS_ENABLED):
            return {}
        return (self._options.get(CONF_PERSON_RULES) or {}).get(person, {})

    @property
    def _uses_places(self) -> bool:
        """Return whether arriving somewhere can cause a reminder."""
        if self._options.get(CONF_PLACES_ENABLED):
            return True
        return bool(self._options.get(CONF_ARRIVAL_ENABLED))

    async def async_start(self) -> None:
        """Start watching for due ideas, unless switched off."""
        data = await self._state.async_load() or {}
        self._last_digest = dt_util.parse_date(data.get("last_digest") or "")
        self._last_review = dt_util.parse_date(data.get("last_review") or "")
        self._last_lists = data.get("last_lists", {})
        self._last_list_zones = data.get("last_list_zones", {})
        if not self.enabled:
            return
        self._unsubs = [
            async_track_time_interval(
                self.hass, self._async_tick, CHECK_INTERVAL, cancel_on_shutdown=True
            ),
            self.hass.bus.async_listen(
                "mobile_app_notification_action", self._async_handle_action
            ),
        ]
        if self._uses_places:
            self._unsubs.append(
                self.hass.bus.async_listen(
                    EVENT_STATE_CHANGED,
                    self._async_handle_state_change,
                    event_filter=_is_person_event,
                )
            )

    @callback
    def async_stop(self) -> None:
        """Stop watching for due ideas."""
        while self._unsubs:
            self._unsubs.pop()()

    async def _async_tick(self, now: datetime) -> None:
        """Deliver whatever is due."""
        await self.async_check(dt_util.now())

    def _is_quiet(self, now: datetime) -> bool:
        """Return whether the quiet hours apply right now."""
        if not self._options.get(CONF_QUIET_ENABLED, True):
            return False
        return is_quiet_time(
            now,
            _parse_time(self._options.get(CONF_QUIET_START)),
            _parse_time(self._options.get(CONF_QUIET_END)),
        )

    async def async_check(self, now: datetime) -> None:
        """Deliver everything that is due."""
        if not self.enabled:
            return
        quiet = self._is_quiet(now)
        for idea in self._ideas.ideas:
            if idea.get("status") != "active" or not idea.get(ATTR_DUE):
                continue
            await self._async_sync_calendar(idea, now)
            due = dt_util.parse_datetime(idea[ATTR_DUE])
            if due is None or due > now:
                continue
            await self._async_process_due_idea(idea, now, quiet)
        if not quiet:
            await self._async_check_digest(now)
            await self._async_check_review(now)
            await self._async_check_list_schedules(now)

    def _fire_due_event(self, idea: dict[str, Any]) -> None:
        """Tell automations about a reminder."""
        self.hass.bus.async_fire(
            EVENT_REMINDER_DUE,
            {
                ATTR_ID: idea[ATTR_ID],
                ATTR_TEXT: idea.get(ATTR_TEXT),
                ATTR_CATEGORY: idea.get(ATTR_CATEGORY),
                ATTR_PRIORITY: idea.get(ATTR_PRIORITY),
                ATTR_DEVICE: idea.get(ATTR_DEVICE),
                ATTR_DUE: idea.get(ATTR_DUE),
                ATTR_ASSIGNEE: idea.get(ATTR_ASSIGNEE),
            },
        )

    async def _async_process_due_idea(
        self, idea: dict[str, Any], now: datetime, quiet: bool
    ) -> None:
        """Send the first reminder or a follow-up."""
        urgent = idea.get(ATTR_PRIORITY) == PRIORITY_URGENT
        reminded_at = idea.get(ATTR_REMINDED_AT)
        if not reminded_at:
            # Quiet hours hold everything back, only urgent ideas reach the phone
            if quiet and not urgent:
                return
            self._fire_due_event(idea)
            alexa_ok = False if quiet else await self._async_speak_reminder(idea)
            send_now = (
                not alexa_ok or int(self._options.get(CONF_REMINDER_DELAY, 0)) == 0
            )
            if send_now:
                await self._async_notify_idea(idea)
            await self._ideas.async_mark_reminded(idea[ATTR_ID], escalated=send_now)
            return

        if quiet and not urgent:
            return
        sent = dt_util.parse_datetime(reminded_at)
        if sent is None:
            return
        if not idea.get(ATTR_ESCALATED):
            delay = timedelta(minutes=int(self._options.get(CONF_REMINDER_DELAY, 0)))
            if sent + delay <= now:
                await self._async_notify_idea(idea)
                await self._ideas.async_mark_reminded(idea[ATTR_ID], escalated=True)
        await self._async_check_urgent_stage(idea, sent, now)

    async def _async_check_urgent_stage(
        self, idea: dict[str, Any], sent: datetime, now: datetime
    ) -> None:
        """Send important ideas that are still open to the urgent services."""
        if (
            not self._options.get(CONF_URGENT_ENABLED)
            or idea.get(ATTR_URGENT_SENT)
            or idea.get(ATTR_PRIORITY) not in (PRIORITY_URGENT, PRIORITY_HIGH)
        ):
            return
        delay = int(self._options.get(CONF_URGENT_DELAY, DEFAULT_URGENT_DELAY))
        if sent + timedelta(minutes=delay) > now:
            return
        for service in self._options.get(CONF_URGENT_NOTIFY) or []:
            await self._async_send(
                service, "Brainstorm: Noch offen", str(idea.get(ATTR_TEXT)), None
            )
        await self._ideas.async_mark_fields(idea[ATTR_ID], {ATTR_URGENT_SENT: True})

    def _echo_entity_from_name(self, name: str | None) -> str | None:
        """Find the Echo of an idea by the name stored with it."""
        return find_echo_entity(self.hass, name) if name else None

    def _alexa_targets(self, idea: dict[str, Any] | None) -> list[str]:
        """Return the Echos to speak on, following the chosen mode."""
        mode = self._options.get(CONF_REMINDER_ALEXA, REMINDER_ALEXA_OFF)
        if mode == REMINDER_ALEXA_OFF:
            return []
        fixed = list(self._options.get(CONF_REMINDER_ECHOS) or [])
        if mode == REMINDER_ALEXA_FIXED:
            return fixed
        if mode == REMINDER_ALEXA_ORIGIN and idea is not None:
            echo = self._echo_entity_from_name(idea.get(ATTR_DEVICE))
            if echo:
                return [echo]
            if fixed:
                return fixed
        for state in self.hass.states.async_all("media_player"):
            if state.attributes.get("last_called") is True:
                return [state.entity_id]
        return fixed

    def _idea_echos(self, idea: dict[str, Any]) -> list[str]:
        """Return the Echos for an idea, following its list and person."""
        channel = self._rule(idea.get(ATTR_CATEGORY)).get(
            RULE_CHANNEL, RULE_CHANNEL_DEFAULT
        )
        if channel in (RULE_CHANNEL_NONE, RULE_CHANNEL_NOTIFY):
            return []
        person_rule = self._person_rule(idea.get(ATTR_ASSIGNEE))
        if person_rule:
            return list(person_rule.get("echos") or [])
        return self._alexa_targets(idea)

    def _idea_services(self, idea: dict[str, Any]) -> list[str]:
        """Return the notification services for an idea."""
        if not self._options.get(CONF_NOTIFY_ENABLED, True):
            return []
        rule = self._rule(idea.get(ATTR_CATEGORY))
        channel = rule.get(RULE_CHANNEL, RULE_CHANNEL_DEFAULT)
        if channel in (RULE_CHANNEL_NONE, RULE_CHANNEL_ALEXA):
            return []
        person_rule = self._person_rule(idea.get(ATTR_ASSIGNEE))
        if person_rule:
            return list(person_rule.get("notify") or [])
        return list(rule.get(RULE_NOTIFY) or self._options.get(CONF_REMINDER_NOTIFY) or [])

    async def _async_speak(self, targets: list[str], message: str) -> bool:
        """Speak a message on Echos and report whether that worked."""
        if not targets or not self.hass.services.has_service("notify", "alexa_media"):
            return False
        try:
            await self.hass.services.async_call(
                "notify",
                "alexa_media",
                {"message": message, "target": targets, "data": {"type": "tts"}},
                blocking=True,
            )
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.warning("Could not speak a Brainstorm reminder: %s", err)
            return False
        return True

    async def _async_speak_reminder(self, idea: dict[str, Any]) -> bool:
        """Speak a reminder for an idea."""
        # Alexa already rings by itself for a reminder made in the skill
        if idea.get(ATTR_ALEXA_NATIVE):
            return True
        return await self._async_speak(
            self._idea_echos(idea), f"Erinnerung: {idea.get(ATTR_TEXT)}."
        )

    async def _async_send(
        self, service: str, title: str, message: str, data: dict[str, Any] | None
    ) -> None:
        """Send a message over one configured service, without stopping the others."""
        domain, _, name = service.partition(".")
        payload: dict[str, Any] = {"title": title, "message": message}
        if data:
            payload["data"] = data
        try:
            if self.hass.services.has_service(domain, name):
                await self.hass.services.async_call(
                    domain, name, payload, blocking=True
                )
            elif self.hass.states.get(service) is not None:
                await self.hass.services.async_call(
                    "notify",
                    "send_message",
                    {"title": title, "message": message},
                    blocking=True,
                    target={"entity_id": service},
                )
            else:
                _LOGGER.warning("Notification service %s does not exist", service)
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.warning("Could not send over %s: %s", service, err)

    def _phone_service(self, service: str) -> str:
        """Prefer a phone's own service, as its notify entity cannot show buttons."""
        _, _, name = service.partition(".")
        phone_service = f"{MOBILE_APP_SERVICE_PREFIX}{name}"
        if self.hass.services.has_service("notify", phone_service):
            return f"notify.{phone_service}"
        return service

    async def _async_notify_idea(self, idea: dict[str, Any]) -> None:
        """Send a reminder to the phones and other services."""
        idea_id = idea[ATTR_ID]
        for configured in self._idea_services(idea):
            service = self._phone_service(configured)
            data = None
            # Only the companion app understands buttons
            if service.startswith(f"notify.{MOBILE_APP_SERVICE_PREFIX}"):
                data = {
                    "tag": f"brainstorm_{idea_id}",
                    "actions": [
                        {
                            "action": f"{ACTION_PREFIX}{ACTION_DONE}_{idea_id}",
                            "title": "Erledigt",
                        },
                        {
                            "action": f"{ACTION_PREFIX}{ACTION_SNOOZE}_{idea_id}",
                            "title": "1 Stunde später",
                        },
                        {
                            "action": f"{ACTION_PREFIX}{ACTION_TOMORROW}_{idea_id}",
                            "title": "Morgen",
                        },
                    ],
                }
            await self._async_send(
                service, "Brainstorm: Erinnerung", str(idea.get(ATTR_TEXT)), data
            )

    async def _async_handle_action(self, event: Event) -> None:
        """Handle a button pressed in a phone notification."""
        action = str(event.data.get("action") or "")
        if not action.startswith(ACTION_PREFIX):
            return
        kind, _, idea_id = action[len(ACTION_PREFIX) :].partition("_")
        if kind == ACTION_DONE:
            await self._ideas.async_update_idea(idea_id, status="completed")
        elif kind == ACTION_SNOOZE:
            await self._ideas.async_set_due(
                idea_id, dt_util.now() + timedelta(hours=1)
            )
        elif kind == ACTION_TOMORROW:
            tomorrow = dt_util.now().date() + timedelta(days=1)
            await self._ideas.async_set_due(
                idea_id,
                datetime.combine(tomorrow, TOMORROW_TIME, dt_util.DEFAULT_TIME_ZONE),
            )

    def _zone_of_state(self, state_value: str | None) -> str | None:
        """Return the zone a person's state stands for."""
        if state_value == "home":
            return ZONE_HOME
        for zone in self.hass.states.async_all("zone"):
            if state_value and zone.attributes.get("friendly_name") == state_value:
                return zone.entity_id
        return None

    def _zone_allowed(self, zone: str | None) -> bool:
        """Return whether reminders for this zone are switched on."""
        if zone == ZONE_HOME:
            return bool(self._options.get(CONF_ARRIVAL_ENABLED))
        return zone is not None and bool(self._options.get(CONF_PLACES_ENABLED))

    async def _async_handle_state_change(self, event: Event) -> None:
        """Remind a person who has just arrived somewhere."""
        new_state = event.data.get("new_state")
        old_state = event.data.get("old_state")
        if new_state is None or old_state is None or new_state.state == old_state.state:
            return
        if old_state.state in ("unknown", "unavailable"):
            return
        zone = self._zone_of_state(new_state.state)
        if not self._zone_allowed(zone):
            return
        person = new_state.entity_id
        now = dt_util.now()
        quiet = self._is_quiet(now)
        for idea in self._ideas.ideas:
            trigger = idea.get(ATTR_TRIGGER)
            if (
                idea.get("status") != "active"
                or not trigger
                or idea.get(ATTR_REMINDED_AT)
                or trigger.get("zone") != zone
                or trigger.get("person") not in (None, person)
            ):
                continue
            self._fire_due_event(idea)
            # Only someone at home can hear an Echo
            if zone == ZONE_HOME and not quiet:
                await self._async_speak_reminder(idea)
            await self._async_notify_idea(idea)
            await self._ideas.async_mark_reminded(idea[ATTR_ID], escalated=True)
        await self._async_check_list_zones(zone, now)

    async def _async_check_list_zones(self, zone: str | None, now: datetime) -> None:
        """Send a list's open ideas when someone reaches its place, once a day."""
        if not self._options.get(CONF_LIST_RULES_ENABLED):
            return
        today = now.date().isoformat()
        for category, rule in (self._options.get(CONF_LIST_RULES) or {}).items():
            if (
                not rule.get(RULE_ZONE_ENABLED)
                or rule.get(RULE_ZONE) != zone
                or self._last_list_zones.get(category) == today
            ):
                continue
            message = self._list_message(category)
            self._last_list_zones[category] = today
            await self._async_save_state()
            if message:
                await self._async_broadcast_list(category, rule, message)

    def _list_message(self, category: str) -> str | None:
        """Return the open ideas of a list as a sentence."""
        texts = [
            str(idea.get(ATTR_TEXT))
            for idea in self._ideas.ideas
            if idea.get("status") == "active" and idea.get(ATTR_CATEGORY) == category
        ]
        if not texts:
            return None
        return f"{category.replace('&', 'und')}: {', '.join(texts)}."

    async def _async_broadcast_list(
        self, category: str, rule: dict[str, Any], message: str
    ) -> None:
        """Send a list's message over the channels of its rule."""
        channel = rule.get(RULE_CHANNEL, RULE_CHANNEL_DEFAULT)
        if channel == RULE_CHANNEL_NONE:
            return
        if channel in (RULE_CHANNEL_DEFAULT, RULE_CHANNEL_ALEXA):
            await self._async_speak(self._alexa_targets(None), message)
        if channel in (RULE_CHANNEL_DEFAULT, RULE_CHANNEL_NOTIFY) and self._options.get(
            CONF_NOTIFY_ENABLED, True
        ):
            services = rule.get(RULE_NOTIFY) or self._options.get(CONF_REMINDER_NOTIFY)
            for service in services or []:
                await self._async_send(service, f"Brainstorm: {category}", message, None)

    async def _async_check_list_schedules(self, now: datetime) -> None:
        """Send lists on their chosen days, like work ideas on weekdays at eight."""
        if not self._options.get(CONF_LIST_RULES_ENABLED):
            return
        for category, rule in (self._options.get(CONF_LIST_RULES) or {}).items():
            last = dt_util.parse_date(self._last_lists.get(category) or "")
            if (
                not rule.get(RULE_SCHEDULE_ENABLED)
                or str(now.weekday()) not in (rule.get(RULE_SCHEDULE_WEEKDAYS) or [])
                or not self._is_scheduled_now(
                    now, _parse_time(rule.get(RULE_SCHEDULE_TIME)), last
                )
            ):
                continue
            self._last_lists[category] = now.date().isoformat()
            await self._async_save_state()
            if message := self._list_message(category):
                await self._async_broadcast_list(category, rule, message)

    async def _async_sync_calendar(self, idea: dict[str, Any], now: datetime) -> None:
        """Add an idea's reminder to the chosen calendar, once."""
        entity = self._options.get(CONF_CALENDAR_ENTITY)
        if (
            not self._options.get(CONF_CALENDAR_ENABLED)
            or not entity
            or idea.get(ATTR_CALENDAR_SYNCED)
        ):
            return
        due = dt_util.parse_datetime(idea[ATTR_DUE])
        if due is None or due <= now:
            return
        try:
            await self.hass.services.async_call(
                "calendar",
                "create_event",
                {
                    "summary": str(idea.get(ATTR_TEXT)),
                    "start_date_time": due.isoformat(),
                    "end_date_time": (due + CALENDAR_EVENT_LENGTH).isoformat(),
                },
                blocking=True,
                target={"entity_id": entity},
            )
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.warning("Could not add a reminder to %s: %s", entity, err)
        # Marked even after an error, a broken calendar must not retry every 30 seconds
        await self._ideas.async_mark_fields(idea[ATTR_ID], {ATTR_CALENDAR_SYNCED: True})

    async def _async_summarize(self, message: str) -> str:
        """Let the chosen AI shorten a long text, keeping the original on any problem."""
        entity = self._options.get(CONF_AI_ENTITY)
        if not self._options.get(CONF_AI_ENABLED) or not entity:
            return message
        instructions = (
            "Fasse diese Erinnerung als kurzen, natürlichen deutschen Satz zum "
            "Vorlesen zusammen. Erfinde nichts dazu und lasse keinen Eintrag weg: "
            f"{message}"
        )
        try:
            async with asyncio.timeout(AI_TIMEOUT_SECONDS):
                result = await self.hass.services.async_call(
                    "ai_task",
                    "generate_data",
                    {
                        "task_name": "Brainstorm",
                        "instructions": instructions,
                        "entity_id": entity,
                    },
                    blocking=True,
                    return_response=True,
                )
        except (HomeAssistantError, ValueError, TimeoutError) as err:
            _LOGGER.warning("Could not summarize with %s: %s", entity, err)
            return message
        summary = (result or {}).get("data")
        return summary.strip() if isinstance(summary, str) and summary.strip() else message

    async def _async_broadcast(self, title: str, message: str) -> None:
        """Send a briefing or review over all configured channels."""
        message = await self._async_summarize(message)
        await self._async_speak(self._alexa_targets(None), message)
        if self._options.get(CONF_NOTIFY_ENABLED, True):
            for service in self._options.get(CONF_REMINDER_NOTIFY) or []:
                await self._async_send(service, title, message, None)

    async def _async_save_state(self) -> None:
        """Remember what has been sent, across restarts."""
        await self._state.async_save(
            {
                "last_digest": self._last_digest.isoformat()
                if self._last_digest
                else "",
                "last_review": self._last_review.isoformat()
                if self._last_review
                else "",
                "last_lists": self._last_lists,
                "last_list_zones": self._last_list_zones,
            }
        )

    @staticmethod
    def _is_scheduled_now(
        now: datetime,
        scheduled: time | None,
        last_sent: date | None,
        limit: timedelta = LATE_SCHEDULE_LIMIT,
    ) -> bool:
        """Return whether a daily schedule is due, but not hours late."""
        if scheduled is None or last_sent == now.date():
            return False
        planned = now.replace(
            hour=scheduled.hour, minute=scheduled.minute, second=0, microsecond=0
        )
        return planned <= now < planned + limit

    def build_digest(self, now: datetime) -> str | None:
        """Return the briefing of what is due today, None if nothing is."""
        due_today = []
        for idea in self._ideas.ideas:
            if idea.get("status") != "active" or not idea.get(ATTR_DUE):
                continue
            due = dt_util.parse_datetime(idea[ATTR_DUE])
            if due is not None and dt_util.as_local(due).date() <= now.date():
                due_today.append(str(idea.get(ATTR_TEXT)))
        if not due_today:
            return None
        if len(due_today) == 1:
            return f"Heute steht an: {due_today[0]}."
        joined = f"{', '.join(due_today[:-1])} und {due_today[-1]}"
        return f"Heute stehen {len(due_today)} Dinge an: {joined}."

    def build_review(self, now: datetime) -> str | None:
        """Return the review of long open ideas, None if there are none."""
        days = int(self._options.get(CONF_REVIEW_DAYS, DEFAULT_REVIEW_DAYS))
        limit = now - timedelta(days=days)
        stale = []
        for idea in self._ideas.ideas:
            if idea.get("status") != "active":
                continue
            created = dt_util.parse_datetime(idea.get(ATTR_CREATED_AT) or "")
            if created is not None and created < limit:
                stale.append((created, str(idea.get(ATTR_TEXT))))
        if not stale:
            return None
        stale.sort(key=lambda entry: entry[0])
        oldest = [text for _, text in stale[:REVIEW_MAX_ITEMS]]
        joined = ", ".join(oldest)
        count = len(stale)
        return (
            f"Wochenrückblick: {count} Einträge sind seit über {days} Tagen offen. "
            f"Die ältesten sind: {joined}. Kann davon etwas weg?"
        )

    def _someone_present(self) -> bool:
        """Return whether a chosen presence sensor reports someone."""
        return any(
            (state := self.hass.states.get(entity)) is not None
            and state.state in PRESENT_STATES
            for entity in self._options.get(CONF_DIGEST_PRESENCE) or []
        )

    async def _async_check_digest(self, now: datetime) -> None:
        """Send the daily briefing once, optionally only when someone is there."""
        if not self._options.get(CONF_DIGEST_ENABLED):
            return
        scheduled = _parse_time(self._options.get(CONF_DIGEST_TIME))
        if self._options.get(CONF_DIGEST_PRESENCE):
            if not self._someone_present() or not self._is_scheduled_now(
                now, scheduled, self._last_digest, PRESENCE_SCHEDULE_LIMIT
            ):
                return
        elif not self._is_scheduled_now(now, scheduled, self._last_digest):
            return
        self._last_digest = now.date()
        await self._async_save_state()
        if message := self.build_digest(now):
            await self._async_broadcast("Brainstorm: Heute", message)

    async def _async_check_review(self, now: datetime) -> None:
        """Send the weekly review once."""
        if (
            not self._options.get(CONF_REVIEW_ENABLED)
            or str(now.weekday()) != str(self._options.get(CONF_REVIEW_WEEKDAY, "6"))
            or not self._is_scheduled_now(
                now,
                _parse_time(self._options.get(CONF_REVIEW_TIME)),
                self._last_review,
            )
        ):
            return
        self._last_review = now.date()
        await self._async_save_state()
        if message := self.build_review(now):
            await self._async_broadcast("Brainstorm: Wochenrückblick", message)


@callback
def _is_person_event(event_data: dict[str, Any]) -> bool:
    """Return whether a state change belongs to a person."""
    return str(event_data.get("entity_id", "")).startswith("person.")
