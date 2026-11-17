"""Turn WhatsApp messages into notes.

A WhatsApp bridge, such as the integration ha-whatsapp, fires an event for
every message it receives. Brainstorm listens to that event, keeps only the
messages of the numbers it knows and adds every line of such a message as a
note of the person the number belongs to. A reply through the bridge confirms
what was noted.

The event and its fields can be set, so other bridges work as well: the text
and the sender are looked for in the usual fields when none are given.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.core import CALLBACK_TYPE, Context, Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_WHATSAPP_CATEGORY,
    CONF_WHATSAPP_ENABLED,
    CONF_WHATSAPP_EVENT,
    CONF_WHATSAPP_PREFIX,
    CONF_WHATSAPP_REPLY,
    CONF_WHATSAPP_REPLY_SERVICE,
    CONF_WHATSAPP_SENDER_FIELD,
    CONF_WHATSAPP_SENDERS,
    CONF_WHATSAPP_TEXT_FIELD,
    DEFAULT_WHATSAPP_EVENT,
    DEFAULT_WHATSAPP_REPLY_SERVICE,
    SOURCE_WHATSAPP,
)
from .languages import get_pack

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

# Where the bridges put the text and the sender, the first one found is used
TEXT_FIELDS = (
    "content",
    "body",
    "text",
    "message",
    "message.text",
    "message.body",
    "data.body",
    "data.text",
)
SENDER_FIELDS = (
    "from",
    "sender",
    "phone",
    "number",
    "chat_id",
    "chatId",
    "jid",
    "message.from",
    "data.from",
)
# Set by the bridges for a message sent from the own number, such as a reply
OWN_FIELDS = ("fromMe", "from_me", "is_from_me", "self")
# A number needs this many digits to be compared by its end
MIN_DIGITS = 6
# Lines of one message become notes of their own, but not too many
MAX_NOTES = 20
_SENDER_LINE = re.compile(r"^\s*(?P<number>[^=:]+?)\s*[=:]\s*(?P<person>\S.*?)\s*$")


def normalize_number(value: Any) -> str:
    """Return the digits of a phone number, without "@c.us", "+" or "00"."""
    raw = str(value or "").split("@", 1)[0]
    digits = re.sub(r"\D", "", raw)
    return digits.removeprefix("00")


def same_number(first: str, second: str) -> bool:
    """Tell whether two numbers are the same, one perhaps without country code.

    "01711234567" and "491711234567" match, as the national form only lacks
    the country code in front of the leading zero.
    """
    if not first or not second:
        return False
    if first == second:
        return True
    short, long_ = sorted((first.lstrip("0"), second.lstrip("0")), key=len)
    return len(short) >= MIN_DIGITS and long_.endswith(short)


def field_value(data: Any, path: str) -> Any:
    """Return a field of event data, a dot leading into a nested one."""
    value = data
    for part in path.split("."):
        if not isinstance(value, Mapping) or part not in value:
            return None
        value = value[part]
    return value


def first_text(data: Mapping[str, Any], field: str, fallbacks: tuple[str, ...]) -> str:
    """Return the text of the chosen field, or of the first usual field."""
    for path in (field,) if field else fallbacks:
        value = field_value(data, path)
        if isinstance(value, (str, int)) and str(value).strip():
            return str(value).strip()
    return ""


def parse_senders(text: str) -> tuple[dict[str, str], list[str]]:
    """Read lines like "+49 171 1234567 = person.jan".

    Return the numbers with their person and the lines that could not be read.
    """
    senders: dict[str, str] = {}
    bad: list[str] = []
    for line in (text or "").splitlines():
        if not line.strip():
            continue
        match = _SENDER_LINE.match(line)
        number = normalize_number(match.group("number")) if match else ""
        if not match or len(number) < MIN_DIGITS:
            bad.append(line.strip())
            continue
        senders[number] = match.group("person")
    return senders, bad


def format_senders(senders: Mapping[str, str]) -> str:
    """Write the numbers back as lines for the settings."""
    return "\n".join(f"+{number} = {person}" for number, person in senders.items())


def resolve_person(hass: HomeAssistant, person: str) -> str | None:
    """Return the person entity of "person.jan", "jan" or "Jan Example"."""
    wanted = person.strip()
    if hass.states.get(wanted) is not None and wanted.startswith("person."):
        return wanted
    folded = wanted.casefold()
    for state in hass.states.async_all("person"):
        if folded in (state.object_id.casefold(), str(state.name).casefold()):
            return state.entity_id
    return None


class WhatsAppWatcher:
    """Add the WhatsApp messages of known numbers as notes."""

    def __init__(
        self, hass: HomeAssistant, store: BrainstormStore, options: dict[str, Any]
    ) -> None:
        """Remember the settings."""
        self.hass = hass
        self.store = store
        self.enabled = bool(options.get(CONF_WHATSAPP_ENABLED))
        self.event = (
            str(options.get(CONF_WHATSAPP_EVENT) or "").strip()
            or DEFAULT_WHATSAPP_EVENT
        )
        self.text_field = str(options.get(CONF_WHATSAPP_TEXT_FIELD) or "").strip()
        self.sender_field = str(options.get(CONF_WHATSAPP_SENDER_FIELD) or "").strip()
        self.senders: dict[str, str] = {
            normalize_number(number): str(person)
            for number, person in (options.get(CONF_WHATSAPP_SENDERS) or {}).items()
            if normalize_number(number)
        }
        self.category = str(options.get(CONF_WHATSAPP_CATEGORY) or "").strip() or None
        self.prefix = str(options.get(CONF_WHATSAPP_PREFIX) or "").strip()
        self.reply = bool(options.get(CONF_WHATSAPP_REPLY, True))
        self.reply_service = (
            str(options.get(CONF_WHATSAPP_REPLY_SERVICE) or "").strip()
            or DEFAULT_WHATSAPP_REPLY_SERVICE
        )
        self._unsub: CALLBACK_TYPE | None = None

    async def async_start(self) -> None:
        """Listen to the messages of the bridge."""
        if self.enabled and self.senders:
            self._unsub = self.hass.bus.async_listen(self.event, self._handle_event)

    @callback
    def async_stop(self) -> None:
        """Stop listening."""
        if self._unsub is not None:
            self._unsub()
            self._unsub = None

    @callback
    def _handle_event(self, event: Event) -> None:
        """Hand a message over, as the event bus does not wait."""
        self.hass.async_create_task(
            self.async_handle_message(dict(event.data)), eager_start=True
        )

    def person_of(self, sender: str) -> str | None:
        """Return the person a sender belongs to, None for an unknown number."""
        number = normalize_number(sender)
        for known, person in self.senders.items():
            if same_number(number, known):
                return person
        return None

    def note_texts(self, text: str) -> list[str]:
        """Return the notes of a message, one per line, without the keyword."""
        if self.prefix:
            if not text.casefold().startswith(self.prefix.casefold()):
                return []
            text = text[len(self.prefix) :].lstrip(" :,-")
        lines = [line.strip(" \t-•*") for line in text.splitlines()]
        return [line for line in lines if line][:MAX_NOTES]

    async def async_handle_message(self, data: Mapping[str, Any]) -> list[str]:
        """Add the notes of one message, returning their texts."""
        if any(data.get(field) is True for field in OWN_FIELDS):
            return []
        sender = first_text(data, self.sender_field, SENDER_FIELDS)
        person = self.person_of(sender)
        if person is None:
            _LOGGER.debug("WhatsApp message from an unknown number left out")
            return []
        texts = self.note_texts(first_text(data, self.text_field, TEXT_FIELDS))
        if not texts:
            return []
        person_entity = resolve_person(self.hass, person)
        user_id = None
        if person_entity and (state := self.hass.states.get(person_entity)):
            user_id = state.attributes.get("user_id")
        context = Context(user_id=user_id)
        added: list[dict[str, Any]] = []
        for text in texts:
            try:
                added.append(
                    await self.store.async_add_idea(
                        text,
                        category=self.category,
                        source=SOURCE_WHATSAPP,
                        device=self._person_name(person_entity, person),
                        context=context,
                        spoken=False,
                    )
                )
            except HomeAssistantError as err:
                _LOGGER.warning("WhatsApp note %r not added: %s", text, err)
        if added and self.reply:
            await self._async_reply(sender, added)
        return [str(idea.get("text") or "") for idea in added]

    def _person_name(self, person_entity: str | None, person: str) -> str:
        """Return the name shown as where a note came from."""
        state = self.hass.states.get(person_entity) if person_entity else None
        return str(state.name) if state is not None else person

    async def _async_reply(self, sender: str, added: list[dict[str, Any]]) -> None:
        """Confirm through the bridge what was noted."""
        pack = get_pack(self.hass.config.language)
        lines = [
            pack.msg(
                "whatsapp_saved",
                text=str(idea.get("text") or ""),
                category=str(idea.get("category") or ""),
            )
            for idea in added
        ]
        domain, _, service = self.reply_service.partition(".")
        if not service or not self.hass.services.has_service(domain, service):
            _LOGGER.warning(
                "WhatsApp reply left out, the action %s does not exist",
                self.reply_service,
            )
            return
        try:
            await self.hass.services.async_call(
                domain,
                service,
                {"target": sender, "message": "\n".join(lines)},
                blocking=True,
            )
        except (HomeAssistantError, ValueError, vol.Invalid) as err:
            _LOGGER.warning(
                "WhatsApp reply through %s failed: %s", self.reply_service, err
            )
