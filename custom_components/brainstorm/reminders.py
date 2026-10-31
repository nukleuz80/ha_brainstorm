"""Proactive reminders, daily briefing and weekly review for Brainstorm Hub."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_CATEGORY,
    ATTR_CREATED_AT,
    ATTR_DEVICE,
    ATTR_DUE,
    ATTR_ESCALATED,
    ATTR_ID,
    ATTR_PRIORITY,
    ATTR_REMINDED_AT,
    ATTR_TEXT,
    CONF_DIGEST_ENABLED,
    CONF_DIGEST_TIME,
    CONF_QUIET_END,
    CONF_QUIET_START,
    CONF_REMINDER_ALEXA,
    CONF_REMINDER_DELAY,
    CONF_REMINDER_ECHOS,
    CONF_REMINDER_NOTIFY,
    CONF_REVIEW_DAYS,
    CONF_REVIEW_ENABLED,
    CONF_REVIEW_TIME,
    CONF_REVIEW_WEEKDAY,
    DEFAULT_REVIEW_DAYS,
    EVENT_REMINDER_DUE,
    PRIORITY_URGENT,
    REMINDER_ALEXA_FIXED,
    REMINDER_ALEXA_OFF,
    REMINDER_ALEXA_ORIGIN,
    REMINDERS_STORAGE_KEY,
    REMINDERS_STORAGE_VERSION,
)

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

CHECK_INTERVAL = timedelta(seconds=30)
LATE_SCHEDULE_LIMIT = timedelta(hours=2)
REVIEW_MAX_ITEMS = 5
ACTION_PREFIX = "BRAINSTORM_"
ACTION_DONE = "DONE"
ACTION_SNOOZE = "SNOOZE"
ACTION_TOMORROW = "TOMORROW"
TOMORROW_TIME = time(9, 0)


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


class ReminderManager:
    """Deliver due ideas over the channels this installation has set up."""

    def __init__(
        self, hass: HomeAssistant, store: BrainstormStore, options: dict[str, Any]
    ) -> None:
        """Initialize the manager."""
        self.hass = hass
        self._ideas = store
        self._options = options
        self._state: Store[dict[str, str]] = Store(
            hass, REMINDERS_STORAGE_VERSION, REMINDERS_STORAGE_KEY
        )
        self._last_digest: date | None = None
        self._last_review: date | None = None
        self._unsubs: list[CALLBACK_TYPE] = []

    @property
    def _notify_services(self) -> list[str]:
        """Return the configured notify services."""
        return list(self._options.get(CONF_REMINDER_NOTIFY) or [])

    @property
    def _alexa_mode(self) -> str:
        """Return how Alexa is used for reminders."""
        return self._options.get(CONF_REMINDER_ALEXA, REMINDER_ALEXA_OFF)

    async def async_start(self) -> None:
        """Start watching for due ideas."""
        data = await self._state.async_load() or {}
        self._last_digest = dt_util.parse_date(data.get("last_digest") or "")
        self._last_review = dt_util.parse_date(data.get("last_review") or "")
        self._unsubs = [
            async_track_time_interval(
                self.hass, self._async_tick, CHECK_INTERVAL, cancel_on_shutdown=True
            ),
            self.hass.bus.async_listen(
                "mobile_app_notification_action", self._async_handle_action
            ),
        ]

    @callback
    def async_stop(self) -> None:
        """Stop watching for due ideas."""
        while self._unsubs:
            self._unsubs.pop()()

    async def _async_tick(self, now: datetime) -> None:
        """Deliver whatever is due."""
        await self.async_check(dt_util.now())

    async def async_check(self, now: datetime) -> None:
        """Deliver due reminders, follow-ups, briefing and review."""
        quiet = is_quiet_time(
            now,
            _parse_time(self._options.get(CONF_QUIET_START)),
            _parse_time(self._options.get(CONF_QUIET_END)),
        )
        for idea in self._ideas.ideas:
            if idea.get("status") != "active" or not idea.get(ATTR_DUE):
                continue
            due = dt_util.parse_datetime(idea[ATTR_DUE])
            if due is None or due > now:
                continue
            await self._async_process_due_idea(idea, now, quiet)
        if not quiet:
            await self._async_check_digest(now)
            await self._async_check_review(now)

    async def _async_process_due_idea(
        self, idea: dict[str, Any], now: datetime, quiet: bool
    ) -> None:
        """Send the first reminder or its follow-up on the phone."""
        urgent = idea.get(ATTR_PRIORITY) == PRIORITY_URGENT
        reminded_at = idea.get(ATTR_REMINDED_AT)
        if not reminded_at:
            # Quiet hours hold everything back, only urgent ideas reach the phone
            if quiet and not urgent:
                return
            self.hass.bus.async_fire(
                EVENT_REMINDER_DUE,
                {
                    ATTR_ID: idea[ATTR_ID],
                    ATTR_TEXT: idea.get(ATTR_TEXT),
                    ATTR_CATEGORY: idea.get(ATTR_CATEGORY),
                    ATTR_PRIORITY: idea.get(ATTR_PRIORITY),
                    ATTR_DEVICE: idea.get(ATTR_DEVICE),
                    ATTR_DUE: idea.get(ATTR_DUE),
                },
            )
            alexa_ok = False if quiet else await self._async_speak_reminder(idea)
            send_now = (
                not alexa_ok or int(self._options.get(CONF_REMINDER_DELAY, 0)) == 0
            )
            if send_now:
                await self._async_notify_idea(idea)
            await self._ideas.async_mark_reminded(idea[ATTR_ID], escalated=send_now)
            return

        if idea.get(ATTR_ESCALATED) or (quiet and not urgent):
            return
        delay = timedelta(minutes=int(self._options.get(CONF_REMINDER_DELAY, 0)))
        sent = dt_util.parse_datetime(reminded_at)
        if sent is None or sent + delay > now:
            return
        await self._async_notify_idea(idea)
        await self._ideas.async_mark_reminded(idea[ATTR_ID], escalated=True)

    def _echo_entity_from_name(self, name: str | None) -> str | None:
        """Find the Echo of an idea by the name stored with it."""
        if not name:
            return None
        for state in self.hass.states.async_all("media_player"):
            if state.attributes.get("friendly_name") == name:
                return state.entity_id
        return None

    def _alexa_targets(self, idea: dict[str, Any] | None) -> list[str]:
        """Return the Echos to speak on, following the chosen mode."""
        mode = self._alexa_mode
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
        return await self._async_speak(
            self._alexa_targets(idea), f"Erinnerung: {idea.get(ATTR_TEXT)}."
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

    async def _async_notify_idea(self, idea: dict[str, Any]) -> None:
        """Send a reminder to the phones and other services."""
        idea_id = idea[ATTR_ID]
        for service in self._notify_services:
            data = None
            # Only the companion app understands buttons
            if service.startswith("notify.mobile_app_"):
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

    async def _async_broadcast(self, title: str, message: str) -> None:
        """Send a briefing or review over all configured channels."""
        await self._async_speak(self._alexa_targets(None), message)
        for service in self._notify_services:
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
            }
        )

    @staticmethod
    def _is_scheduled_now(
        now: datetime, scheduled: time | None, last_sent: date | None
    ) -> bool:
        """Return whether a daily schedule is due, but not hours late."""
        if scheduled is None or last_sent == now.date():
            return False
        planned = now.replace(
            hour=scheduled.hour, minute=scheduled.minute, second=0, microsecond=0
        )
        return planned <= now < planned + LATE_SCHEDULE_LIMIT

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

    async def _async_check_digest(self, now: datetime) -> None:
        """Send the daily briefing once."""
        if not self._options.get(CONF_DIGEST_ENABLED) or not self._is_scheduled_now(
            now, _parse_time(self._options.get(CONF_DIGEST_TIME)), self._last_digest
        ):
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
