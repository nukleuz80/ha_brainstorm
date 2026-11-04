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

from homeassistant.components import persistent_notification, webhook
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.network import get_url
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .alexa_display import build_directive
from .const import (
    ATTR_ALEXA_NATIVE,
    ATTR_CATEGORY,
    ATTR_DUE,
    ATTR_ID,
    ATTR_OWNER,
    ATTR_STATUS,
    ATTR_TEXT,
    CONF_NATIVE_REMINDERS,
    CONF_REMINDERS_ENABLED,
    DOMAIN,
    SKILL_STORAGE_KEY,
    SKILL_STORAGE_VERSION,
)
from .languages import PACKS, get_pack
from .languages.common import LanguagePack
from .reminders import (
    ZONE_HOME,
    ReminderRequest,
    build_reminder_request,
    find_echo_entity,
    format_due,
)

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

MAX_TEXT_LENGTH = 500
MAX_SPEECH_LENGTH = 7900
MIN_IDEA_LENGTH = 3

# The skill code gives up after 6 seconds, so an unknown Echo must not take longer
DEVICE_WAIT_SECONDS = 3.5
ALEXA_EVENT_MAX_AGE_SECONDS = 30
# Alexa writes a sentence to its history only after the skill answered, so a
# sentence Alexa could not place is stored when that entry arrives, up to this long
FALLBACK_LATE_SECONDS = 60
FALLBACK_NOTIFICATION_ID = "brainstorm_skill_lost_sentence"
EVENT_LAST_CALLED = "alexa_media_last_called_event"

ACTION_CAPTURE = "capture"
ACTION_READ = "read"
ACTION_READ_ALL = "read_all"
ACTION_SHOW = "show"
ACTION_DISPLAY_DONE = "display_done"
ACTION_LAUNCH = "launch"
ACTION_REMIND = "remind"
ACTION_DONE = "done"
ACTION_SNOOZE = "snooze"
ACTION_NATIVE_CONFIRM = "native_confirm"
ACTION_FALLBACK = "fallback"
ACTIONS = (
    ACTION_NATIVE_CONFIRM,
    ACTION_CAPTURE,
    ACTION_READ,
    ACTION_READ_ALL,
    ACTION_SHOW,
    ACTION_DISPLAY_DONE,
    ACTION_LAUNCH,
    ACTION_REMIND,
    ACTION_DONE,
    ACTION_SNOOZE,
    ACTION_FALLBACK,
)
SNOOZE_TIME = timedelta(hours=1)
# What the skill has to be able to say without Home Assistant
SKILL_CODE_TEXTS = (
    "skill_unreachable",
    "skill_inactive",
    "skill_no_text",
    "skill_help",
)

# Kept small on purpose, so that improvements reach users through the integration
_SKILL_CODE = '''"""Brainstorm Hub Alexa skill. Keep this code private, it contains your secret address."""
import json
import urllib.error
import urllib.request

WEBHOOK_URL = "__WEBHOOK_URL__"
TIMEOUT_SECONDS = 6
REMINDER_API_TIMEOUT_SECONDS = 2
TEXTS = __TEXTS__


def _text(event, key):
    """Return a text in the language of the request, as Home Assistant may be down."""
    language = str(event["request"].get("locale") or "").split("-")[0]
    return TEXTS.get(language, TEXTS["en"])[key]


def _response(text, end_session=True):
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": end_session,
        },
    }


def _has_screen(event):
    device = event["context"]["System"].get("device", {})
    return "Alexa.Presentation.APL" in device.get("supportedInterfaces", {})


def _call_home_assistant(event, action, text=""):
    system = event["context"]["System"]
    payload = {
        "application_id": system["application"]["applicationId"],
        "device_id": system.get("device", {}).get("deviceId"),
        "action": action,
        "text": text,
        "display": _has_screen(event),
        "locale": event["request"].get("locale"),
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
        return _response(_text(event, "skill_unreachable"))
    if data.get("silent"):
        return {"version": "1.0", "response": {"shouldEndSession": True}}
    if not data.get("speech"):
        return _response(_text(event, "skill_inactive"))
    answer = _response(data["speech"], data.get("end_session", True))
    if data.get("directives"):
        answer["response"]["directives"] = data["directives"]
        # Not set, the screen stays and can be touched without an open microphone
        if data.get("end_session", True):
            del answer["response"]["shouldEndSession"]
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
    if request["type"] == "Alexa.Presentation.APL.UserEvent":
        arguments = request.get("arguments") or []
        if len(arguments) == 2 and arguments[0] == "done":
            return _call_home_assistant(event, "display_done", str(arguments[1]))
        return {"version": "1.0", "response": {}}
    if request["type"] != "IntentRequest":
        if request.get("errors"):
            print(json.dumps(request["errors"]))
        return {"version": "1.0", "response": {}}

    intent = request.get("intent", {})
    slots = intent.get("slots", {})
    if intent.get("name") == "CaptureIdeaIntent":
        text = slots.get("text", {}).get("value")
        if text:
            return _call_home_assistant(event, "capture", text)
        return _response(_text(event, "skill_no_text"))
    if intent.get("name") == "ReminderIntent":
        return _call_home_assistant(event, "remind", slots.get("text", {}).get("value") or "")
    if intent.get("name") == "DoneIntent":
        return _call_home_assistant(event, "done", slots.get("text", {}).get("value") or "")
    if intent.get("name") == "SnoozeIntent":
        return _call_home_assistant(event, "snooze")
    if intent.get("name") == "ReadIdeasIntent":
        return _call_home_assistant(event, "read", slots.get("category", {}).get("value") or "")
    if intent.get("name") == "ShowIdeasIntent":
        return _call_home_assistant(event, "show", slots.get("category", {}).get("value") or "")
    if intent.get("name") == "ReadAllIdeasIntent":
        return _call_home_assistant(event, "read_all")
    if intent.get("name") == "AMAZON.FallbackIntent":
        # Home Assistant takes the sentence from the Alexa history of the Echo
        return _call_home_assistant(event, "fallback")
    if intent.get("name") == "AMAZON.HelpIntent":
        return _response(_text(event, "skill_help"), False)
    return _response("Okay.")
'''
SKILL_CODE_TEMPLATE = _SKILL_CODE.replace(
    "__TEXTS__",
    repr(
        {
            code: {key: pack.messages[key] for key in SKILL_CODE_TEXTS}
            for code, pack in PACKS.items()
        }
    ),
)


def clean_voice_text(text: str, pack: LanguagePack) -> str:
    """Remove command words and list names, like the native voice capture."""
    cleaned = text.strip()
    for prefix in pack.voice_prefixes:
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix) :]
    for suffix in pack.voice_suffixes:
        if cleaned.lower().endswith(suffix):
            cleaned = cleaned[: -len(suffix)]
    return cleaned.strip()


def _normalize(text: str) -> str:
    """Reduce a sentence to its letters and digits for comparing."""
    return re.sub(r"[\W_]+", "", text.lower())


_INVOCATION = re.compile(
    r"^.*?\bbrainstorm\b[\s,.:;!?-]*(?:(?:dass|that)\b\s*)?",
    re.IGNORECASE | re.DOTALL,
)


def sentence_after_invocation(summary: str) -> str:
    """Return what was said after the skill's name, such as 'sage Brainstorm'."""
    return _INVOCATION.sub("", summary, count=1).strip()


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


@dataclass
class _FallbackRequest:
    """A sentence Alexa could not place, waiting for its Alexa history entry."""

    echo_name: str | None
    answer: str
    future: asyncio.Future[tuple[str, str]]
    created: float = field(default_factory=time.monotonic)


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
        self._devices: dict[str, dict[str, Any]] = {}
        self.last_unknown_device: dict[str, str | None] | None = None
        self._active = False
        self._unsub_events: Any = None
        self._recent_events: deque[tuple[float, str, str]] = deque(maxlen=20)
        self._pending: list[_PendingRequest] = []
        self._fallbacks: list[_FallbackRequest] = []
        self._fallback_tasks: set[asyncio.Task[None]] = set()
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
        self.last_unknown_device = data.get("last_unknown_device")
        if not self._webhook_id:
            await self._async_new_webhook_id()

    async def _async_save(self) -> None:
        """Persist the secret, skill link and known Echos."""
        await self._store.async_save(
            {
                "webhook_id": self._webhook_id,
                "application_id": self._application_id,
                "devices": self._devices,
                "last_unknown_device": self.last_unknown_device,
            }
        )

    async def _async_new_webhook_id(self) -> None:
        """Create a new secret, which invalidates the old skill code."""
        self._webhook_id = f"brainstorm_{secrets.token_hex(24)}"
        self._application_id = None
        self._devices = {}
        self.last_unknown_device = None
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
        for fallback in self._fallbacks:
            fallback.future.cancel()
        self._fallbacks.clear()
        for task in self._fallback_tasks:
            task.cancel()
        self._fallback_tasks.clear()

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

    def get_interaction_model(self, language: str | None = None) -> str:
        """Return the voice model for the Alexa developer console."""
        pack = get_pack(language or self.hass.config.language)
        return json.dumps(pack.skill_model, indent=2, ensure_ascii=False)

    def known_device_names(self) -> set[str]:
        """Return the names of all devices the skill has seen."""
        return {str(device["name"]) for device in self._devices.values()}

    async def async_name_last_unknown_device(self, name: str) -> None:
        """Name the sender Home Assistant could not identify, like the Alexa app."""
        unknown = self.last_unknown_device
        if unknown is None or not unknown.get("device_id"):
            return
        self._devices[str(unknown["device_id"])] = {
            "name": name,
            "entity_id": None,
            "custom": True,
        }
        idea_id = unknown.get("idea_id")
        self.last_unknown_device = None
        await self._async_save()
        if idea_id:
            await self._ideas.async_update_idea(str(idea_id), device=name)

    def _echo_from_name(self, name: str) -> EchoDevice:
        """Find the media player of an Echo by its Alexa name."""
        return EchoDevice(name, find_echo_entity(self.hass, name))

    @callback
    def _async_learn_device(self, device_id: str, echo: EchoDevice) -> None:
        """Remember which Echo the skill's device id stands for."""
        known = {"name": echo.name, "entity_id": echo.entity_id}
        current = self._devices.get(device_id)
        # A name chosen by the user wins over what Alexa reports
        if current is not None and current.get("custom"):
            return
        if current != known:
            self._devices[device_id] = known
            self.hass.async_create_task(self._async_save())

    @callback
    def _async_handle_last_called(self, event: Event) -> None:
        """Match an Alexa history entry to a skill request."""
        name = event.data.get("name")
        summary = str(event.data.get("summary") or "")
        response = str(event.data.get("response") or "")
        if not name:
            return
        mentions_skill = "brainstorm" in _normalize(summary)

        now = time.monotonic()
        self._pending = [
            pending
            for pending in self._pending
            if now - pending.created < ALEXA_EVENT_MAX_AGE_SECONDS
        ]
        pending = (
            next((p for p in self._pending if _is_same_sentence(p.text, summary)), None)
            if mentions_skill
            else None
        )
        if pending is None:
            answered = self._async_answer_fallback(
                str(name), summary, response, mentions_skill
            )
            if mentions_skill and not answered:
                self._recent_events.append((now, name, summary))
            return

        self._pending.remove(pending)
        echo = self._echo_from_name(name)
        self._async_learn_device(pending.device_id, echo)
        unknown = self.last_unknown_device
        if unknown is not None and unknown.get("device_id") == pending.device_id:
            self.last_unknown_device = None
        if not pending.future.done():
            pending.future.set_result(echo)
        # The idea was stored before Alexa reported the Echo, or with an outdated one
        if pending.idea_id and (
            pending.used_device is None or pending.used_device.name != echo.name
        ):
            self.hass.async_create_task(
                self._ideas.async_update_idea(pending.idea_id, device=echo.name)
            )
            if self._ideas.privacy_enabled:
                self.hass.async_create_task(
                    self._ideas.async_mark_fields(
                        pending.idea_id,
                        {ATTR_OWNER: self._ideas.voice_user_for(echo.name)},
                    )
                )

    @callback
    def _async_answer_fallback(
        self, name: str, summary: str, response: str, mentions_skill: bool
    ) -> bool:
        """Hand a history entry to a sentence Alexa could not place."""
        now = time.monotonic()
        self._fallbacks = [
            fallback
            for fallback in self._fallbacks
            if not fallback.future.done()
            and now - fallback.created < FALLBACK_LATE_SECONDS
        ]
        for fallback in self._fallbacks:
            if response:
                # The entry carries Alexa's answer, so it must be the answer
                # given to this sentence, from the same Echo if that is known
                matches = _normalize(response) == _normalize(fallback.answer) and (
                    fallback.echo_name in (None, name)
                )
            else:
                # Older Alexa Media leaves the answer out. Within an open session
                # the sentence does not name the skill again, so only an entry
                # from the same Echo can belong to it
                matches = fallback.echo_name == name or (
                    fallback.echo_name is None and mentions_skill
                )
            if matches:
                self._fallbacks.remove(fallback)
                fallback.future.set_result((name, summary))
                return True
        return False

    async def _async_fallback(
        self, device_id: str | None, echo: EchoDevice | None, pack: LanguagePack
    ) -> web.Response:
        """Store a sentence Alexa could not place, using the Alexa history."""
        known = self._devices.get(device_id or "")
        # The Alexa app and other named senders leave no history to read
        if known is not None and known.get("custom"):
            return self._speech(pack.msg("skill_fallback"), end_session=False)

        # Waiting would only keep the person waiting: Alexa adds the sentence to
        # its history together with this answer
        answer = pack.msg("skill_fallback_later")
        request = _FallbackRequest(
            echo.name if echo else None, answer, self.hass.loop.create_future()
        )
        self._fallbacks.append(request)
        task = self.hass.async_create_background_task(
            self._async_store_fallback(request, pack),
            "brainstorm_skill_late_sentence",
        )
        self._fallback_tasks.add(task)
        task.add_done_callback(self._fallback_tasks.discard)
        return self._speech(answer)

    async def _async_store_fallback(
        self, request: _FallbackRequest, pack: LanguagePack
    ) -> None:
        """Store a sentence once its Alexa history entry arrives."""
        try:
            name, summary = await asyncio.wait_for(
                request.future, FALLBACK_LATE_SECONDS
            )
        except TimeoutError:
            _LOGGER.warning(
                "Alexa reported no sentence for a skill request it could not place, "
                "so nothing was stored"
            )
            persistent_notification.async_create(
                self.hass,
                pack.msg("skill_fallback_lost"),
                title="Brainstorm Hub",
                notification_id=FALLBACK_NOTIFICATION_ID,
            )
            return
        await self._async_capture(
            sentence_after_invocation(summary), self._echo_from_name(name), None, pack
        )

    async def _async_resolve_echo(
        self, device_id: str | None, text: str
    ) -> tuple[EchoDevice | None, _PendingRequest | None]:
        """Return the Echo of a request, waiting for it only if it is still unknown."""
        if not device_id:
            return None, None

        # A name chosen by the user needs no confirmation from the Alexa history
        known = self._devices.get(device_id)
        if known is not None and known.get("custom"):
            return EchoDevice(str(known["name"])), None

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
            self.last_unknown_device = {
                "device_id": device_id,
                "time": dt_util.now().strftime("%d.%m.%Y %H:%M:%S"),
                "idea_id": None,
            }
            await self._async_save()
            return None, pending
        return echo, None

    def _known_echo(self, device_id: str | None) -> EchoDevice | None:
        """Return an Echo already known, as touching one leaves no Alexa history."""
        known = self._devices.get(device_id or "")
        if known is None:
            return None
        if known.get("custom"):
            return EchoDevice(str(known["name"]))
        return self._echo_from_name(str(known["name"]))

    def _speech(
        self,
        text: str,
        end_session: bool = True,
        directives: list[dict[str, Any]] | None = None,
    ) -> web.Response:
        """Return text for Alexa to speak, and what a screen should show with it."""
        data: dict[str, Any] = {"speech": text, "end_session": end_session}
        if directives:
            data["directives"] = directives
        return web.json_response(data)

    def _display(
        self,
        wanted: bool,
        user_id: str | None,
        pack: LanguagePack,
        category: str | None = None,
    ) -> list[dict[str, Any]] | None:
        """Return the lists for an Echo with a screen."""
        if not wanted:
            return None
        return [
            build_directive(
                self._ideas.get_ideas_by_category(user_id=user_id),
                self._ideas.categories,
                self._ideas.category_colors,
                category,
                pack,
            )
        ]

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
        pack: LanguagePack,
        request: ReminderRequest | None = None,
        no_time_found: bool = False,
    ) -> web.Response:
        """Store an idea and report where it went."""
        cleaned = clean_voice_text(text, pack)[:MAX_TEXT_LENGTH]
        if len(cleaned) < MIN_IDEA_LENGTH:
            return self._speech(pack.msg("skill_no_text"))
        try:
            idea = await self._ideas.async_add_idea(
                text=cleaned,
                source="alexa_skill",
                device=echo.name if echo else None,
                due=request.due if request else None,
                assignee=request.assignee if request else None,
                trigger=request.trigger if request else None,
                owner=self._ideas.voice_user_for(echo.name if echo else None),
                language=pack.code,
            )
        except HomeAssistantError as err:
            _LOGGER.warning("Could not store idea from Alexa skill: %s", err)
            return self._speech(pack.msg("skill_save_failed"))

        if pending is not None:
            pending.idea_id = idea.get("id")
            if (
                echo is None
                and self.last_unknown_device is not None
                and self.last_unknown_device["device_id"] == pending.device_id
            ):
                self.last_unknown_device["idea_id"] = idea.get("id")
                await self._async_save()
        self.last_request = {
            "time": dt_util.now().strftime("%d.%m.%Y %H:%M:%S"),
            "text": idea.get("text", ""),
            "device": echo.name if echo else "?",
        }
        if request is not None:
            return self._reminder_answer(request, idea, pack)
        if no_time_found:
            return self._speech(pack.msg("skill_saved_no_time"))
        # A date found in the sentence leads to a reminder, so it has to be said
        due = dt_util.parse_datetime(idea.get(ATTR_DUE) or "")
        when = (
            pack.msg("skill_due", when=format_due(due, dt_util.now(), pack.code))
            if due
            else ""
        )
        category = idea.get(ATTR_CATEGORY)
        if category and category != "Inbox":
            return self._speech(
                pack.msg(
                    "skill_saved_in",
                    category=pack.spoken_category(category),
                    when=when,
                )
            )
        return self._speech(pack.msg("skill_saved", when=when))

    def _reminder_answer(
        self, request: ReminderRequest, idea: dict[str, Any], pack: LanguagePack
    ) -> web.Response:
        """Confirm a reminder, and pass on what a real Alexa reminder would need."""
        now = dt_util.now()
        when = (
            format_due(request.due, now, pack.code)
            if request.due
            else self._place_name(request, pack)
        )
        who = self._person_name(request.assignee) or pack.msg("skill_you")
        text = idea.get(ATTR_TEXT)
        speech = pack.msg("skill_remind", who=who, when=when, text=text)
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

    def _place_name(self, request: ReminderRequest, pack: LanguagePack) -> str:
        """Say where a reminder is meant for."""
        zone = (request.trigger or {}).get("zone")
        if zone == ZONE_HOME:
            return pack.msg("skill_at_home")
        state = self.hass.states.get(zone) if zone else None
        return pack.msg("skill_at", name=state.name) if state else pack.msg("skill_here")

    async def _async_remind(
        self,
        text: str,
        echo: EchoDevice | None,
        pending: _PendingRequest | None,
        pack: LanguagePack,
    ) -> web.Response:
        """Store an idea with the spoken time or place as its reminder."""
        options = self._ideas.options
        if not options.get(CONF_REMINDERS_ENABLED, True):
            response = await self._async_capture(text, echo, pending, pack)
            if response.status != 200:
                return response
            return self._speech(pack.msg("skill_reminders_off"))
        now = dt_util.now()
        request = build_reminder_request(
            self.hass, options, clean_voice_text(text, pack), now, pack.code
        )
        if request.due is None and request.trigger is None:
            return await self._async_capture(
                text, echo, pending, pack, no_time_found=True
            )
        if request.due is not None and request.due <= now:
            return self._speech(pack.msg("skill_in_past"))
        return await self._async_capture(
            request.text, echo, pending, pack, request=request
        )

    async def _async_done(
        self, text: str, user_id: str | None, pack: LanguagePack
    ) -> web.Response:
        """Complete the idea a person named, or the last one reminded of."""
        cleaned = text.strip()
        idea = (
            self._ideas.find_open_idea(cleaned, user_id)
            if cleaned
            else self._ideas.last_reminded_idea(user_id)
        )
        if idea is None or not self._ideas.can_edit(idea, user_id):
            return self._speech(pack.msg("skill_not_found"))
        await self._ideas.async_update_idea(idea[ATTR_ID], status="completed")
        return self._speech(pack.msg("skill_done", text=idea.get(ATTR_TEXT)))

    async def _async_display_done(
        self, idea_id: str, user_id: str | None, pack: LanguagePack
    ) -> web.Response:
        """Complete the idea touched on the screen and show the lists again."""
        idea = self._ideas.get_idea(idea_id)
        if idea is None or not self._ideas.can_edit(idea, user_id):
            return self._speech(
                pack.msg("skill_not_found"),
                directives=self._display(True, user_id, pack),
            )
        # A second touch can arrive before the screen has changed
        if idea.get(ATTR_STATUS) == "active":
            await self._ideas.async_update_idea(idea_id, status="completed")
        return self._speech(
            pack.msg("skill_done", text=idea.get(ATTR_TEXT)),
            directives=self._display(True, user_id, pack, idea.get(ATTR_CATEGORY)),
        )

    def _read(
        self,
        category: str | None,
        wants_display: bool,
        user_id: str | None,
        pack: LanguagePack,
    ) -> web.Response:
        """Read a category aloud, or offer the categories as reading all is too long."""
        if category is None:
            return self._speech(
                self._ideas.get_overview_text(user_id, pack.code),
                end_session=False,
                directives=self._display(wants_display, user_id, pack),
            )
        speech = self._ideas.get_announcement_text(category, user_id, pack.code)
        return self._speech(
            speech[:MAX_SPEECH_LENGTH],
            directives=self._display(wants_display, user_id, pack, category),
        )

    def _show(
        self,
        category: str | None,
        wants_display: bool,
        user_id: str | None,
        pack: LanguagePack,
    ) -> web.Response:
        """Show the lists, and read them aloud if there is no screen or nothing to show."""
        if not wants_display or not self._ideas.get_ideas_by_category(
            category, user_id=user_id
        ):
            return self._read(category, wants_display, user_id, pack)
        return self._speech(
            pack.msg("skill_here_is", category=pack.spoken_category(category))
            if category
            else pack.msg("skill_here_are"),
            directives=self._display(True, user_id, pack, category),
        )

    async def _async_snooze(
        self, user_id: str | None, pack: LanguagePack
    ) -> web.Response:
        """Move the last reminder one hour ahead."""
        idea = self._ideas.last_reminded_idea(user_id)
        if idea is None:
            return self._speech(pack.msg("skill_no_reminder"))
        due = dt_util.now() + SNOOZE_TIME
        await self._ideas.async_set_due(idea[ATTR_ID], due)
        when = format_due(due, dt_util.now(), pack.code)
        return self._speech(pack.msg("skill_snoozed", when=when))

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
        # Older skill code does not send this and keeps answering by voice only
        wants_display = payload.get("display") is True
        # Older skill code does not send this and keeps the language of Home Assistant
        locale = payload.get("locale")
        pack = get_pack(
            locale if isinstance(locale, str) and locale else self.hass.config.language
        )
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

        if action in (ACTION_DISPLAY_DONE, ACTION_FALLBACK):
            # Neither has a sentence to match against the Alexa history
            echo, pending = self._known_echo(device_id), None
        else:
            echo, pending = await self._async_resolve_echo(device_id, text)

        # An unknown Echo is let through, so that an idea never gets lost
        allowed = self._ideas.allowed_echos
        if allowed and echo and echo.entity_id and echo.entity_id not in allowed:
            if pending is not None:
                pending.future.cancel()
                self._pending.remove(pending)
            return web.json_response({"silent": True})

        voice_user = self._ideas.voice_user_for(echo.name if echo else None)

        if action == ACTION_LAUNCH:
            return self._speech(
                pack.msg("skill_launch"),
                end_session=False,
                directives=self._display(wants_display, voice_user, pack),
            )
        if action == ACTION_SHOW:
            return self._show(
                self._category_from_speech(text), wants_display, voice_user, pack
            )
        if action == ACTION_DISPLAY_DONE:
            return await self._async_display_done(text, voice_user, pack)
        if action == ACTION_FALLBACK:
            return await self._async_fallback(device_id, echo, pack)
        if action == ACTION_READ_ALL:
            speech = self._ideas.get_announcement_text(
                user_id=voice_user, language=pack.code
            )
            return self._speech(
                speech[:MAX_SPEECH_LENGTH],
                directives=self._display(wants_display, voice_user, pack),
            )
        if action == ACTION_READ:
            return self._read(
                self._category_from_speech(text), wants_display, voice_user, pack
            )
        if action == ACTION_REMIND:
            return await self._async_remind(text, echo, pending, pack)
        if action == ACTION_DONE:
            return await self._async_done(text, voice_user, pack)
        if action == ACTION_SNOOZE:
            return await self._async_snooze(voice_user, pack)
        return await self._async_capture(text, echo, pending, pack)
