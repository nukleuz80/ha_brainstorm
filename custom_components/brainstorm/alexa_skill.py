"""Connection between a user's own Alexa skill and Brainstorm Hub."""
from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from datetime import timedelta
import json
import logging
import re
import secrets
import time
from typing import TYPE_CHECKING, Any

from aiohttp import hdrs, web

from homeassistant.components import webhook
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import entity_sources
from homeassistant.helpers.network import get_url
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_ALEXA_NATIVE,
    ATTR_CATEGORY,
    ATTR_ID,
    ATTR_TEXT,
    CONF_NATIVE_REMINDERS,
    CONF_REMINDERS_ENABLED,
    DOMAIN,
    SKILL_STORAGE_KEY,
    SKILL_STORAGE_VERSION,
)
from .reminders import ZONE_HOME, ReminderRequest, build_reminder_request, format_due

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

MAX_TEXT_LENGTH = 500
MAX_SPEECH_LENGTH = 7900
MIN_IDEA_LENGTH = 3

# The skill code gives up after 6 seconds, so an unknown Echo must not take longer
DEVICE_WAIT_SECONDS = 3.5
ALEXA_EVENT_MAX_AGE_SECONDS = 30
ALEXA_MEDIA_DOMAIN = "alexa_media"
EVENT_LAST_CALLED = "alexa_media_last_called_event"

ACTION_CAPTURE = "capture"
ACTION_READ = "read"
ACTION_READ_ALL = "read_all"
ACTION_LAUNCH = "launch"
ACTION_REMIND = "remind"
ACTION_DONE = "done"
ACTION_SNOOZE = "snooze"
ACTION_NATIVE_CONFIRM = "native_confirm"
ACTIONS = (
    ACTION_NATIVE_CONFIRM,
    ACTION_CAPTURE,
    ACTION_READ,
    ACTION_READ_ALL,
    ACTION_LAUNCH,
    ACTION_REMIND,
    ACTION_DONE,
    ACTION_SNOOZE,
)
SNOOZE_TIME = timedelta(hours=1)

# Same words as the native voice capture, tried in this order
_TEXT_PREFIXES = (
    "setze auf meine einkaufsliste ",
    "setz auf meine einkaufsliste ",
    "setze auf die einkaufsliste ",
    "setz auf die einkaufsliste ",
    "setze auf meine to-do-liste ",
    "setz auf meine to-do-liste ",
    "setze auf die to-do-liste ",
    "setz auf die to-do-liste ",
    "setze auf meine todoliste ",
    "setz auf meine todoliste ",
    "setze auf meine liste ",
    "setz auf meine liste ",
    "setze auf die liste ",
    "setz auf die liste ",
    "packe auf meine liste ",
    "pack auf meine liste ",
    "schreibe auf meine liste ",
    "schreib auf meine liste ",
    "setze ",
    "setz ",
    "packe ",
    "pack ",
    "schreibe ",
    "schreib ",
    "erinnere mich an ",
    "erinnere mich ",
    "erinnere ",
    "neue idee für den ",
    "neue idee für das ",
    "neue idee für die ",
    "neue idee für ",
    "neue idee ",
    "idee für den ",
    "idee für das ",
    "idee für die ",
    "idee für ",
    "idee ",
    "notiz für den ",
    "notiz für das ",
    "notiz für die ",
    "notiz für ",
    "notiz ",
    "notiere für den ",
    "notiere für das ",
    "notiere für die ",
    "notiere für ",
    "notiere ",
    "merke dir für den ",
    "merke dir für ",
    "merke dir ",
    "merke ",
    "brainstorm ",
    # Alexa has already removed the command word from the skill's text
    "für den ",
    "für das ",
    "für die ",
    "für ",
)
_TEXT_SUFFIXES = (
    " auf meine einkaufsliste",
    " auf die einkaufsliste",
    " auf meine to do liste",
    " auf die to do liste",
    " auf meine liste",
    " auf die liste",
    " auf meine to-do-liste",
    " auf die to-do-liste",
    " auf meine todoliste",
    " auf die todoliste",
)

INTERACTION_MODEL: dict[str, Any] = {
    "interactionModel": {
        "languageModel": {
            "invocationName": "brainstorm",
            "intents": [
                {
                    "name": "CaptureIdeaIntent",
                    "slots": [{"name": "text", "type": "AMAZON.SearchQuery"}],
                    "samples": [
                        "notiere {text}",
                        "notier {text}",
                        "notiz {text}",
                        "neue notiz {text}",
                        "idee {text}",
                        "neue idee {text}",
                        "eintrag {text}",
                        "neuer eintrag {text}",
                        "merke dir {text}",
                        "merke {text}",
                        "setze {text}",
                        "setz {text}",
                        "packe {text}",
                        "pack {text}",
                        "schreibe {text}",
                        "schreib {text}",
                        "schreib auf {text}",
                    ],
                },
                {
                    "name": "ReminderIntent",
                    "slots": [{"name": "text", "type": "AMAZON.SearchQuery"}],
                    "samples": [
                        "erinnere mich an {text}",
                        "erinnere mich {text}",
                        "erinnere {text}",
                        "termin {text}",
                    ],
                },
                {
                    "name": "DoneIntent",
                    "slots": [{"name": "text", "type": "AMAZON.SearchQuery"}],
                    "samples": [
                        "erledigt",
                        "ist erledigt",
                        "fertig",
                        "erledigt {text}",
                        "hake ab {text}",
                        "fertig mit {text}",
                    ],
                },
                {
                    "name": "SnoozeIntent",
                    "samples": ["später", "später erinnern", "nochmal später"],
                },
                {
                    "name": "ReadAllIdeasIntent",
                    "samples": [
                        "alle einträge",
                        "alle notizen",
                        "alles vorlesen",
                        "notizen vorlesen",
                    ],
                },
                {
                    "name": "ReadIdeasIntent",
                    "slots": [{"name": "category", "type": "AMAZON.SearchQuery"}],
                    "samples": [
                        "ansage",
                        "vorlesen",
                        "abfragen",
                        "abhören",
                        "was steht drin",
                        "ansage für {category}",
                        "ansage {category}",
                        "lies {category}",
                        "lies vor {category}",
                        "kategorie {category}",
                    ],
                },
                {"name": "AMAZON.CancelIntent", "samples": []},
                {"name": "AMAZON.HelpIntent", "samples": []},
                {"name": "AMAZON.StopIntent", "samples": []},
                {"name": "AMAZON.NavigateHomeIntent", "samples": []},
                {"name": "AMAZON.FallbackIntent", "samples": []},
            ],
            "types": [],
        }
    }
}

# Kept small on purpose, so that improvements reach users through the integration
SKILL_CODE_TEMPLATE = '''"""Brainstorm Hub Alexa skill. Keep this code private, it contains your secret address."""
import json
import urllib.error
import urllib.request

WEBHOOK_URL = "__WEBHOOK_URL__"
TIMEOUT_SECONDS = 6
REMINDER_API_TIMEOUT_SECONDS = 2
HELP_TEXT = "Sage zum Beispiel: notiere Kellerlicht dimmen, erinnere mich morgen um 8 an die Tonnen, oder Ansage Alltag."


def _response(text, end_session=True):
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": end_session,
        },
    }


def _call_home_assistant(event, action, text=""):
    system = event["context"]["System"]
    payload = {
        "application_id": system["application"]["applicationId"],
        "device_id": system.get("device", {}).get("deviceId"),
        "action": action,
        "text": text,
    }
    request = urllib.request.Request(
        WEBHOOK_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as reply:
            body = reply.read().decode()
            data = json.loads(body) if body else {}
    except (urllib.error.URLError, TimeoutError, ValueError):
        return _response("Home Assistant ist nicht erreichbar. Es wurde nichts gespeichert.")
    if data.get("silent"):
        return {"version": "1.0", "response": {"shouldEndSession": True}}
    if not data.get("speech"):
        return _response("Der Skill-Modus ist in Brainstorm nicht aktiv. Es wurde nichts gespeichert.")
    answer = _response(data["speech"], data.get("end_session", True))
    if data.get("alexa_reminder"):
        _add_alexa_reminder(event, data["alexa_reminder"], answer)
    return answer


def _add_alexa_reminder(event, reminder, answer):
    """Also create a real Alexa reminder, keeping the Home Assistant one on any problem."""
    system = event["context"]["System"]
    body = {
        "requestTime": event["request"]["timestamp"],
        "trigger": {
            "type": "SCHEDULED_ABSOLUTE",
            "scheduledTime": reminder["time"],
            "timeZoneId": reminder["time_zone"],
        },
        "alertInfo": {
            "spokenInfo": {"content": [{"locale": event["request"]["locale"], "text": reminder["text"]}]}
        },
        "pushNotification": {"status": "ENABLED"},
    }
    request = urllib.request.Request(
        system["apiEndpoint"] + "/v1/alerts/reminders",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + system.get("apiAccessToken", ""),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=REMINDER_API_TIMEOUT_SECONDS):
            pass
    except urllib.error.HTTPError as err:
        if err.code in (401, 403):
            answer["response"]["card"] = {
                "type": "AskForPermissionsConsent",
                "permissions": ["alexa::alerts:reminders:skill:readwrite"],
            }
        return
    except (urllib.error.URLError, TimeoutError):
        return
    _call_home_assistant(event, "native_confirm", reminder["id"])


def lambda_handler(event, context):
    request = event["request"]
    if request["type"] == "LaunchRequest":
        return _call_home_assistant(event, "launch")
    if request["type"] == "SessionEndedRequest":
        return {"version": "1.0", "response": {}}

    intent = request.get("intent", {})
    slots = intent.get("slots", {})
    if intent.get("name") == "CaptureIdeaIntent":
        text = slots.get("text", {}).get("value")
        if text:
            return _call_home_assistant(event, "capture", text)
        return _response("Ich habe keinen Text verstanden.")
    if intent.get("name") == "ReminderIntent":
        return _call_home_assistant(event, "remind", slots.get("text", {}).get("value") or "")
    if intent.get("name") == "DoneIntent":
        return _call_home_assistant(event, "done", slots.get("text", {}).get("value") or "")
    if intent.get("name") == "SnoozeIntent":
        return _call_home_assistant(event, "snooze")
    if intent.get("name") == "ReadIdeasIntent":
        return _call_home_assistant(event, "read", slots.get("category", {}).get("value") or "")
    if intent.get("name") == "ReadAllIdeasIntent":
        return _call_home_assistant(event, "read_all")
    if intent.get("name") in ("AMAZON.HelpIntent", "AMAZON.FallbackIntent"):
        return _response(HELP_TEXT, False)
    return _response("Okay.")
'''


def clean_voice_text(text: str) -> str:
    """Remove command words and list names, like the native voice capture."""
    cleaned = text.strip()
    for prefix in _TEXT_PREFIXES:
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix) :]
    for suffix in _TEXT_SUFFIXES:
        if cleaned.lower().endswith(suffix):
            cleaned = cleaned[: -len(suffix)]
    return cleaned.strip()


def _normalize(text: str) -> str:
    """Reduce a sentence to its letters and digits for comparing."""
    return re.sub(r"[\W_]+", "", text.lower())


def _is_same_sentence(text: str, summary: str) -> bool:
    """Return whether the Alexa history entry belongs to the skill's text."""
    normalized = _normalize(summary)
    return "brainstorm" in normalized and _normalize(text) in normalized


@dataclass
class EchoDevice:
    """An Echo known to Home Assistant."""

    name: str
    entity_id: str | None = None


@dataclass
class _PendingRequest:
    """A skill request that is waiting for its Alexa history entry."""

    device_id: str
    text: str
    future: asyncio.Future[EchoDevice]
    created: float = field(default_factory=time.monotonic)
    idea_id: str | None = None
    used_device: EchoDevice | None = None


class AlexaSkill:
    """Accept ideas from the Alexa skill the user built for this installation."""

    def __init__(self, hass: HomeAssistant, store: BrainstormStore) -> None:
        """Initialize the skill connection."""
        self.hass = hass
        self._ideas = store
        self._store: Store[dict[str, Any]] = Store(
            hass, SKILL_STORAGE_VERSION, SKILL_STORAGE_KEY
        )
        self._webhook_id = ""
        self._application_id: str | None = None
        self._devices: dict[str, dict[str, str | None]] = {}
        self._active = False
        self._unsub_events: Any = None
        self._recent_events: deque[tuple[float, str, str]] = deque(maxlen=20)
        self._pending: list[_PendingRequest] = []
        self.last_request: dict[str, str] | None = None

    @property
    def is_linked(self) -> bool:
        """Return whether a skill has been linked to this installation."""
        return self._application_id is not None

    async def async_load(self) -> None:
        """Load the stored secret, skill link and known Echos."""
        data = await self._store.async_load() or {}
        self._webhook_id = data.get("webhook_id", "")
        self._application_id = data.get("application_id")
        self._devices = data.get("devices", {})
        if not self._webhook_id:
            await self._async_new_webhook_id()

    async def _async_save(self) -> None:
        """Persist the secret, skill link and known Echos."""
        await self._store.async_save(
            {
                "webhook_id": self._webhook_id,
                "application_id": self._application_id,
                "devices": self._devices,
            }
        )

    async def _async_new_webhook_id(self) -> None:
        """Create a new secret, which invalidates the old skill code."""
        self._webhook_id = f"brainstorm_{secrets.token_hex(24)}"
        self._application_id = None
        self._devices = {}
        await self._async_save()

    @callback
    def async_start(self) -> None:
        """Start accepting requests from the skill."""
        webhook.async_register(
            self.hass,
            DOMAIN,
            "Brainstorm Alexa Skill",
            self._webhook_id,
            self._async_handle_webhook,
            local_only=False,
            allowed_methods=[hdrs.METH_POST],
        )
        self._unsub_events = self.hass.bus.async_listen(
            EVENT_LAST_CALLED, self._async_handle_last_called
        )
        self._active = True

    @callback
    def async_stop(self) -> None:
        """Stop accepting requests from the skill."""
        if self._active:
            webhook.async_unregister(self.hass, self._webhook_id)
            self._unsub_events()
            self._active = False
        for pending in self._pending:
            pending.future.cancel()
        self._pending.clear()

    async def async_reset(self) -> None:
        """Replace the secret and remove the skill link."""
        was_active = self._active
        self.async_stop()
        await self._async_new_webhook_id()
        self.last_request = None
        if was_active:
            self.async_start()

    def get_skill_code(self) -> str:
        """Return the skill code with this installation's public address.

        Raises NoURLAvailableError if Home Assistant has no public HTTPS address.
        """
        # webhook.async_generate_url() excludes Home Assistant Cloud addresses
        base_url = get_url(
            self.hass, allow_internal=False, allow_ip=False, require_ssl=True
        )
        url = f"{base_url}{webhook.async_generate_path(self._webhook_id)}"
        return SKILL_CODE_TEMPLATE.replace("__WEBHOOK_URL__", url)

    @staticmethod
    def get_interaction_model() -> str:
        """Return the voice model for the Alexa developer console."""
        return json.dumps(INTERACTION_MODEL, indent=2, ensure_ascii=False)

    def _echo_from_name(self, name: str) -> EchoDevice:
        """Find the media player of an Echo by its Alexa name."""
        sources = entity_sources(self.hass)
        for state in self.hass.states.async_all("media_player"):
            source = sources.get(state.entity_id)
            if (
                source is not None
                and source["domain"] == ALEXA_MEDIA_DOMAIN
                and state.attributes.get("friendly_name") == name
            ):
                return EchoDevice(name, state.entity_id)
        return EchoDevice(name)

    @callback
    def _async_learn_device(self, device_id: str, echo: EchoDevice) -> None:
        """Remember which Echo the skill's device id stands for."""
        known = {"name": echo.name, "entity_id": echo.entity_id}
        if self._devices.get(device_id) != known:
            self._devices[device_id] = known
            self.hass.async_create_task(self._async_save())

    @callback
    def _async_handle_last_called(self, event: Event) -> None:
        """Match an Alexa history entry to a skill request."""
        name = event.data.get("name")
        summary = str(event.data.get("summary") or "")
        if not name or "brainstorm" not in _normalize(summary):
            return

        now = time.monotonic()
        self._pending = [
            pending
            for pending in self._pending
            if now - pending.created < ALEXA_EVENT_MAX_AGE_SECONDS
        ]
        pending = next(
            (p for p in self._pending if _is_same_sentence(p.text, summary)), None
        )
        if pending is None:
            self._recent_events.append((now, name, summary))
            return

        self._pending.remove(pending)
        echo = self._echo_from_name(name)
        self._async_learn_device(pending.device_id, echo)
        if not pending.future.done():
            pending.future.set_result(echo)
        # The idea was stored before Alexa reported the Echo, or with an outdated one
        if pending.idea_id and (
            pending.used_device is None or pending.used_device.name != echo.name
        ):
            self.hass.async_create_task(
                self._ideas.async_update_idea(pending.idea_id, device=echo.name)
            )

    async def _async_resolve_echo(
        self, device_id: str | None, text: str
    ) -> tuple[EchoDevice | None, _PendingRequest | None]:
        """Return the Echo of a request, waiting for it only if it is still unknown."""
        if not device_id:
            return None, None

        now = time.monotonic()
        for entry in self._recent_events:
            if (
                now - entry[0] < ALEXA_EVENT_MAX_AGE_SECONDS
                and _is_same_sentence(text, entry[2])
            ):
                self._recent_events.remove(entry)
                echo = self._echo_from_name(entry[1])
                self._async_learn_device(device_id, echo)
                return echo, None

        pending = _PendingRequest(
            device_id, text, self.hass.loop.create_future()
        )
        self._pending.append(pending)
        if known := self._devices.get(device_id):
            # The name may have changed since Alexa reported this Echo
            name = str(known["name"])
            echo = self._echo_from_name(name)
            pending.used_device = echo
            return echo, pending

        try:
            echo = await asyncio.wait_for(
                asyncio.shield(pending.future), DEVICE_WAIT_SECONDS
            )
        except TimeoutError:
            return None, pending
        return echo, None

    def _speech(
        self, german: str, english: str, end_session: bool = True
    ) -> web.Response:
        """Return text for Alexa to speak."""
        is_german = self.hass.config.language.startswith("de")
        return web.json_response(
            {"speech": german if is_german else english, "end_session": end_session}
        )

    def _category_from_speech(self, spoken: str) -> str | None:
        """Find the category a spoken request is about, None meaning all."""
        spoken = spoken.lower()
        for category in self._ideas.categories:
            for word in re.split(r"\W+", category.lower()):
                if len(word) >= 4 and word in spoken:
                    return category
        return None

    async def _async_capture(
        self,
        text: str,
        echo: EchoDevice | None,
        pending: _PendingRequest | None,
        request: ReminderRequest | None = None,
        no_time_found: bool = False,
    ) -> web.Response:
        """Store an idea and report where it went."""
        cleaned = clean_voice_text(text)[:MAX_TEXT_LENGTH]
        if len(cleaned) < MIN_IDEA_LENGTH:
            return self._speech(
                "Ich habe keinen Text verstanden.", "I did not understand any text."
            )
        try:
            idea = await self._ideas.async_add_idea(
                text=cleaned,
                source="alexa_skill",
                device=echo.name if echo else None,
                due=request.due if request else None,
                assignee=request.assignee if request else None,
                trigger=request.trigger if request else None,
            )
        except HomeAssistantError as err:
            _LOGGER.warning("Could not store idea from Alexa skill: %s", err)
            return self._speech(
                "Das konnte ich nicht speichern.", "I could not save that."
            )

        if pending is not None:
            pending.idea_id = idea.get("id")
        self.last_request = {
            "time": dt_util.now().strftime("%d.%m.%Y %H:%M:%S"),
            "text": idea.get("text", ""),
            "device": echo.name if echo else "?",
        }
        if request is not None:
            return self._reminder_answer(request, idea)
        if no_time_found:
            return self._speech(
                "Gespeichert, aber ohne Erinnerung. Ich habe keinen Zeitpunkt verstanden.",
                "Saved, but without a reminder. I did not understand a time.",
            )
        category = idea.get(ATTR_CATEGORY)
        if category and category != "Inbox":
            return self._speech(
                f"Gespeichert unter {category.replace('&', 'und')}.",
                f"Saved under {category.replace('&', 'and')}.",
            )
        return self._speech("Gespeichert.", "Saved.")

    def _reminder_answer(
        self, request: ReminderRequest, idea: dict[str, Any]
    ) -> web.Response:
        """Confirm a reminder, and pass on what a real Alexa reminder would need."""
        now = dt_util.now()
        when = format_due(request.due, now) if request.due else self._place_name(request)
        who = self._person_name(request.assignee) or "dich"
        text = idea.get(ATTR_TEXT)
        speech = f"Okay, ich erinnere {who} {when} an {text}."
        data: dict[str, Any] = {"speech": speech, "end_session": True}
        # Only the person speaking can get a real reminder, and only for a set time
        if (
            self._ideas.options.get(CONF_NATIVE_REMINDERS)
            and request.due
            and not request.assignee
        ):
            local_due = dt_util.as_local(request.due)
            data["alexa_reminder"] = {
                "id": idea[ATTR_ID],
                "text": text,
                "time": local_due.strftime("%Y-%m-%dT%H:%M:%S"),
                "time_zone": self.hass.config.time_zone,
            }
        return web.json_response(data)

    def _person_name(self, entity_id: str | None) -> str | None:
        """Return the name of a person."""
        state = self.hass.states.get(entity_id) if entity_id else None
        return state.name if state else None

    def _place_name(self, request: ReminderRequest) -> str:
        """Say where a reminder is meant for."""
        zone = (request.trigger or {}).get("zone")
        if zone == ZONE_HOME:
            return "beim Heimkommen"
        state = self.hass.states.get(zone) if zone else None
        return f"bei {state.name}" if state else "an diesem Ort"

    async def _async_remind(
        self, text: str, echo: EchoDevice | None, pending: _PendingRequest | None
    ) -> web.Response:
        """Store an idea with the spoken time or place as its reminder."""
        options = self._ideas.options
        if not options.get(CONF_REMINDERS_ENABLED, True):
            response = await self._async_capture(text, echo, pending)
            if response.status != 200:
                return response
            return self._speech(
                "Gespeichert, aber Erinnerungen sind ausgeschaltet.",
                "Saved, but reminders are switched off.",
            )
        now = dt_util.now()
        request = build_reminder_request(
            self.hass, options, clean_voice_text(text), now
        )
        if request.due is None and request.trigger is None:
            return await self._async_capture(text, echo, pending, no_time_found=True)
        if request.due is not None and request.due <= now:
            return self._speech(
                "Dieser Zeitpunkt liegt in der Vergangenheit.",
                "That time is in the past.",
            )
        return await self._async_capture(
            request.text, echo, pending, request=request
        )

    async def _async_done(self, text: str) -> web.Response:
        """Complete the idea a person named, or the last one reminded of."""
        cleaned = text.strip()
        idea = (
            self._ideas.find_open_idea(cleaned)
            if cleaned
            else self._ideas.last_reminded_idea()
        )
        if idea is None:
            return self._speech(
                "Diesen Eintrag habe ich nicht gefunden.", "I could not find that idea."
            )
        await self._ideas.async_update_idea(idea[ATTR_ID], status="completed")
        return self._speech(
            f"Erledigt: {idea.get(ATTR_TEXT)}.", f"Done: {idea.get(ATTR_TEXT)}."
        )

    async def _async_snooze(self) -> web.Response:
        """Move the last reminder one hour ahead."""
        idea = self._ideas.last_reminded_idea()
        if idea is None:
            return self._speech(
                "Es gibt gerade keine Erinnerung zum Verschieben.",
                "There is no reminder to move.",
            )
        due = dt_util.now() + SNOOZE_TIME
        await self._ideas.async_set_due(idea[ATTR_ID], due)
        when = format_due(due, dt_util.now())
        return self._speech(
            f"Okay, ich erinnere dich {when} wieder.", f"Okay, again {when}."
        )

    async def _async_handle_webhook(
        self, hass: HomeAssistant, webhook_id: str, request: web.Request
    ) -> web.Response:
        """Handle a request from the skill."""
        try:
            payload = await request.json()
        except ValueError:
            return web.Response(status=400)
        if not isinstance(payload, dict):
            return web.Response(status=400)

        application_id = payload.get("application_id")
        action = payload.get("action", ACTION_CAPTURE)
        text = payload.get("text", None if action == ACTION_CAPTURE else "")
        device_id = payload.get("device_id")
        if (
            not isinstance(application_id, str)
            or not application_id
            or action not in ACTIONS
            or not isinstance(text, str)
            or not isinstance(device_id, str | None)
        ):
            return web.Response(status=400)

        # The first skill to call the secret address becomes the linked one
        if self._application_id is None:
            self._application_id = application_id
            await self._async_save()
        elif application_id != self._application_id:
            _LOGGER.warning("Rejected a request from an unknown Alexa skill")
            return web.Response(status=403)

        if action == ACTION_NATIVE_CONFIRM:
            await self._ideas.async_mark_fields(text, {ATTR_ALEXA_NATIVE: True})
            return web.json_response({"ok": True})

        echo, pending = await self._async_resolve_echo(device_id, text)

        # An unknown Echo is let through, so that an idea never gets lost
        allowed = self._ideas.allowed_echos
        if allowed and echo and echo.entity_id and echo.entity_id not in allowed:
            if pending is not None:
                pending.future.cancel()
                self._pending.remove(pending)
            return web.json_response({"silent": True})

        if action == ACTION_LAUNCH:
            return self._speech(
                "Brainstorm bereit. Sage notiere und deine Notiz, oder sage Ansage.",
                "Brainstorm is ready. Say notiere and your note, or say Ansage.",
                end_session=False,
            )
        if action == ACTION_READ_ALL:
            speech = self._ideas.get_announcement_text()
            return self._speech(speech[:MAX_SPEECH_LENGTH], speech[:MAX_SPEECH_LENGTH])
        if action == ACTION_READ:
            category = self._category_from_speech(text)
            if category is None:
                # Reading everything is too long, so offer the categories instead
                speech = self._ideas.get_overview_text()
                return self._speech(speech, speech, end_session=False)
            speech = self._ideas.get_announcement_text(category)
            return self._speech(speech[:MAX_SPEECH_LENGTH], speech[:MAX_SPEECH_LENGTH])
        if action == ACTION_REMIND:
            return await self._async_remind(text, echo, pending)
        if action == ACTION_DONE:
            return await self._async_done(text)
        if action == ACTION_SNOOZE:
            return await self._async_snooze()
        return await self._async_capture(text, echo, pending)
